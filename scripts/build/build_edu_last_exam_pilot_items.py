#!/usr/bin/env python3
"""Validate and export the hand-authored edu_last_exam_pilot_v1 item set."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "data" / "edu_last_exam_pilot_v1"
OUT = ROOT / "private" / "edu_last_exam_pilot_v1"
AUTHORED = OUT / "authored" / "items.jsonl"

EXPECTED_COUNTS = {
    "grading_robustness": 5,
    "teacher_intent": 2,
    "diagnostic_teaching": 3,
    "assessment_design": 2,
}
REQUIRED_KEYS = [
    "item_id",
    "family",
    "task_type",
    "difficulty",
    "interaction",
    "media_type",
    "source_evidence",
    "system_prompt",
    "user_prompt",
    "expected_output_contract",
    "gold",
    "scoring",
    "review_status",
    "author",
]
VALID_MEDIA = {"text"}
VALID_REVIEW = {"pending"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def problems(row: dict[str, Any]) -> list[str]:
    out: list[str] = []
    item_id = str(row.get("item_id", "<missing>"))
    for key in REQUIRED_KEYS:
        if key not in row:
            out.append(f"{item_id}: missing key {key}")
    if row.get("family") not in EXPECTED_COUNTS:
        out.append(f"{item_id}: unknown family {row.get('family')}")
    if row.get("media_type") not in VALID_MEDIA:
        out.append(f"{item_id}: media_type must be text")
    if row.get("review_status") not in VALID_REVIEW:
        out.append(f"{item_id}: review_status must be pending")
    if row.get("author") != "claude-code":
        out.append(f"{item_id}: author must be claude-code")
    if not isinstance(row.get("source_evidence"), list) or not row.get("source_evidence"):
        out.append(f"{item_id}: source_evidence must be a non-empty list")

    scoring = row.get("scoring")
    if not isinstance(scoring, dict):
        out.append(f"{item_id}: scoring must be an object")
        return out
    for key in ("hard_gates", "criteria", "forbidden"):
        if key not in scoring:
            out.append(f"{item_id}: scoring missing {key}")
    if not isinstance(scoring.get("hard_gates"), list) or not scoring.get("hard_gates"):
        out.append(f"{item_id}: hard_gates must be non-empty")
    if not isinstance(scoring.get("forbidden"), list):
        out.append(f"{item_id}: forbidden must be a list")
    criteria = scoring.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        out.append(f"{item_id}: criteria must be non-empty")
    else:
        total = 0
        for criterion in criteria:
            if not isinstance(criterion, dict):
                out.append(f"{item_id}: criterion must be an object")
                continue
            if not criterion.get("name") or not criterion.get("description"):
                out.append(f"{item_id}: criterion missing name or description")
            weight = criterion.get("weight")
            if not isinstance(weight, int) or weight <= 0:
                out.append(f"{item_id}: criterion weight must be a positive integer")
            else:
                total += weight
        if total != 10:
            out.append(f"{item_id}: criteria weights sum to {total}, expected 10")

    expected = row.get("expected_output_contract")
    if not isinstance(expected, dict):
        out.append(f"{item_id}: expected_output_contract must be an object")
    else:
        if not expected.get("format"):
            out.append(f"{item_id}: expected_output_contract missing format")
        if not expected.get("keys") and expected.get("format") in {"json", "json_array"}:
            out.append(f"{item_id}: JSON output contract missing keys")
    if not isinstance(row.get("gold"), dict) or not row.get("gold"):
        out.append(f"{item_id}: gold must be a non-empty object")
    return out


def validate(rows: list[dict[str, Any]]) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    ids: set[str] = set()
    for idx, row in enumerate(rows, 1):
        item_id = str(row.get("item_id", f"row-{idx}"))
        if item_id in ids:
            errors.append(f"{item_id}: duplicate item_id")
        ids.add(item_id)
        errors.extend(problems(row))
    counts = Counter(row.get("family") for row in rows)
    for family, expected in EXPECTED_COUNTS.items():
        actual = counts.get(family, 0)
        if actual != expected:
            errors.append(f"{family}: item count {actual} != {expected}")
    total = len(rows)
    if total != 12:
        errors.append(f"total item count {total} != 12")
    if any(row.get("media_type") != "text" for row in rows):
        errors.append("non-text item found; visual tasks must stay deferred")
    summary = {
        "total": total,
        "by_family": dict(counts),
        "text_only": all(row.get("media_type") == "text" for row in rows),
        "problem_count": len(errors),
        "pass_threshold": 8,
        "hard_gate_policy": "any_hard_gate_failure_scores_zero",
    }
    return errors, summary


def export(rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    rows = sorted(rows, key=lambda row: str(row.get("item_id", "")))
    write_jsonl(OUT / "items.jsonl", rows)
    fields = [
        "item_id",
        "family",
        "task_type",
        "difficulty",
        "interaction",
        "user_prompt",
        "gold",
        "hard_gates",
        "criteria",
        "review_status",
    ]
    with (OUT / "review_sheet.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            scoring = row.get("scoring", {})
            writer.writerow(
                {
                    "item_id": row.get("item_id", ""),
                    "family": row.get("family", ""),
                    "task_type": row.get("task_type", ""),
                    "difficulty": row.get("difficulty", ""),
                    "interaction": row.get("interaction", ""),
                    "user_prompt": row.get("user_prompt", ""),
                    "gold": json.dumps(row.get("gold", {}), ensure_ascii=False),
                    "hard_gates": json.dumps(scoring.get("hard_gates", []), ensure_ascii=False),
                    "criteria": json.dumps(scoring.get("criteria", []), ensure_ascii=False),
                    "review_status": row.get("review_status", ""),
                }
            )
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "draft_pending_review",
        "summary": summary,
        "notes": [
            "自动校验通过不等于题目效度成立。",
            "本版只收文本题；图像与交互任务见 data/edu_last_exam_pilot_v1/deferred_visual_tasks.md。",
            "接入评测前需完成两名教育者逐题审查和裁判校准。",
        ],
    }
    (OUT / "build_report.md").write_text(
        "# edu_last_exam_pilot_v1 build report\n\n"
        + json.dumps(report, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["validate-only", "export"])
    args = parser.parse_args()
    rows = read_jsonl(AUTHORED)
    errors, summary = validate(rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        print(f"\n{len(errors)} validation errors:")
        print("\n".join(errors))
        return 1
    if args.command == "export":
        export(rows, summary)
        print(f"exported {len(rows)} items to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
