import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_selection_queue_has_all_directions_and_local_cases():
    path = ROOT / "reports/edu_last_exam_item_selection_v1/selection_queue.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "candidate_review_queue"
    assert len(data["directions"]) == 37
    assert {row["direction_id"] for row in data["directions"]} == {f"{i:02d}" for i in range(1, 38)}
    assert sum(len(row["local_source_cases"]) for row in data["directions"]) == 81
    assert sum(len(row["full_coverage_cases"]) for row in data["directions"]) == 38


def test_selection_queue_keeps_scoring_and_candidate_audit_fields():
    data = json.loads((ROOT / "reports/edu_last_exam_item_selection_v1/selection_queue.json").read_text(encoding="utf-8"))
    direction = next(row for row in data["directions"] if row["direction_id"] == "01")
    assert direction["task_ids"]
    assert direction["benchmark_candidates"]
    candidate = direction["benchmark_candidates"][0]["top_items"][0]
    assert {"item_id", "suite", "outcome", "p_correct", "scoring_mode", "candidate_status"} <= set(candidate)
    blocked = next(row for row in data["directions"] if row["direction_id"] == "30")
    assert blocked["direction_selection_status"].startswith("blocked_")
    assert blocked["full_coverage_cases"][0]["item_id"] == "ELE-FC-30-001"
