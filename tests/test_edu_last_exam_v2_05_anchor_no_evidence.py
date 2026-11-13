"""Offline checks for the evidence-scaffolding ablation."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build import build_edu_last_exam_v2_pilot as v2

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "private/edu_last_exam_v2_05_anchor/authored/ELE-V2-05-002.json").read_text(encoding="utf-8"))
BATCH = ROOT / "private/edu_last_exam_v2_05_anchor_no_evidence"
ITEM = json.loads((BATCH / "authored/ELE-V2-05-003.json").read_text(encoding="utf-8"))
PROTOCOL = json.loads((ROOT / "data/edu_last_exam_v2_05_anchor_no_evidence/protocol.json").read_text(encoding="utf-8"))


def test_ablation_card_does_not_need_historical_failure():
    cases, _, items_with_v1_failures = v2.validate_cards(PROTOCOL, batch=BATCH)
    assert cases == []
    assert items_with_v1_failures == 0


def test_user_inputs_and_gold_are_identical_to_the_prior_trial():
    base_prompts = {row["prompt_id"]: row for row in BASE["prompts"]}
    for prompt in ITEM["prompts"]:
        base = base_prompts[prompt["prompt_id"]]
        assert prompt["user_prompt"] == base["user_prompt"]
        assert prompt["interaction_mode"] == base["interaction_mode"]
        assert ITEM["gold"]["per_prompt"][prompt["prompt_id"]] == BASE["gold"]["per_prompt"][prompt["prompt_id"]]
        assert '"evidence"' not in prompt["system_prompt"]
        assert prompt["system_prompt"] == base["system_prompt"].replace(',"evidence":["支持反馈判断的学生原文引文"]', "")


def test_scoring_does_not_turn_missing_quotes_into_a_hidden_failure():
    c1 = ITEM["rubric"]["criteria"][0]["observable"]
    assert "原文证据" not in c1
    assert "语气变化本身不判失败" in json.dumps(ITEM["rubric"], ensure_ascii=False)
