"""V2 pilot content and runtime regressions; no model APIs are called."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil

import pytest

from scripts.full_coverage import core
from scripts.build import build_edu_last_exam_v2_pilot as v2
from scripts.build.build_edu_last_exam_full_coverage import build

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "private/edu_last_exam_v2_pilot"
PROTOCOL = json.loads((ROOT / "data/edu_last_exam_v2_pilot/protocol.json").read_text())
ITEMS = {item["item_id"]: item for item in (json.loads(line) for line in (BATCH / "items.jsonl").read_text().splitlines())}
PROMPTS = {(row["item_id"], row["prompt_id"]): row for row in (json.loads(line) for line in (BATCH / "prompts.jsonl").read_text().splitlines())}
RUNTIMES = json.loads((BATCH / "runtimes.json").read_text())


def recorded_call(responses):
    calls = []
    answers = iter(responses)

    def call(messages, index):
        calls.append(copy.deepcopy(messages))
        return {"status": "generated", "response": next(answers)}

    return call, calls


def episode_task(item_id, prompt_id):
    prompt = PROMPTS[item_id, prompt_id]
    case_id = f"{item_id}__{prompt_id}"
    messages, _, unsupported = core.prepare_messages(BATCH, prompt)
    assert not unsupported
    return {
        "item_id": item_id,
        "prompt_id": prompt_id,
        "case_id": case_id,
        "runtime": RUNTIMES[case_id],
        "messages": messages,
    }


def test_protocol_cards_authored_and_mechanism_blueprints_align():
    evidence_cases, evidence_hashes, items_with_v1_failures = v2.validate_cards(PROTOCOL)
    assert set(ITEMS) == set(PROTOCOL["expected_item_ids"])
    assert len(ITEMS) == 5 and len(PROMPTS) == 11
    assert len(evidence_cases) == 9 and len(set(evidence_cases)) == 8
    assert items_with_v1_failures == 5
    assert all(ITEMS[item_id]["status"]["model_evaluation"] == "not_run" for item_id in ITEMS)
    assert all(ITEMS[item_id]["status"]["frozen"] is False for item_id in ITEMS)
    assert evidence_hashes
    assert {item["direction_id"] for item in ITEMS.values()} == {"01", "09", "12", "14", "33"}


def test_cards_do_not_require_a_historical_v1_failure(tmp_path):
    copied = tmp_path / "batch"
    shutil.copytree(BATCH, copied)
    card_path = copied / "cards.jsonl"
    cards = [json.loads(line) for line in card_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for card in cards:
        card["v1_evidence"] = []
    card_path.write_text("".join(json.dumps(card, ensure_ascii=False) + "\n" for card in cards), encoding="utf-8")
    evidence_cases, _, items_with_v1_failures = v2.validate_cards(PROTOCOL, batch=copied)
    assert evidence_cases == []
    assert items_with_v1_failures == 0


def test_default_full_coverage_loader_still_requires_the_original_38_packages():
    items = core.load_items()
    assert len(items) == 38
    assert {item["direction_id"] for item in items} == {f"{number:02}" for number in range(1, 38)}


def test_public_exports_exclude_gold_rubric_and_future_observations():
    for row in PROMPTS.values():
        assert set(row) == {"item_id", "direction_id", "prompt_id", "system_prompt", "user_prompt", "assets", "interaction_mode"}
        public = row["system_prompt"] + row["user_prompt"]
        assert "critical_errors" not in public and "acceptable_alternatives" not in public
        assert "学生在新表提交(14+18+16)" not in public
        assert "学生独立回答：‘实验只测20°C" not in public
        assert "reference_answer" not in public


def test_v2_math_and_evidence_gold_are_internally_consistent():
    current = json.loads((BATCH / "stimuli/12/history_unknown.json").read_text())["current_task"]
    completed = [row for row in current["rows"] if row["status"] == "completed"]
    current_gold = (16 + 15 + 20) / sum(row["seeds_sown"] for row in completed)
    probe_gold = (14 + 18 + 16) / 60
    assert current_gold == 0.85 and probe_gold == 0.80
    assert "85%" in ITEMS["ELE-V2-12-001"]["gold"]["per_prompt"]["history_unknown"]["reference_answer"]["current"]
    assert "80%" in ITEMS["ELE-V2-12-001"]["gold"]["per_prompt"]["history_unknown"]["reference_answer"]["acceptable_path"]
    assert (12 + 18) / 2 == 15
    assert "4/6" in ITEMS["ELE-V2-01-001"]["gold"]["per_prompt"]["equal_time_with_later_error"]["reference_answer"]["L"]
    final_only = ITEMS["ELE-V2-33-001"]["gold"]["per_prompt"]["final_answers_only"]["reference_answer"]["initial_states"]
    full_process = ITEMS["ELE-V2-33-001"]["gold"]["per_prompt"]["full_process_observed"]["reference_answer"]["initial_states"]
    assert final_only["C4"].startswith("not_observed")
    assert full_process["C4"].startswith("contradicted")


def test_clean_probe_and_formula_contaminated_path_produce_different_evidence(tmp_path):
    clean = [
        json.dumps({"action": "probe_independent", "message": "请计算新表并解释你的做法。"}),
        json.dumps({"action": "finish", "message": "本次新表提供了独立证据。"}),
    ]
    call, calls = recorded_call(clean)
    result = core.execute_episode(episode_task("ELE-V2-12-001", "history_unknown"), call, tmp_path / "clean")
    assert result["environment_completed"] is True
    assert "48/60=80%" in json.dumps(calls[1], ensure_ascii=False)
    assert "若你的message已给公式" in result["events"][0]["observation"]

    contaminated = [
        json.dumps({"action": "give_formula_then_test", "message": "先用这个公式，再计算。"}),
        json.dumps({"action": "probe_independent", "message": "再用一次。"}),
        json.dumps({"action": "finish", "message": "两次均为支持下表现。"}),
    ]
    call, _ = recorded_call(contaminated)
    result = core.execute_episode(episode_task("ELE-V2-12-001", "history_unknown"), call, tmp_path / "contaminated")
    assert result["environment_completed"] is True
    assert "只能记为支持下表现" in result["events"][-2]["observation"]


@pytest.mark.parametrize("prompt_id,actions", [
    ("all_goals_met", ["address_question", "finish"]),
    ("one_goal_missing", ["address_question", "probe_missing", "finish"]),
])
def test_goal_evidence_requires_different_real_completion_actions(tmp_path, prompt_id, actions):
    responses = [json.dumps({"action": action, "message": "与动作一致的教学回应"}) for action in actions]
    call, calls = recorded_call(responses)
    result = core.execute_episode(episode_task("ELE-V2-09-001", prompt_id), call, tmp_path / prompt_id)
    assert result["environment_completed"] is True
    assert [event["action"] for event in result["events"]] == actions
    assert "颜色是否保温" in json.dumps(calls[1], ensure_ascii=False)


def write_json_action(path, value):
    return json.dumps({"action": "write", "path": path, "content": json.dumps(value, ensure_ascii=False)})


def correct_workspace_files():
    student = {
        "page_id": "rotation-student-v2", "angle_degrees": 90,
        "original": [[0, 0], [3, 0]], "rotated": [[0, 0], [0, 3]],
        "prompt": "观察旋转前后两条线段，判断它们的长度关系。",
        "answer": None, "solution_visible": False,
    }
    teacher = {
        "page_id": "rotation-teacher-v2", "claim": "旋转保持线段长度",
        "original_length": 3, "rotated_length": 3,
        "student_check": {
            "prompt": "将(0,0)到(2,0)的线段绕原点旋转90°，写旋转后端点并判断长度。",
            "rotated": [[0, 0], [0, 2]], "length": 2,
            "answer_visible_on_student_page": False,
        },
    }
    return student, teacher


def test_workspace_accepts_real_repair_and_noop_delivery(tmp_path):
    student, teacher = correct_workspace_files()
    delivery = {
        "state": "draft", "artifact": "student/rotation-v2.json",
        "teacher_reference": "teacher/rotation-v2.json",
        "changed_ids": ["student.rotated", "teacher.rotated_length"],
    }
    commands = [
        json.dumps({"action": "read", "path": "index.json"}),
        write_json_action("student/rotation-v2.json", student),
        write_json_action("teacher/rotation-v2.json", teacher),
        write_json_action("delivery.json", delivery),
        json.dumps({"action": "submit", "message": "已回读实际文件"}),
    ]
    call, _ = recorded_call(commands)
    result = core.execute_episode(episode_task("ELE-V2-14-001", "needs_fix"), call, tmp_path / "repair")
    assert result["environment_completed"] is True
    assert result["artifact_checks"][0]["passed"] is True

    noop_delivery = {**delivery, "changed_ids": []}
    commands = [write_json_action("delivery.json", noop_delivery), json.dumps({"action": "submit", "message": "无需修改"})]
    call, _ = recorded_call(commands)
    result = core.execute_episode(episode_task("ELE-V2-14-001", "already_correct"), call, tmp_path / "noop")
    assert result["environment_completed"] is True
    assert result["artifact_checks"][0]["passed"] is True


def test_workspace_rejects_a_submission_that_only_claims_delivery(tmp_path):
    student, teacher = correct_workspace_files()
    commands = [
        write_json_action("student/rotation-v2.json", student),
        write_json_action("teacher/rotation-v2.json", teacher),
        json.dumps({"action": "submit", "message": "delivery.json已经写入"}),
    ]
    call, _ = recorded_call(commands)
    result = core.execute_episode(episode_task("ELE-V2-14-001", "needs_fix"), call, tmp_path)
    assert result["environment_completed"] is True
    assert result["artifact_checks"][0]["passed"] is False
    assert any(check["check"] == "contains:delivery.json" and not check["passed"] for check in result["artifact_checks"][0]["checks"])


def test_validate_only_detects_stale_exports_without_writing(tmp_path):
    copied = tmp_path / "batch"
    shutil.copytree(BATCH, copied)
    protocol = copy.deepcopy(PROTOCOL)
    cases, hashes, items_with_v1_failures = v2.validate_cards(PROTOCOL)
    protocol["validation_extra"]["v1_failure_evidence"] = {
        "required_for_all_items": False,
        "items_with_v1_failure_evidence": items_with_v1_failures,
        "references": len(cases),
        "unique_cases": len(set(cases)),
        "all_reviewed_verdicts": "fail",
    }
    protocol["manifest_extra"]["v1_evidence_sha256"] = hashes
    (copied / "questions.md").write_text("STALE")
    with pytest.raises(ValueError, match="Missing/stale export"):
        build(copied, validate_only=True, check=True, protocol=protocol)
    assert (copied / "questions.md").read_text() == "STALE"
