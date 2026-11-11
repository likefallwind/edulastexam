import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_route_matrix_covers_all_37_directions():
    path = ROOT / "data/edu_last_exam_evidence_route_matrix_v1/route_matrix.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["directions"]
    assert len(rows) == 37
    assert {row["direction_id"] for row in rows} == {f"{i:02d}" for i in range(1, 38)}
    assert all(row["source_ids"] and row["benchmarks"] for row in rows)
    assert all(row["oracle_type"] and row["promotion_gate"] for row in rows)
    assert {row["evidence_route"] for row in rows} == {
        "reuse_original", "benchmark_adaptation", "mechanism_authored", "blocked"
    }


def test_generated_inventory_keeps_historical_error_sources_separate():
    path = ROOT / "reports/edu_last_exam_evidence_inventory_v1/inventory.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["direction_count"] == 37
    assert data["benchmark_count"] >= 20
    assert len(data["historical_selection_stats"]["frontier_v1"]) > 0
    assert data["historical_error_and_analysis_reports"]["edubench_judge_swap"]["exists"]
    assert "K12Bench old full outputs" in " ".join(data["interpretation"])
