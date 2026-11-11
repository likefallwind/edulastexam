#!/usr/bin/env python3
"""Build an auditable inventory of existing educational benchmark artifacts.

The inventory is intentionally descriptive. It does not score new responses and
does not promote historical model errors to benchmark conclusions.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT.parent / "edubenchmark"
MATRIX = ROOT / "data/edu_last_exam_evidence_route_matrix_v1/route_matrix.json"

BENCHMARK_SOURCE_DIRS = {
    "asap_2": "asap_2",
    "ceval": "ceval",
    "edubench": "edubench",
    "eduillustrate": "eduillustrate",
    "k12bench": "k12bench",
    "k12vista": "k12vista",
    "interactscience": "interactscience",
    "longtutor_diagnosis": "longtutor",
    "longtutor_evidence": "longtutor",
    "longtutor_teaching": "longtutor",
    "mathtutorbench_mistake_correction": "mathtutorbench",
    "mathtutorbench_mistake_location": "mathtutorbench",
    "mathtutorbench_pedagogy": "mathtutorbench",
    "mathtutorbench_pedagogy_hard": "mathtutorbench",
    "mathtutorbench_problem_solving": "mathtutorbench",
    "mathtutorbench_scaffolding": "mathtutorbench",
    "mathtutorbench_scaffolding_hard": "mathtutorbench",
    "mathtutorbench_socratic": "mathtutorbench",
    "mathtutorbench_solution_correctness": "mathtutorbench",
    "mmtutorbench": "mmtutorbench",
    "mooccube_prereq": "mooccube",
    "p07_selfcheck": "p07_selfcheck",
    "p08_abstention": "p08_abstention",
    "p08_calibration": "p08_calibration",
    "pedagogy_benchmark": "pedagogy_benchmark",
    "safe_child_llm": "safe_child_llm",
    "scivideobench": "scivideobench",
    "student_risk_v2": "student_risk_v2",
    "tutorbench": "tutorbench",
}

HISTORICAL_REPORTS = {
    "frontier_selection": "reports/frontier_selection_v1/selection_report.md",
    "frontier_validation": "reports/frontier_selection_v1/validation_report.md",
    "mini_selection": "reports/mini_selection_v2/selection_report.md",
    "aggregate_index": "reports/eval/_aggregate/index.md",
    "edubench_item_level": "reports/eval/edubench/_analysis/item_level_analysis.json",
    "edubench_judge_swap": "reports/eval/edubench/_judge_swap/agreement.json",
    "student_risk_error_stats": "reports/eval/student_risk_v2/_audit/codex-manual-error-stats.json",
    "student_risk_type_analysis": "reports/eval/student_risk_v2/_audit/codex-manual-type-analysis.md",
    "existing_evidence_matrix": "doc/edu_last_exam_evidence_matrix_2026-11-09.md",
    "frontier_failure_cases": "reports/edubenchassistant/education-llm-frontier-failure-cases-2026-11-06.html",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def jsonl_stats(path: Path) -> dict[str, Any]:
    rows = 0
    item_ids: list[str] = []
    score_status = collections.Counter()
    correct = 0
    score = 0
    judge_models: set[str] = set()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            rows += 1
            if row.get("item_id") is not None:
                item_ids.append(str(row["item_id"]))
            if row.get("score_status") is not None:
                score_status[str(row["score_status"])] += 1
            if isinstance(row.get("correct"), bool):
                correct += 1
            if isinstance(row.get("score"), (int, float)):
                score += 1
            if row.get("judge_model"):
                judge_models.add(str(row["judge_model"]))
    counts = collections.Counter(item_ids)
    return {
        "rows": rows,
        "unique_item_ids": len(counts),
        "duplicate_rows": sum(count - 1 for count in counts.values() if count > 1),
        "score_status": dict(sorted(score_status.items())),
        "boolean_correct_rows": correct,
        "numeric_score_rows": score,
        "judge_models": sorted(judge_models),
    }


def suite_inventory(source: Path, suite: str, benchmark: str) -> dict[str, Any]:
    root = source / "reports/eval_suites" / suite / benchmark
    scored_files = sorted(root.rglob("scored.jsonl")) if root.exists() else []
    stats = [jsonl_stats(path) for path in scored_files]
    return {
        "suite": suite,
        "benchmark": benchmark,
        "path": str(root.relative_to(source)),
        "exists": root.exists(),
        "scored_files": len(scored_files),
        "rows_total": sum(item["rows"] for item in stats),
        "unique_item_ids_sum": sum(item["unique_item_ids"] for item in stats),
        "duplicate_rows_sum": sum(item["duplicate_rows"] for item in stats),
        "boolean_correct_rows": sum(item["boolean_correct_rows"] for item in stats),
        "numeric_score_rows": sum(item["numeric_score_rows"] for item in stats),
        "judge_models": sorted({model for item in stats for model in item["judge_models"]}),
        "scored_file_samples": [str(path.relative_to(source)) for path in scored_files[:8]],
    }


def full_eval_inventory(source: Path, benchmark: str) -> dict[str, Any]:
    root = source / "reports/eval" / benchmark
    scored_files = []
    if root.exists():
        for path in sorted(root.rglob("scored.jsonl")):
            relative = path.relative_to(root)
            if relative.parts and relative.parts[0].startswith("_"):
                continue
            scored_files.append(path)
    stats = [jsonl_stats(path) for path in scored_files]
    return {
        "suite": "full_eval",
        "benchmark": benchmark,
        "path": str(root.relative_to(source)),
        "exists": root.exists(),
        "scored_files": len(scored_files),
        "rows_total": sum(item["rows"] for item in stats),
        "unique_item_ids_sum": sum(item["unique_item_ids"] for item in stats),
        "duplicate_rows_sum": sum(item["duplicate_rows"] for item in stats),
        "boolean_correct_rows": sum(item["boolean_correct_rows"] for item in stats),
        "numeric_score_rows": sum(item["numeric_score_rows"] for item in stats),
        "judge_models": sorted({model for item in stats for model in item["judge_models"]}),
        "scored_file_samples": [str(path.relative_to(source)) for path in scored_files[:8]],
    }


def raw_inventory(source: Path, benchmark: str) -> dict[str, Any]:
    dirname = BENCHMARK_SOURCE_DIRS.get(benchmark, benchmark)
    root = source / "sources/datasets" / dirname
    files = []
    jsonl_rows = 0
    jsonl_unique_ids: set[str] = set()
    for path in sorted(root.rglob("*")) if root.exists() else []:
        if not path.is_file() or path.suffix.lower() not in {".jsonl", ".json", ".csv", ".tsv"}:
            continue
        files.append(path)
        if path.suffix.lower() == ".jsonl":
            with path.open(encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(row, dict):
                        jsonl_rows += 1
                        if row.get("item_id") is not None:
                            jsonl_unique_ids.add(str(row["item_id"]))
    return {
        "source_dir": str(root.relative_to(source)),
        "exists": root.exists(),
        "file_count": len(files),
        "structured_file_samples": [str(path.relative_to(source)) for path in files[:12]],
        "jsonl_rows": jsonl_rows,
        "jsonl_unique_item_ids": len(jsonl_unique_ids),
    }


def parse_selection_report(path: Path) -> list[dict[str, Any]]:
    """Extract the stable per-benchmark table from an existing markdown report."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) != 7:
            continue
        try:
            rows.append({
                "benchmark": cells[0],
                "items": int(cells[1]),
                "unanimous_failure": int(cells[2]),
                "mixed_outcome": int(cells[3]),
                "unanimous_pass": int(cells[4]),
                "mean_error_rate": float(cells[5]),
                "mean_pairwise_disagreement": float(cells[6]),
            })
        except ValueError:
            continue
    return rows


