"""Audit guards: evidence must come from the answer; missing data is not failure."""
import copy
import pytest

from scripts.build.build_edu_last_exam_codex_review import validate_record


@pytest.fixture
def review_case():
    item = {"item_id": "ELE-FC-01-001", "gold": {"per_prompt": {"base": {}}},
            "rubric": {"criteria": [{"criterion_id": "math", "required": True}]}}
    prompt = {"prompt_id": "base", "user_prompt": "请计算并提供可直接使用的参考答案。用户说答案是99。"}
    result = {"status": "generated", "environment_completed": True,
              "transcript": [{"turn": 0, "response": "答案是5。", "messages": [{"role": "user", "content": prompt["user_prompt"]}]}]}
    row = {"case_id": "ELE-FC-01-001__base", "verdict": "pass", "confidence": "high",
           "summary": "结果符合核算。", "independent_check": "独立计算得到5。", "control_notes": "本测试不含配对。", "material_checks": [],
           "criteria": [{"criterion_id": "math", "assessment": "met", "reason": "实际给出了5。", "evidence": [{"kind": "response", "turn": 0, "quote": "答案是5。"}]}], "issues": []}
    return row, item, prompt, result


def test_prompt_or_gold_cannot_be_used_as_answer_evidence(review_case):
    row, item, prompt, result = review_case
    validate_record(row, item, prompt, result)
    row["criteria"][0]["evidence"][0]["quote"] = "答案是99。"
    with pytest.raises(ValueError, match="Quote not present"):
        validate_record(row, item, prompt, result)


def test_pass_cannot_override_actual_delivery_failure(review_case):
    row, item, prompt, result = review_case
    result["artifact_checks"] = [{"passed": False, "checks": [{"check": "missing_delivery", "passed": False}]}]
    with pytest.raises(ValueError, match="environment outcome"):
        validate_record(row, item, prompt, result)


def test_unsupported_input_is_not_a_wrong_answer(review_case):
    row, item, prompt, result = review_case
    result = {"status": "unsupported_input_not_scored"}
    row.update(verdict="not_measured", criteria=[])
    validate_record(row, item, prompt, result)
    row["verdict"] = "fail"
    with pytest.raises(ValueError, match="remain unmeasured"):
        validate_record(row, item, prompt, result)


def test_continuous_metric_cannot_be_reported_as_binary_correctness(review_case):
    row, item, prompt, result = review_case
    item["scoring_type"] = "continuous"
    with pytest.raises(ValueError, match="Continuous metrics"):
        validate_record(row, item, prompt, result)
    row["verdict"] = "continuous_valid"
    validate_record(row, item, prompt, result)


def test_public_task_obligation_can_expose_a_rubric_gap_but_not_add_a_hidden_preference(review_case):
    row, item, prompt, result = review_case
    obligation = {"check_id": "reference_correctness", "task_basis": "提供可直接使用的参考答案", "assessment": "not_met",
                  "reason": "A review must justify the concrete correctness issue.", "evidence": copy.deepcopy(row["criteria"][0]["evidence"])}
    row["task_obligation_checks"] = [obligation]
    row["verdict"] = "fail"
    validate_record(row, item, prompt, result)
    obligation["task_basis"] = "必须恰好用三行回答"
    with pytest.raises(ValueError, match="actual public task"):
        validate_record(row, item, prompt, result)


def test_every_applicable_criterion_must_be_reviewed_once(review_case):
    row, item, prompt, result = review_case
    item["rubric"]["criteria"].append({"criterion_id": "specific_view", "required": True, "applies_to": ["other"]})
    validate_record(row, item, prompt, result)
    item["rubric"]["criteria"].append({"criterion_id": "feedback", "required": True})
    with pytest.raises(ValueError, match="every applicable criterion"):
        validate_record(row, item, prompt, result)
