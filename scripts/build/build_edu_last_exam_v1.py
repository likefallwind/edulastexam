#!/usr/bin/env python3
"""Build the small, reviewable Edu Last Exam v1 test candidate.

The source challenge_v2 batch is kept intact.  This builder selects eight
reviewed packages, applies only the documented wording/gold corrections, and
copies their public stimuli, private references, and offline checks into a
separate release-candidate directory.  It never calls a model or the network.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "private/edu_last_exam_pilot_v1/challenge_v2"
OUT = ROOT / "private/edu_last_exam_v1"
SELECTION = ROOT / "data/edu_last_exam_v1/selection.json"
DATA_README = ROOT / "data/edu_last_exam_v1/README.md"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def selected_ids(selection: dict) -> list[str]:
    ids = [package["item_id"] for package in selection["packages"]]
    assert len(ids) == len(set(ids)) == 8, ids
    assert ids == ["ELE-C2-01", "ELE-C2-03", "ELE-C2-09", "ELE-C2-10", "ELE-C2-12", "ELE-C2-13", "ELE-C2-16", "ELE-C2-20"], ids
    return ids


def apply_revisions(item: dict) -> dict:
    """Apply the audit's narrow revisions without changing challenge_v2."""
    item = copy.deepcopy(item)
    ident = item["item_id"]
    gold = item["gold"]["per_prompt"]

    if ident == "ELE-C2-10":
        answer = gold["base"]["reference_answer"]
        answer["quantitative"]["max_difference_error_g"] = "0.4"
        answer["quantitative"]["error_explanation"] = (
            "两次读数各自的误差界为±0.2g；比较前后读数时误差相减，最坏差值误差界为±0.4g。"
            "只有真实变化大于0.4g时，才可仅凭误差界保证辨别；具体一对读数仍须结合允许区间判断。"
        )
        item["rubric"]["criteria"][3]["description"] = (
            "两分支反馈正确处理系统边界和气体去向；明确两次±0.2g读数比较的最坏差值误差为±0.4g，"
            "区分真实/理想量减少与实际显示可能不可辨，不凭未知数据给具体读数。"
        )

    elif ident == "ELE-C2-12":
        answer = gold["base"]["reference_answer"]
        answer["current_state"] = (
            "按 record_id 核对：负号展开的早期无提示错误为 R03、R07、R11、R14；"
            "近期无提示成功为 R23、R24、R25、R26、R28、R32、R34、R38。"
            "固定费用的无提示遗漏为 R05、R10、R17、R27、R30、R35、R37、R40；"
            "R31 是提示固定费用后改对。R33、R39 在其它文字情境中正确，R36 能独立解同构符号方程。"
            "因此优先核验费用语句到数量关系的转换，不能继续只用早期负号错例认定当前仍不会展开。"
        )
        gold["base"]["reasoning"] = (
            "按 record_id、日期、任务类别和实际援助分别核查：R03/R07/R11/R14 是早期无提示负号展开错误；"
            "R23/R24/R25/R26/R28/R32/R34/R38 是近期无提示正确。"
            "R05/R10/R17/R27/R30/R35/R37/R40 反复遗漏固定费用，R31 在提示后改对；"
            "R33/R39 的其它文字题和 R36 的同构符号方程构成反证。"
            "任务类别与提示不同，不能据此宣称因果学习增益或唯一认知原因。"
        )

    elif ident == "ELE-C2-16":
        for criterion in item["rubric"]["criteria"]:
            criterion["description"] = criterion["description"].replace("交付3", "交付2")
        item["self_review"]["protocol_note"] = (
            "静态一次性交付；题面要求设计两阶段测评，但当前 runner 不执行阶段间读数发放。"
        )

    elif ident == "ELE-C2-20":
        prompt = next(p for p in item["prompts"] if p["prompt_id"] == "base")
        prompt["user_prompt"] += (
            "\n\n附加可验收要求：评测会执行 `reset(); advance(2)`。"
            "历史曲线或 `samples` 必须包含 t=1 秒附近的真实中间状态，解析值约为 9.9326V，"
            "允许误差不超过0.05V；不能只保存端点后画直线。该检查与终点数值、切换连续性、历史不可改写分别计分。"
        )
        for criterion in item["rubric"]["criteria"]:
            if criterion["criterion_id"] == "representation":
                criterion["description"] = (
                    "曲线与当前状态一致，历史点不被改写，且包含足以检验指数变化的中间采样（例如t=1秒约9.9326V）；"
                    "重置恢复初态并清空历史，控件实际可操作。"
                )
        gold["base"]["reasoning"] += (
            " 端点通过不足以证明曲线真实；在两秒充电中必须保留中间采样，"
            "t=1秒的解析值约为9.9326V，不能用端点直线替代。"
        )
    return item


