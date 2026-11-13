#!/usr/bin/env python3
"""Validate and export the 37-direction exploratory task batch, entirely offline."""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage.core import BATCH, artifact_check, asset_path, digest, load_items, runtime_for, write_json
from scripts.build.build_edu_last_exam_scenario_v1 import html_document


def oracle_checks(batch, items):
    checks = []
    validators = sorted({runtime_for(i, p["prompt_id"])["validator"] for i in items for p in i["prompts"] if runtime_for(i, p["prompt_id"]).get("mode") == "artifact"})
    for validator in validators:
        source = batch / "reference" / validator / "oracle_cases.json"
        if not source.is_file():
            raise ValueError(f"Missing positive/negative artifact oracle: {source}")
        examples = json.loads(source.read_text())
        if {e["expected_pass"] for e in examples} != {False, True}:
            raise ValueError(f"Validator {validator} needs both positive and negative checks")
        for number, example in enumerate(examples):
            with tempfile.TemporaryDirectory(prefix=f"edu_fc_{validator}_") as tmp:
                result = artifact_check({"validator": validator}, example["response_text"], Path(tmp), example["prompt_id"])
                if result.get("passed") is not example["expected_pass"]:
                    raise ValueError(f"Oracle {validator}/{number} failed: {result}")
                checks.append({"validator": validator, "example": number, "expected_pass": example["expected_pass"], "matched": True})
    return checks


