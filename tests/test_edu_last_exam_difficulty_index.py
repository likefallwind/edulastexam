import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build/build_edu_last_exam_difficulty_index.py"
SOURCE = ROOT.parent / "edubenchmark"


def test_check_reads_existing_ceval_and_mooccube_runs():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source-root",
            str(SOURCE),
            "--suites",
            "mini_v2",
            "frontier_v1",
            "--benchmarks",
            "ceval",
            "mooccube_prereq",
            "--check",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    assert summary["status"] == "discovery_only"
    assert summary["n_records"] > 0
    by_key = {(row["suite"], row["benchmark"]): row for row in summary["collections"]}
    assert by_key[("mini_v2", "ceval")]["status"] == "ok"
    assert by_key[("mini_v2", "mooccube_prereq")]["status"] == "ok"
    assert by_key[("frontier_v1", "ceval")]["status"] == "ok"
    assert by_key[("frontier_v1", "mooccube_prereq")]["status"] == "ok"


def test_check_can_mine_full_runs_and_cross_suite_candidates():
    completed = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--source-root",
            str(SOURCE),
            "--suites",
            "mini_v2",
            "frontier_v1",
            "--benchmarks",
            "ceval",
            "mooccube_prereq",
            "--full-benchmarks",
            "ceval",
            "mooccube_prereq",
            "--check",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    summary = json.loads(completed.stdout)
    by_key = {(row["suite"], row["benchmark"]): row for row in summary["collections"]}
    assert by_key[("full_eval", "ceval")]["n_items"] == 1346
    assert by_key[("full_eval", "mooccube_prereq")]["n_items"] == 300
    assert summary["cross_suite_candidate_counts"]["both_unanimous_failure"] == 8


def test_candidate_map_has_all_37_directions():
    path = ROOT / "data/edu_last_exam_difficulty_mining_v1/direction_mechanism_map.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = {row["direction_id"] for row in data["directions"]}
    assert ids == {f"{number:02d}" for number in range(1, 38)}
    assert sum(len(group["direction_ids"]) for group in data["groups"]) == 37
    assert all(row["mechanism"] and row["hardness_conditions"] for row in data["directions"])