def safe_copy(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise AssertionError(f"missing source asset: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_package_assets(item: dict) -> None:
    number = f'{item["direction_id"]:02d}'
    for subtree in ("stimuli", "reference"):
        src = SOURCE / subtree / number
        dst = OUT / subtree / number
        if not src.is_dir():
            raise AssertionError(f"missing package directory: {src}")
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    safe_copy(SOURCE / "checks" / f"{number}.py", OUT / "checks" / f"{number}.py")


def validate_rows(items: list[dict], batch: Path) -> list[dict]:
    expected = {"ELE-C2-01", "ELE-C2-03", "ELE-C2-09", "ELE-C2-10", "ELE-C2-12", "ELE-C2-13", "ELE-C2-16", "ELE-C2-20"}
    assert {item["item_id"] for item in items} == expected
    assert len(items) == len(expected)
    checks: set[Path] = set()
    for item in items:
        assert item["author"] == "codex"
        assert item["material_origin"] == "synthetic_research_informed"
        assert item["challenge_rationale"]["difficulty_status"] == "challenge_candidate_not_measured"
        assert item["source_evidence"]
        for source in item["source_evidence"]:
            assert 2024 <= source["year"] <= 2026 and source["url"].startswith("https://")
        prompt_ids = {prompt["prompt_id"] for prompt in item["prompts"]}
        assert prompt_ids and len(prompt_ids) == len(item["prompts"])
        assert set(item["gold"]["per_prompt"]) == prompt_ids
        for prompt in item["prompts"]:
            assert prompt["system_prompt"].strip() and prompt["user_prompt"].strip()
            assert prompt["interaction_mode"] in {"single_turn", "decision_snapshot", "artifact_task"}
            assert "reference/" not in prompt["user_prompt"]
            for asset in prompt["assets"]:
                relative = Path(asset)
                assert relative.parts[0] == "stimuli" and ".." not in relative.parts and (batch / relative).is_file(), asset
        assert sum(c["points"] for c in item["rubric"]["criteria"]) == item["rubric"]["total_points"] == 10
        assert len({c["criterion_id"] for c in item["rubric"]["criteria"]}) == len(item["rubric"]["criteria"])
        assert item["self_review"]["human_review"] == "pending"
        for check in item["self_review"]["checks"]:
            relative = Path(check)
            assert relative.parts[0] == "checks" and relative.name == f'{item["direction_id"]:02d}.py'
            checks.add(batch / relative)
    results = []
    for check in sorted(checks):
        result = subprocess.run([sys.executable, str(check)], cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, f"{check}:\n{result.stdout}\n{result.stderr}"
        results.append({"path": str(check.relative_to(batch)), "status": "passed", "output": result.stdout.strip()})
    return results


def write_review_material(items: list[dict], checks: list[dict]) -> None:
    questions = [
        "# Edu Last Exam v1 · 测试候选题册",
        "",
        "本册只包含八个任务包；参考答案和评分依据存放在同目录的 review.md，不属于模型投递内容。",
        "",
    ]
    review = [
        "# Edu Last Exam v1 · 审阅册",
        "",
        "状态：test_release_candidate；人工审核 owner_review_pending；模型实测 not_run。",
        "",
    ]
    for item in items:
        title = f'{item["item_id"]} · {item["title"]}'
        questions += [f'## {title}', ""]
        review += [f'## {title}', "", "### 出题理由", "", item["challenge_rationale"]["failure_mechanism"], "", item["challenge_rationale"]["why_not_trivial"], ""]
        for prompt in item["prompts"]:
            questions += [f'### 版本 {prompt["prompt_id"]}', "", prompt["system_prompt"], "", prompt["user_prompt"], "", "附件：" + ", ".join(prompt["assets"]), ""]
            gold = item["gold"]["per_prompt"][prompt["prompt_id"]]
            review += [f'### 参考答案 · {prompt["prompt_id"]}', "", "```json", json.dumps(gold["reference_answer"], ensure_ascii=False, indent=2), "```", "", "依据：" + gold["reasoning"], "", "可接受替代：", ""]
            review += ["- " + alternative for alternative in gold["acceptable_alternatives"]] + ["", "常见误判：", ""]
            review += ["- " + error for error in item["gold"]["common_misjudgments"]] + [""]
        review += ["### 评分依据", "", "```json", json.dumps(item["rubric"], ensure_ascii=False, indent=2), "```", ""]
        questions += ["---", ""]
    (OUT / "questions.md").write_text("\n".join(questions) + "\n", encoding="utf-8")
    (OUT / "review.md").write_text("\n".join(review) + "\n", encoding="utf-8")
    prompts = [{"item_id": item["item_id"], **prompt} for item in items for prompt in item["prompts"]]
    write_jsonl(OUT / "prompts.jsonl", prompts)
    rows = [["item_id", "track", "title", "prompt_count", "difficulty_status", "human_review", "model_evaluation"]]
    tracks = {package["item_id"]: package["track"] for package in json.loads(SELECTION.read_text(encoding="utf-8"))["packages"]}
    rows.extend([[item["item_id"], tracks[item["item_id"]], item["title"], len(item["prompts"]), "not_measured", "owner_review_pending", "not_run"] for item in items])
    with (OUT / "review_sheet.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)
    report = ["# Edu Last Exam v1 构建报告", "", "- 8个任务包，" + str(len(prompts)) + "个投递 prompt。", "- 来源：challenge_v2；修订均记录在 data/edu_last_exam_v1/selection.json。", "- 状态：test_release_candidate；未进行模型实测。", "", "## 离线检查", ""]
    report += [f'- `{result["path"]}`：{result["output"]}' for result in checks]
    (OUT / "build_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def build() -> dict:
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    ids = selected_ids(selection)
    source_rows = {item["item_id"]: item for item in read_jsonl(SOURCE / "items.jsonl")}
    assert set(ids) <= source_rows.keys()
    items = [apply_revisions(source_rows[item_id]) for item_id in ids]
    source_checks = validate_rows(items, SOURCE)
    OUT.mkdir(parents=True, exist_ok=True)
    for item in items:
        copy_package_assets(item)
    write_jsonl(OUT / "items.jsonl", items)
    write_review_material(items, source_checks)
    shutil.copy2(SELECTION, OUT / "selection.json")
    (OUT / "README.md").write_text(
        "# Edu Last Exam v1 · 私有审阅与投递材料\n\n"
        "这里是由构建器导出的八个任务包测试候选集，包含题目投递稿、刺激材料、参考解和离线检查。\n"
        "机器可读选择清单见 [`data/edu_last_exam_v1/selection.json`](../../data/edu_last_exam_v1/selection.json)，\n"
        "逐题审查见 [`docs/reviews/edu_last_exam_challenge_v2_audit_2026-11-09.md`](../../docs/reviews/edu_last_exam_challenge_v2_audit_2026-11-09.md)。\n\n"
        "状态：`test_release_candidate`；人工审核：`owner_review_pending`；模型实测：`not_run`。\n",
        encoding="utf-8",
    )
    output_checks = validate_rows(items, OUT)
    hashes = {}
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            hashes[str(path.relative_to(OUT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "edu_last_exam_v1_test_2026-11-09",
        "status": "test_release_candidate",
        "human_review": "owner_review_pending",
        "model_evaluation": "not_run",
        "difficulty_status": "not_measured",
        "source_batch": str(SOURCE.relative_to(ROOT)),
        "package_count": len(items),
        "prompt_count": sum(len(item["prompts"]) for item in items),
        "item_ids": ids,
        "tracks": {package["item_id"]: package["track"] for package in selection["packages"]},
        "offline_checks": output_checks,
        "sha256": hashes,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": "exported", "items": len(items), "prompts": manifest["prompt_count"], "checks": len(output_checks), "model_evaluation": "not_run"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true", help="validate source-selected rows without writing v1")
    args = parser.parse_args()
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    ids = selected_ids(selection)
    source_rows = {item["item_id"]: item for item in read_jsonl(SOURCE / "items.jsonl")}
    items = [apply_revisions(source_rows[item_id]) for item_id in ids]
    if args.validate_only:
        checks = validate_rows(items, SOURCE)
        result = {"status": "validated", "items": len(items), "prompts": sum(len(item["prompts"]) for item in items), "checks": len(checks), "model_evaluation": "not_run"}
    else:
        result = build()
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