def build(batch, validate_only=False, check=False, allow_partial=False, protocol=None):
    protocol = protocol or {}
    items = load_items(
        batch,
        require_all=not allow_partial,
        item_glob=protocol.get("item_glob", "ELE-FC-*.json"),
        item_id_pattern=protocol.get("item_id_pattern", r"ELE-FC-\d{2}-\d{3}"),
        expected_item_ids=protocol.get("expected_item_ids"),
    )
    oracles = oracle_checks(batch, items)
    prompts, runtimes, assets = [], {}, {}
    question_lines = protocol.get("question_lines", ["# Edu Last Exam 全方向探索题册", "", "作者候选，独立教师审阅待完成；题册不含评分金标。版本与基础案例分别计数。", ""])
    review_lines = protocol.get("review_lines", ["# Edu Last Exam 全方向评分与测量边界", "", "仅供审阅，禁止投递给被测模型。语义评分需独立复核，试跑不等于冻结。", ""])
    report_dir = ROOT / protocol.get("report_directory", "reports/full_coverage_v1")
    summary_rows = []
    for item in items:
        item_id = item["item_id"]
        question_lines += [f"## {item_id} · {item['title']}", ""]
        review_lines += [f"## {item_id} · {item['title']}", "", "测量：" + item["measurement_claim"], "", "机制：" + item["failure_mechanism"], "", "教育后果：" + item["education_consequence"], "", "未测子结论：" + "；".join(item["unmeasured_subclaims"]), "", "### 来源与适配", "", "```json", json.dumps({k: item[k] for k in ("material_origin", "source_evidence", "adaptations", "limitations")}, ensure_ascii=False, indent=2), "```", ""]
        for prompt in item["prompts"]:
            row = {"item_id": item_id, "direction_id": item["direction_id"], **{k: prompt[k] for k in ("prompt_id", "system_prompt", "user_prompt", "assets", "interaction_mode")}}
            prompts.append(row)
            case_id = item_id + "__" + prompt["prompt_id"]
            runtime = runtime_for(item, prompt["prompt_id"])
            runtimes[case_id] = runtime
            question_lines += [f"### 版本 {prompt['prompt_id']} · {runtime['mode']}", "", prompt["system_prompt"], "", prompt["user_prompt"], ""]
            for relative in prompt["assets"]:
                path = asset_path(batch, relative)
                assets[relative] = {"sha256": digest(path.read_bytes()), "bytes": path.stat().st_size}
                question_lines += [f"[附件 {relative}]({relative})", ""]
            review_lines += [f"### 版本 {prompt['prompt_id']}", "", "```json", json.dumps(item["gold"]["per_prompt"][prompt["prompt_id"]], ensure_ascii=False, indent=2), "```", ""]
        review_lines += ["### Rubric、控制与环境", "", "```json", json.dumps({"rubric": item["rubric"], "controls": item["controls"], "runtime": item.get("runtime", {})}, ensure_ascii=False, indent=2), "```", ""]
        summary_rows.append({"direction_id": item["direction_id"], "item_id": item_id, "title": item["title"], "variants": len(item["prompts"]), "modes": sorted({runtime_for(item, p["prompt_id"])["mode"] for p in item["prompts"]}), "measurement_claim": item["measurement_claim"], "unmeasured_subclaims": item["unmeasured_subclaims"], "human_review": item["status"]["human_review"]})
    expected_prompt_count = protocol.get("expected_prompt_count")
    if expected_prompt_count is not None and len(prompts) != expected_prompt_count:
        raise ValueError(f"Prompt count mismatch: expected {expected_prompt_count}, got {len(prompts)}")
    validation = {"status": "offline_validated_candidate", "direction_count": len({i["direction_id"] for i in items}), "item_count": len(items), "prompt_count": len(prompts), "asset_count": len(assets), "runtime_counts": dict(collections.Counter(r["mode"] for r in runtimes.values())), "artifact_oracles": oracles, "human_review": "pending", "difficulty": "not_established", "model_evaluation": "tracked_in_separate_runs", "complete_direct_measurement_all_subclaims": False}
    validation.update(protocol.get("validation_extra", {}))
    exported = {
        batch / "items.jsonl": ''.join(json.dumps(i, ensure_ascii=False) + "\n" for i in items),
        batch / "prompts.jsonl": ''.join(json.dumps(p, ensure_ascii=False) + "\n" for p in prompts),
        batch / "runtimes.json": json.dumps(runtimes, ensure_ascii=False, indent=2) + "\n",
        batch / "questions.md": '\n'.join(question_lines) + "\n",
        batch / "review.md": '\n'.join(review_lines) + "\n",
        batch / "questions.html": html_document('\n'.join(question_lines), protocol.get("questions_html_title", "Edu Last Exam 全方向题册")).decode(),
        batch / "review.html": html_document('\n'.join(review_lines), protocol.get("review_html_title", "Edu Last Exam 评分审阅册")).decode(),
    }
    for item in items:
        exported[batch / "reference" / (item["item_id"] + ".json")] = json.dumps({k: item[k] for k in ("gold", "rubric", "controls", "measurement_claim", "unmeasured_subclaims")}, ensure_ascii=False, indent=2) + "\n"
    default_author = {"agent": "Codex", "method": "source_curation_and_assisted_authoring", "exact_model_id": "not_exposed_in_task", "excluded_test_author": "GLM-5.3-Flash did not author canonical content"}
    manifest = {**validation, "schema_version": protocol.get("schema_version", "edu_full_coverage_candidate_v1"), "author": protocol.get("author", default_author), "prediction_export_sha256": digest(exported[batch / "prompts.jsonl"].encode()), "runtime_sha256": digest(exported[batch / "runtimes.json"].encode()), "item_export_sha256": digest(exported[batch / "items.jsonl"].encode()), "assets": assets, "coverage": summary_rows, "canonical": False, "frozen": False}
    manifest.update(protocol.get("manifest_extra", {}))
    exported[batch / "manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    exported[report_dir / "offline_validation.json"] = json.dumps(validation, ensure_ascii=False, indent=2) + "\n"
    coverage_lines = protocol.get("coverage_lines", ["# 全方向候选实现状态", "", "本表由作者题包生成，不表示已完成独立教师审核或所有子构念的直接测量。", "", "|方向|题包|版本|环境|测量边界|尚未覆盖|", "|---|---|---:|---|---|---|"])
    for row in summary_rows:
        values = [row["direction_id"], row["item_id"], str(row["variants"]), ", ".join(row["modes"]), row["measurement_claim"], "；".join(row["unmeasured_subclaims"])]
        coverage_lines.append("|" + "|".join(v.replace("|", "／").replace("\n", " ") for v in values) + "|")
    exported[report_dir / "implementation_status.md"] = '\n'.join(coverage_lines) + "\n"
    exported[report_dir / "implementation_status.html"] = html_document('\n'.join(coverage_lines), protocol.get("coverage_html_title", "全方向候选实现状态")).decode()
    if check:
        for path, content in exported.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise ValueError(f"Missing/stale export: {path}")
    elif not validate_only:
        for path, content in exported.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False))
    return validation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--allow-partial", action="store_true", help="Development only; cannot declare full coverage")
    args = parser.parse_args()
    build(args.batch.resolve(), args.validate_only, args.check, args.allow_partial)


if __name__ == "__main__":
    main()
