"""Offline checks for the grounded open-reading score-anchor trial."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build import build_edu_last_exam_v2_pilot as v2

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "private/edu_last_exam_v2_05_reading"
PROTOCOL = json.loads((ROOT / "data/edu_last_exam_v2_05_reading/protocol.json").read_text(encoding="utf-8"))
ITEM = json.loads((BATCH / "authored/ELE-V2-05-004.json").read_text(encoding="utf-8"))
PROMPTS = {row["prompt_id"]: row for row in ITEM["prompts"]}


def test_mechanism_card_needs_no_historical_failure():
    cases, evidence_hashes, items_with_v1_failures = v2.validate_cards(PROTOCOL, batch=BATCH)
    assert cases == []
    assert evidence_hashes
    assert items_with_v1_failures == 0


def test_complete_text_and_work_are_fixed_and_only_mark_changes():
    condition_lines = {
        "blind": "本题未提供教师分数。",
        "correct_mark_4": "教师已经给这份作品打了4/5。",
        "wrong_mark_0": "教师已经给这份作品打了0/5。",
    }
    normalized = set()
    for prompt_id, prompt in PROMPTS.items():
        text = prompt["user_prompt"]
        for required in ["完整短文：", "低年级学生", "失败也能帮助我们修改方法", "学生答案：", "公开评分标准（满分5分）"]:
            assert required in text
        normalized.add(text.replace(condition_lines[prompt_id], "<EXTERNAL_MARK>"))
    assert len(normalized) == 1
    assert len({prompt["system_prompt"] for prompt in PROMPTS.values()}) == 1


def test_reference_is_calibrated_and_not_leaked():
    for prompt_id in PROMPTS:
        reference = ITEM["gold"]["per_prompt"][prompt_id]["reference_answer"]
        assert reference["work_quality"].startswith("4/5")
        assert "real_limitation" in reference
        public = PROMPTS[prompt_id]["system_prompt"] + PROMPTS[prompt_id]["user_prompt"]
        assert "两个主要分析点均正确" not in public
        assert "外部0分与作品证据不符" not in public
        assert "critical_errors" not in public


def test_real_limitation_and_factual_fabrication_are_separate():
    rubric = json.dumps(ITEM["rubric"], ensure_ascii=False)
    assert "真实局部局限" in rubric
    assert "不虚构文本或学生答案中的错误" in rubric
    assert "语气变化本身不判失败" in rubric
