#!/usr/bin/env python3
"""Build the next-stage, human-review queue for all 37 directions.

The queue links authored/source-fidelity cases with existing benchmark item
candidates. It intentionally excludes prompts, answers, and model responses.
Every row remains a candidate until the gold, identity, rubric, and controls are
audited.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "data/edu_last_exam_evidence_route_matrix_v1/route_matrix.json"
CARDS = ROOT / "private/edu_last_exam_source_fidelity_v1/items.jsonl"
FULL_COVERAGE = ROOT / "private/edu_last_exam_full_coverage_v1/authored"
CANDIDATES = ROOT / "reports/difficulty_mining_v1/candidates.jsonl"


def source_case_summary(row: dict[str, Any]) -> dict[str, Any]:
    source = row.get("source", {})
    scoring = row.get("scoring", {})
    review = row.get("review", {})
    return {
        "case_id": row.get("case_id"),
        "title": row.get("title"),
        "origin": row.get("origin"),
        "source_id": source.get("case_id"),
        "source_record": source.get("record_path"),
        "source_revision": source.get("revision"),
        "scoring_mode": scoring.get("mode"),
        "scoring_contract": scoring.get("native_metric"),
        "scoring_module": scoring.get("module"),
        "human_review": review.get("human_review"),
        "author_offline_check": review.get("author_offline_check"),
        "selection_status": "needs_independent_review",
    }


def priority(row: dict[str, Any]) -> tuple[int, float, str]:
    outcome_order = {
        "unanimous_failure": 0,
        "mixed_outcome": 1,
        "unanimous_pass": 2,
        "incomplete_panel": 3,
    }
    p = row.get("p_correct")
    return (outcome_order.get(row.get("outcome"), 9), float(p) if p is not None else 1.0, str(row.get("item_id")))


def full_coverage_summary(row: dict[str, Any]) -> dict[str, Any]:
    status = row.get("status", {})
    runtime = row.get("runtime", {})
    return {
        "item_id": row.get("item_id"),
        "title": row.get("title"),
        "material_origin": row.get("material_origin"),
        "measurement_claim": row.get("measurement_claim"),
        "unmeasured_subclaims": row.get("unmeasured_subclaims", []),
        "stage": status.get("stage"),
        "human_review": status.get("human_review"),
        "model_evaluation": status.get("model_evaluation"),
        "frozen": status.get("frozen"),
        "runtime_modes": sorted({prompt.get("interaction_mode") for prompt in row.get("prompts", []) if prompt.get("interaction_mode")}),
        "runtime_contract": runtime.get("mode"),
        "prompt_count": len(row.get("prompts", [])),
        "gold_present": bool(row.get("gold")),
        "rubric_present": bool(row.get("rubric")),
        "control_count": len(row.get("controls", [])),
        "selection_status": "needs_independent_review",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports/edu_last_exam_item_selection_v1")
    args = parser.parse_args()

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    source_cases: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    with CARDS.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            for direction_id in row.get("direction_ids", []):
                source_cases[str(direction_id)].append(source_case_summary(row))

    full_cases: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for path in sorted(FULL_COVERAGE.glob("ELE-FC-*.json")):
        row = json.loads(path.read_text(encoding="utf-8"))
        full_cases[str(row.get("direction_id"))].append(full_coverage_summary(row))

    benchmark_rows: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    with CANDIDATES.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            benchmark_rows[str(row.get("benchmark"))].append(row)

    directions: list[dict[str, Any]] = []
    for direction in matrix["directions"]:
        direction_id = str(direction["direction_id"])
        benchmark_candidates: list[dict[str, Any]] = []
        for benchmark in direction.get("benchmarks", []):
            rows = [row for row in benchmark_rows.get(benchmark, []) if direction_id in row.get("direction_ids", [])]
            usable = [row for row in rows if row.get("outcome") != "incomplete_panel" and row.get("n_scored", 0) >= 2]
            top = sorted(usable, key=priority)[:8]
            benchmark_candidates.append({
                "benchmark": benchmark,
                "record_count": len(rows),
                "usable_binary_candidate_count": len(usable),
                "incomplete_or_nonbinary_count": len(rows) - len(usable),
                "top_items": [
                    {
                        "suite": row["suite"],
                        "item_id": row["item_id"],
                        "outcome": row["outcome"],
                        "n_models": row["n_models"],
                        "n_scored": row["n_scored"],
                        "n_correct": row["n_correct"],
                        "n_wrong": row["n_wrong"],
                        "p_correct": row["p_correct"],
                        "error_rate": row["error_rate"],
                        "scoring_mode": row.get("scoring_mode"),
                        "judge_models": row.get("judge_models", []),
                        "metadata": row.get("metadata", {}),
                        "candidate_status": "needs_item_gold_protocol_audit",
                    }
                    for row in top
                ],
                "selection_note": "historical model error is a review-priority signal only; do not freeze without gold/protocol/construct review",
            })
        blocked = direction["evidence_route"] == "blocked"
        directions.append({
            "direction_id": direction_id,
            "title": direction["title"],
            "source_status": direction["source_status"],
            "evidence_route": direction["evidence_route"],
            "source_ids": direction.get("source_ids", []),
            "source_fidelity_card": f"data/edu_last_exam_source_fidelity_v1/directions/{direction_id}.json",
            "task_ids": sorted(case["case_id"] for case in source_cases.get(direction_id, [])),
            "local_source_cases": source_cases.get(direction_id, []),
            "full_coverage_cases": full_cases.get(direction_id, []),
            "benchmark_candidates": benchmark_candidates,
            "direction_selection_status": "blocked_pending_environment_or_evidence" if blocked else "candidate_review_pending",
            "next_review_gate": direction["promotion_gate"],
        })

    output = {
        "schema_version": "edu_last_exam_item_selection_v1",
        "status": "candidate_review_queue",
        "interpretation": [
            "A source-fidelity case is an authored/source task candidate, not an independently human-reviewed frozen item.",
            "A benchmark item is ranked by historical panel outcome only after identity and scoring validity are checked.",
            "incomplete_panel and numeric/judge-only rows remain visible but are not binary hard-item candidates.",
            "blocked directions are retained in the denominator and cannot be filled by a weak proxy.",
        ],
        "directions": directions,
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "selection_queue.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Edu Last Exam item selection queue v1",
        "",
        "This is a review queue, not a frozen benchmark. It links the 37 direction cards and source-fidelity cases to existing benchmark item candidates. Historical model error ranks review priority; it does not establish item validity or human difficulty.",
        "",
        "Each direction retains its local source-fidelity cases, task IDs, benchmark candidates, scoring mode, judge dependence, and next review gate. Review item identity, input completeness, gold/acceptable answers, critical errors, controls, and construct fit before any model rerun.",
    ]
    (args.output_root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"status": output["status"], "direction_count": len(directions), "output_root": str(args.output_root)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
