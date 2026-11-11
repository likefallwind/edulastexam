#!/usr/bin/env python3
"""Mine item-level historical model errors from an existing edubenchmark checkout.

This is a discovery index, not a benchmark scorer. It deliberately stores no raw
model responses and never modifies the source checkout.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT.parent / "edubenchmark"
MAP_PATH = ROOT / "data/edu_last_exam_difficulty_mining_v1/direction_mechanism_map.json"
ROUTE_MATRIX_PATH = ROOT / "data/edu_last_exam_evidence_route_matrix_v1/route_matrix.json"

ALLOWED_METADATA = {
    "buckets", "task", "field", "variant", "chance", "n_constraints",
    "n_satisfied", "n_concepts", "n_constraints_total", "n_reverse_distractors",
    "order_n5", "order_n6", "source", "subject", "category", "score_status",
    "unparsed",
}


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            if isinstance(value, dict):
                yield value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def item_list_path(source: Path, suite: str, benchmark: str) -> Path:
    if suite == "mini_v2":
        return source / "data/mini_selection_v2" / f"{benchmark}_items_v2.txt"
    if suite == "frontier_v1":
        return source / "data/frontier_selection_v1" / f"{benchmark}_frontier_items_v1.txt"
    raise ValueError(f"unsupported suite: {suite}")


def full_item_source_path(source: Path, benchmark: str) -> Path:
    paths = {
        "ceval": source / "sources/datasets/ceval/data/val.jsonl",
        "mooccube_prereq": source / "sources/datasets/mooccube/items_v1.jsonl",
    }
    try:
        return paths[benchmark]
    except KeyError as exc:
        raise ValueError(f"no full item source configured for {benchmark}") from exc


def load_item_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_jsonl_item_ids(path: Path) -> list[str]:
    ids: list[str] = []
    for row in read_jsonl(path):
        item_id = row.get("item_id")
        if item_id is not None:
            ids.append(str(item_id))
    return ids


def safe_metadata(row: dict[str, Any]) -> dict[str, Any]:
    """Keep structural fields, excluding gold, response, and extraction traces."""
    result: dict[str, Any] = {}
    for key, value in row.items():
        if key not in ALLOWED_METADATA:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            result[key] = value
        elif key == "buckets" and isinstance(value, dict):
            result[key] = {
                str(k): v for k, v in value.items()
                if isinstance(v, (str, int, float, bool)) or v is None
            }
    return result


def direction_lookup(mapping: dict[str, Any], benchmark: str, route_matrix: dict[str, Any] | None = None) -> list[str]:
    hint = mapping.get("benchmark_hints", {}).get(benchmark, {})
    ids = {str(value) for value in hint.get("direction_ids", [])}
    if route_matrix:
        for direction in route_matrix.get("directions", []):
            if benchmark in direction.get("benchmarks", []):
                ids.add(str(direction["direction_id"]))
    return sorted(ids)


def scoring_metadata(observations: list[tuple[str, bool, dict[str, Any]]]) -> dict[str, Any]:
    judge_models = sorted({str(row["judge_model"]) for _, _, row in observations if row.get("judge_model")})
    has_numeric_score = any(isinstance(row.get("score"), (int, float)) for _, _, row in observations)
    return {
        "scoring_mode": "judge_dependent" if judge_models else ("numeric_score" if has_numeric_score else "rule_or_exact"),
        "judge_models": judge_models,
    }


def collect_benchmark(source: Path, suite: str, benchmark: str, mapping: dict[str, Any], route_matrix: dict[str, Any]) -> dict[str, Any]:
    list_path = item_list_path(source, suite, benchmark)
    if not list_path.exists():
        return {"suite": suite, "benchmark": benchmark, "status": "missing_item_list", "records": []}

    item_ids = load_item_ids(list_path)
    selected = set(item_ids)
    eval_dir = source / "reports/eval_suites" / suite / benchmark
    model_rows: dict[str, dict[str, dict[str, Any]]] = {}
    if eval_dir.exists():
        for model_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            scored_path = model_dir / "scored.jsonl"
            if not scored_path.exists():
                continue
            rows: dict[str, dict[str, Any]] = {}
            for row in read_jsonl(scored_path):
                item_id = row.get("item_id")
                if item_id in selected and item_id not in rows:
                    rows[str(item_id)] = row
            if rows:
                model_rows[model_dir.name] = rows

    model_names = sorted(model_rows)
    by_item: dict[str, list[tuple[str, bool, dict[str, Any]]]] = collections.defaultdict(list)
    for model_name in model_names:
        for item_id, row in model_rows[model_name].items():
            if row.get("score_status") != "scored" or not isinstance(row.get("correct"), bool):
                continue
            by_item[item_id].append((model_name, bool(row["correct"]), row))

    records: list[dict[str, Any]] = []
    for item_id in item_ids:
        observations = by_item.get(item_id, [])
        n_scored = len(observations)
        n_correct = sum(correct for _, correct, _ in observations)
        n_wrong = n_scored - n_correct
        if n_scored == 0 or n_scored < len(model_names):
            outcome = "incomplete_panel"
        elif n_wrong == n_scored:
            outcome = "unanimous_failure"
        elif n_correct == n_scored:
            outcome = "unanimous_pass"
        else:
            outcome = "mixed_outcome"
        metadata = safe_metadata(observations[0][2]) if observations else {}
        score_meta = scoring_metadata(observations)
        records.append({
            "suite": suite,
            "benchmark": benchmark,
            "item_id": item_id,
            "direction_ids": direction_lookup(mapping, benchmark, route_matrix),
            "panel_models": model_names,
            "n_models": len(model_names),
            "n_scored": n_scored,
            "n_correct": n_correct,
            "n_wrong": n_wrong,
            "p_correct": (n_correct / n_scored) if n_scored else None,
            "error_rate": (n_wrong / n_scored) if n_scored else None,
            "outcome": outcome,
            "historical_model_error": outcome in {"unanimous_failure", "mixed_outcome"},
            "gold_stability": "not_checked",
            "human_difficulty": "unmeasured",
            "mapping_status": "provisional_benchmark_hint",
            **score_meta,
            "metadata": metadata,
        })

    outcome_counts = collections.Counter(row["outcome"] for row in records)
    return {
        "suite": suite,
        "benchmark": benchmark,
        "status": "ok" if model_names else "missing_scored_runs",
        "item_list": str(list_path.relative_to(source)),
        "item_list_sha256": sha256_file(list_path),
        "n_items": len(item_ids),
        "panel_models": model_names,
        "n_panel_models": len(model_names),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "threshold_counts": {
            "p_correct_le_0.25": sum(row["p_correct"] is not None and row["p_correct"] <= 0.25 for row in records),
            "p_correct_le_0.50": sum(row["p_correct"] is not None and row["p_correct"] <= 0.50 for row in records),
        },
        "records": records,
    }


def collect_full_eval(source: Path, benchmark: str, mapping: dict[str, Any], route_matrix: dict[str, Any]) -> dict[str, Any]:
    """Aggregate the full item-level runs, when the source has canonical JSONL IDs."""
    source_items = full_item_source_path(source, benchmark)
    if not source_items.exists():
        return {"suite": "full_eval", "benchmark": benchmark, "status": "missing_item_source", "records": []}
    item_ids = load_jsonl_item_ids(source_items)
    selected = set(item_ids)
    eval_dir = source / "reports/eval" / benchmark
    model_rows: dict[str, dict[str, dict[str, Any]]] = {}
    if eval_dir.exists():
        for model_dir in sorted(path for path in eval_dir.iterdir() if path.is_dir()):
            scored_path = model_dir / "scored.jsonl"
            if not scored_path.exists():
                continue
            rows: dict[str, dict[str, Any]] = {}
            for row in read_jsonl(scored_path):
                item_id = row.get("item_id")
                if item_id in selected and item_id not in rows:
                    rows[str(item_id)] = row
            if rows:
                model_rows[model_dir.name] = rows

    model_names = sorted(model_rows)
    by_item: dict[str, list[tuple[str, bool, dict[str, Any]]]] = collections.defaultdict(list)
    for model_name in model_names:
        for item_id, row in model_rows[model_name].items():
            if row.get("score_status") != "scored" or not isinstance(row.get("correct"), bool):
                continue
            by_item[item_id].append((model_name, bool(row["correct"]), row))

    records: list[dict[str, Any]] = []
    for item_id in item_ids:
        observations = by_item.get(item_id, [])
        n_scored = len(observations)
        n_correct = sum(correct for _, correct, _ in observations)
        n_wrong = n_scored - n_correct
        if n_scored == 0 or n_scored < len(model_names):
            outcome = "incomplete_panel"
        elif n_wrong == n_scored:
            outcome = "unanimous_failure"
        elif n_correct == n_scored:
            outcome = "unanimous_pass"
        else:
            outcome = "mixed_outcome"
        records.append({
            "suite": "full_eval",
            "benchmark": benchmark,
            "item_id": item_id,
            "direction_ids": direction_lookup(mapping, benchmark, route_matrix),
            "panel_models": model_names,
            "n_models": len(model_names),
            "n_scored": n_scored,
            "n_correct": n_correct,
            "n_wrong": n_wrong,
            "p_correct": (n_correct / n_scored) if n_scored else None,
            "error_rate": (n_wrong / n_scored) if n_scored else None,
            "outcome": outcome,
            "historical_model_error": outcome in {"unanimous_failure", "mixed_outcome"},
            "gold_stability": "not_checked",
            "human_difficulty": "unmeasured",
            "mapping_status": "provisional_benchmark_hint",
            **scoring_metadata(observations),
            "metadata": safe_metadata(observations[0][2]) if observations else {},
        })
    outcome_counts = collections.Counter(row["outcome"] for row in records)
    return {
        "suite": "full_eval",
        "benchmark": benchmark,
        "status": "ok" if model_names else "missing_scored_runs",
        "item_list": str(source_items.relative_to(source)),
        "item_list_sha256": sha256_file(source_items),
        "n_items": len(item_ids),
        "panel_models": model_names,
        "n_panel_models": len(model_names),
        "outcome_counts": dict(sorted(outcome_counts.items())),
        "threshold_counts": {
            "p_correct_le_0.25": sum(row["p_correct"] is not None and row["p_correct"] <= 0.25 for row in records),
            "p_correct_le_0.50": sum(row["p_correct"] is not None and row["p_correct"] <= 0.50 for row in records),
        },
        "records": records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports/difficulty_mining_v1")
    parser.add_argument("--suites", nargs="+", default=["mini_v2", "frontier_v1"])
    parser.add_argument("--benchmarks", nargs="+", default=["ceval", "mooccube_prereq"])
    parser.add_argument("--full-benchmarks", nargs="+", default=[], help="also mine full reports/eval runs for configured benchmarks")
    parser.add_argument("--check", action="store_true", help="read and summarize without writing reports")
    return parser.parse_args()


def cross_suite_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key = {(row["suite"], row["benchmark"], row["item_id"]): row for row in records}
    benchmarks = sorted({row["benchmark"] for row in records})
    result: list[dict[str, Any]] = []
    for benchmark in benchmarks:
        mini_ids = {key[2] for key in by_key if key[:2] == ("mini_v2", benchmark)}
        frontier_ids = {key[2] for key in by_key if key[:2] == ("frontier_v1", benchmark)}
        for item_id in sorted(mini_ids & frontier_ids):
            mini = by_key[("mini_v2", benchmark, item_id)]
            frontier = by_key[("frontier_v1", benchmark, item_id)]
            if mini["outcome"] == "unanimous_failure" and frontier["outcome"] == "unanimous_failure":
                overlap_label = "both_unanimous_failure"
            elif all(row["p_correct"] is not None and row["p_correct"] <= 0.25 for row in (mini, frontier)):
                overlap_label = "both_p_correct_le_0.25"
            elif all(row["p_correct"] is not None and row["p_correct"] <= 0.50 for row in (mini, frontier)):
                overlap_label = "both_p_correct_le_0.50"
            else:
                continue
            result.append({
                "benchmark": benchmark,
                "item_id": item_id,
                "overlap_label": overlap_label,
                "direction_ids": sorted(set(mini["direction_ids"] + frontier["direction_ids"])),
                "mini": {key: mini[key] for key in ("panel_models", "n_scored", "n_correct", "p_correct", "outcome")},
                "frontier": {key: frontier[key] for key in ("panel_models", "n_scored", "n_correct", "p_correct", "outcome")},
                "gold_stability": "not_checked",
                "human_difficulty": "unmeasured",
            })
    return result


def main() -> int:
    args = parse_args()
    source = args.source_root.expanduser().resolve()
    mapping = read_json(MAP_PATH)
    route_matrix = read_json(ROUTE_MATRIX_PATH)
    collections_out: list[dict[str, Any]] = []
    all_records: list[dict[str, Any]] = []
    for suite in args.suites:
        for benchmark in args.benchmarks:
            result = collect_benchmark(source, suite, benchmark, mapping, route_matrix)
            collections_out.append({key: value for key, value in result.items() if key != "records"})
            all_records.extend(result.get("records", []))
    for benchmark in args.full_benchmarks:
        result = collect_full_eval(source, benchmark, mapping, route_matrix)
        collections_out.append({key: value for key, value in result.items() if key != "records"})
        all_records.extend(result.get("records", []))

    summary = {
        "schema_version": "edu_last_exam_difficulty_mining_v1",
        "status": "discovery_only",
        "source_checkout": "../edubenchmark" if source == DEFAULT_SOURCE.resolve() else str(args.source_root),
        "suites": list(args.suites),
        "benchmarks": list(args.benchmarks),
        "full_benchmarks": list(args.full_benchmarks),
        "n_records": len(all_records),
        "cross_suite_candidate_counts": dict(collections.Counter(row["overlap_label"] for row in cross_suite_candidates(all_records))),
        "collections": collections_out,
        "interpretation": [
            "unanimous_failure is historical panel model error, not an official or human difficulty label",
            "mini_v2 and frontier_v1 are different selections and must not be averaged",
            "candidate promotion requires item/gold/protocol review and held-out model or human evidence",
        ],
    }
    if args.check:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.output_root / "candidates.jsonl").open("w", encoding="utf-8") as handle:
        for row in all_records:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with (args.output_root / "cross_suite_candidates.jsonl").open("w", encoding="utf-8") as handle:
        for row in cross_suite_candidates(all_records):
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    readme = """# Difficulty mining v1

This report is generated from existing `edubenchmark` scored JSONL files. It is a
candidate discovery index, not a frozen benchmark result. `unanimous_failure`
means that the historical panel models all missed the item under that suite's
protocol. It does not establish human difficulty, a correct gold answer, or an
education failure. `mini_v2` and `frontier_v1` are separate selections and are
reported separately.

Before promotion, inspect the original item, gold, scoring protocol, data
completeness, contamination risk, and educational consequence. Then re-run on
held-out models and, where the claim requires it, obtain independent human or
teacher evidence.

`cross_suite_candidates.jsonl` contains only items shared by `mini_v2` and
`frontier_v1` that remain low-scoring in both views. It is a review queue, not a
second score.
"""
    (args.output_root / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
