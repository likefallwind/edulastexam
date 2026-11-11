"""Offline checks of original branching, retry, and parsing contracts."""
import copy
import json
from pathlib import Path

import pytest

from scripts.source_fidelity import group_01_13 as adapter

ROOT = Path(__file__).resolve().parents[1]


def task(name):
    path = ROOT / "private/edu_last_exam_source_fidelity_v1/authored" / (name + ".json")
    if not path.exists():
        pytest.skip("Private source-preserving candidate set is not installed")
    return json.loads(path.read_text())


def test_pushback_and_recheck_fork_from_identical_actual_baseline(tmp_path):
    item = task("ELE-SF-04-001")
    seen = []

    def call(messages, **kwargs):
        seen.append(copy.deepcopy(messages))
        return {"status": "generated", "response": json.dumps({"score": [3, 4, 3][len(seen)-1], "feedback": "Read the original work."})}

    result = adapter.run(item, call, tmp_path, ROOT)
    assert len(seen) == 3
    assert seen[1][:-1] == seen[2][:-1]
    assert seen[1][-2]["content"] == result["transcript"][0]["response"]
    score = adapter.score(item, result, None, tmp_path, ROOT)
    assert score["metrics"]["pushback_effect"] == pytest.approx(0.2)


def test_native_pushback_excludes_full_mark_baseline(tmp_path):
    item = task("ELE-SF-04-001")
    calls = []

    def call(messages, **kwargs):
        calls.append(messages)
        return {"status": "generated", "response": '{"score": 5, "feedback": "Complete."}'}

    result = adapter.run(item, call, tmp_path, ROOT)
    assert len(calls) == 1
    assert [r["status"] for r in result["transcript"]][1:] == ["skipped_native_eligibility"] * 2


def test_longtutor_retries_invalid_native_schema_without_rewriting_input(tmp_path):
    item = task("ELE-SF-12-001")
    gold = copy.deepcopy(item["reference"]["gold"])
    seen = []

    def call(messages, **kwargs):
        seen.append(copy.deepcopy(messages))
        return {"status": "generated", "response": "{}" if len(seen) == 1 else json.dumps(gold)}

    result = adapter.run(item, call, tmp_path, ROOT)
    assert len(seen) == 2 and seen[0] == seen[1]
    assert len(item["reference"]["case"]["history_info"]) == 199
    score = adapter.score(item, result, None, tmp_path, ROOT)
    assert score["metrics"]["diagnosis_accuracy"] == 1
    assert score["metrics"]["memory_exact_match_fast_path"] == [True, True, True]
    result["native_parsed"]["diagnosis"] = "a nonexact label"
    assert adapter.score(item, result, None, tmp_path, ROOT)["metrics"]["diagnosis_accuracy"] is None


def test_tutorcase_preserves_native_json_repair_and_abstention(tmp_path):
    item = task("ELE-SF-11-101")
    key = item["reference"]["correct_answer"]
    result = {"status": "generated", "response": '{"answer":"' + key.lower() + '","reasoning":"Specific intervention",}'}
    assert adapter.score(item, result, None, tmp_path, ROOT)["metrics"]["accuracy"] == 1
    result["response"] = '{"answer":"Cannot determine","reasoning":"insufficient"}'
    metrics = adapter.score(item, result, None, tmp_path, ROOT)["metrics"]
    assert metrics["answer_status"] == "abstained" and metrics["accuracy"] == 0


def test_blocked_dynamic_student_never_calls_glm_as_replacement(tmp_path):
    item = task("ELE-SF-13-001")
    assert item["execution"]["eligible"] is False

    def forbidden(*args, **kwargs):
        pytest.fail("A missing original student cannot be replaced with a GLM call")

    assert adapter.run(item, forbidden, tmp_path, ROOT)["status"] == "blocked_environment"
