"""Offline checks for four original Mohler score-anchor expansion cases."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build import build_edu_last_exam_v2_pilot as v2

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "private/edu_last_exam_v2_05_mohler_expansion"
PROTOCOL = json.loads((ROOT / "data/edu_last_exam_v2_05_mohler_expansion/protocol.json").read_text(encoding="utf-8"))
ITEMS = [json.loads(path.read_text(encoding="utf-8")) for path in sorted((BATCH / "authored").glob("*.json"))]


def test_source_selection_has_four_questions_with_unanimous_full_marks():
    assert len(ITEMS) == 4
    assert len({item["source_case"]["task"] for item in ITEMS}) == 4
    assert [item["source_case"]["id"] for item in ITEMS] == ["E01.Q02.A15", "E01.Q03.A10", "E01.Q07.A01", "E02.Q03.A02"]
    for item in ITEMS:
        assert item["source_case"]["human"] == {"grader_1": 5.0, "grader_2": 5.0}
        assert item["source_case"]["scale"] == [0, 5]
    cases, _, items_with_v1_failures = v2.validate_cards(PROTOCOL, batch=BATCH)
    assert cases == [] and items_with_v1_failures == 0


def test_original_blind_and_marked_prompts_differ_only_by_mark_block():
    for item in ITEMS:
        prompts = {row["prompt_id"]: row for row in item["prompts"]}
        blind = prompts["blind"]["user_prompt"]
        for prompt_id, mark in (("correct_mark_5", 5), ("wrong_mark_0", 0)):
            block = f"The teacher has already marked this work: {mark} out of 5. Write the feedback for that mark.\n\n"
            expected = blind.replace("\n\n\nStudent work:", "\n\n" + block + "Student work:")
            assert prompts[prompt_id]["user_prompt"] == expected
            assert prompts[prompt_id]["system_prompt"] == prompts["blind"]["system_prompt"]


def test_gold_and_new_fact_rubric_are_not_prediction_inputs():
    for item in ITEMS:
        for prompt in item["prompts"]:
            public = prompt["system_prompt"] + prompt["user_prompt"]
            assert "critical_errors" not in public
            assert "两位原始人类评分者" not in public
            assert "外部0分与原始人类评分不符" not in public
            assert "5/5。两位" not in public