def parse_mini_coverage_report(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            continue
        try:
            rows.append({
                "benchmark": cells[0],
                "profile": cells[1],
                "role": cells[2],
                "selected_items": int(cells[3]),
                "full_items": int(cells[4]),
                "selection_ratio": float(cells[5].strip("%")) if cells[5].endswith("%") else float(cells[5]),
            })
        except ValueError:
            continue
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports/edu_last_exam_evidence_inventory_v1")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source_root.expanduser().resolve()
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    for row in matrix["directions"]:
        card_path = ROOT / "data/edu_last_exam_source_fidelity_v1/directions" / f"{row['direction_id']}.json"
        if not card_path.exists():
            row["source_fidelity_card"] = None
            continue
        card = json.loads(card_path.read_text(encoding="utf-8"))
        original = card.get("original_task", {})
        decision = card.get("decision", {})
        row["source_fidelity_card"] = str(card_path.relative_to(ROOT))
        row["task_ids"] = card.get("task_ids", [])
        row["source_fidelity_status"] = card.get("status")
        row["source_decision_route"] = decision.get("route")
        row["original_task_available"] = original.get("available")
        row["scoring_contract_summary"] = original.get("scoring_contract")
        row["condition_mapping_count"] = len(card.get("condition_mapping", []))
    benchmarks = sorted({benchmark for row in matrix["directions"] for benchmark in row["benchmarks"]})
    suites = [suite_inventory(source, suite, benchmark) for suite in ("mini_v2", "frontier_v1") for benchmark in benchmarks]
    full = [full_eval_inventory(source, benchmark) for benchmark in benchmarks]
    raw = [raw_inventory(source, benchmark) for benchmark in benchmarks]
    historical = {
        key: {
            "path": path,
            "exists": (source / path).exists(),
            "sha256": sha256(source / path) if (source / path).is_file() else None,
        }
        for key, path in HISTORICAL_REPORTS.items()
    }
    historical_selection = {
        "frontier_v1": parse_selection_report(source / HISTORICAL_REPORTS["frontier_selection"]),
        "mini_v2": parse_mini_coverage_report(source / HISTORICAL_REPORTS["mini_selection"]),
    }
    output = {
        "schema_version": "edu_last_exam_evidence_inventory_v1",
        "status": "descriptive_inventory",
        "source_checkout": "../edubenchmark" if source == DEFAULT_SOURCE.resolve() else str(args.source_root),
        "direction_count": len(matrix["directions"]),
        "benchmark_count": len(benchmarks),
        "benchmarks": benchmarks,
        "suite_artifacts": suites,
        "full_eval_artifacts": full,
        "raw_sources": raw,
        "historical_error_and_analysis_reports": historical,
        "historical_selection_stats": historical_selection,
        "interpretation": [
            "Existing scored files are inventory evidence; they do not establish item validity or human difficulty.",
            "Frontier and mini selections are different samples; do not average their rates.",
            "Judge-dependent scores require judge-swap or human review before promotion.",
            "K12Bench old full outputs with duplicate identity must not be mined as all-wrong candidates until rerun with the repaired adapter.",
        ],
    }
    if args.check:
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "inventory.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "direction_route_matrix.json").write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    readme = """# Edu Last Exam evidence inventory v1

This report inventories original task directories, selected-suite scored files,
full evaluation outputs, and historical error analyses from the read-only
`../edubenchmark` checkout. It is a routing and audit index. It does not claim
that every scored item is valid, that a model panel error is AI difficulty, or
that a judge score is a human judgment.

Use `direction_route_matrix.json` to decide whether a direction can reuse an
original task, needs benchmark adaptation, needs a mechanism-authored item, or
is blocked by missing environment/evidence. Before a candidate is frozen, audit
identity, input completeness, gold/rubric, scoring mode, controls, and the
required held-out or human/artifact evidence.
"""
    (args.output_root / "README.md").write_text(readme, encoding="utf-8")
    print(json.dumps({"status": output["status"], "direction_count": output["direction_count"], "benchmark_count": output["benchmark_count"], "output_root": str(args.output_root)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
