#!/usr/bin/env python3
"""Validate and export the authored Edu Last Exam challenge candidates.

Offline only. Does not call a model, score model responses, or modify pilot v1.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "private/edu_last_exam_pilot_v1/challenge_v2"
SPEC = ROOT / "data/edu_last_exam_pilot_v1/challenge_v2/authoring_spec.json"


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def asset_path(path, prefix):
    relative = Path(path)
    assert not relative.is_absolute() and ".." not in relative.parts, f"Unsafe path: {path}"
    assert relative.parts[0] == prefix, f"Unexpected {prefix} reference: {path}"
    resolved = (BATCH / relative).resolve()
    assert resolved.is_relative_to(BATCH.resolve()) and resolved.is_file(), f"Missing or external file: {path}"
    return resolved


def validate(items, spec):
    assert {r["direction_id"] for r in items} == set(spec["expected_direction_ids"]), "Incomplete direction coverage"
    assert len(items) == len(spec["expected_direction_ids"]), "Duplicate direction"
    cards = read_jsonl(BATCH / "cards.jsonl")
    assert {c["item_id"] for c in cards} == {r["item_id"] for r in items}, "Card/item mismatch"
    checks = set()
    for item in items:
        ident = item["item_id"]
        assert ident == f'ELE-C2-{item["direction_id"]:02d}', ident
        assert set(spec["required_fields"]) <= item.keys(), ident
        assert item["author"] == "codex" and item["material_origin"] == "synthetic_research_informed", ident
        assert item["challenge_rationale"]["difficulty_status"] == "challenge_candidate_not_measured", ident
        assert item["source_evidence"], ident
        for source in item["source_evidence"]:
            assert 2024 <= source["year"] <= 2026 and source["url"].startswith("https://"), source
            assert all(source.get(k) for k in ("title", "supported_mechanism", "limits")), source
        prompts = item["prompts"]
        prompt_ids = {p["prompt_id"] for p in prompts}
        assert len(prompt_ids) == len(prompts) and prompts, ident
        assert set(item["gold"]["per_prompt"]) == prompt_ids, f"Gold/prompt mismatch: {ident}"
        for prompt in prompts:
            assert prompt["system_prompt"].strip() and prompt["user_prompt"].strip(), ident
            assert prompt["interaction_mode"] in {"single_turn", "decision_snapshot", "artifact_task"}, ident
            for path in prompt["assets"]:
                asset_path(path, "stimuli")
            assert "reference/" not in prompt["user_prompt"], f"Reference path leaked: {ident}"
        for gold in item["gold"]["per_prompt"].values():
            assert gold["reference_answer"] and gold["reasoning"] and gold["acceptable_alternatives"], ident
        rubric = item["rubric"]
        assert 4 <= len(rubric["criteria"]) <= 6, ident
        assert sum(c["points"] for c in rubric["criteria"]) == rubric["total_points"] == 10, ident
        assert len({c["criterion_id"] for c in rubric["criteria"]}) == len(rubric["criteria"]), ident
        covered = set()
        for criterion in rubric["criteria"]:
            assert criterion["description"] and criterion["visible_requirement"] and criterion["points"] > 0, ident
            assert criterion["prompt_scope"] and set(criterion["prompt_scope"]) <= prompt_ids, ident
            covered.update(criterion["prompt_scope"])
        assert covered == prompt_ids, ident
        review = item["self_review"]
        assert all(review[k] is True for k in ("input_sufficient", "gold_checked", "no_hidden_requirements")), ident
        assert review["human_review"] == "pending" and review["model_evaluation"] == "not_run", ident
        assert review["checks"], ident
        for path in review["checks"]:
            checks.add(asset_path(path, "checks"))
    results = []
    for script in sorted(checks):
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, capture_output=True, text=True, timeout=60)
        assert result.returncode == 0, f"{script.name}:\n{result.stdout}\n{result.stderr}"
        results.append({"path": str(script.relative_to(BATCH)), "status": "passed", "output": result.stdout.strip()})
    return results


def pretty(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)


def gold_documents(item):
    markdown, web = [], []
    for variant, gold in item["gold"]["per_prompt"].items():
        answer = pretty(gold["reference_answer"])
        markdown.extend([f"### 参考答案 · {variant}", "", answer, "", "推导与依据：" + gold["reasoning"], "", "可接受替代：", ""])
        markdown.extend("- " + text for text in gold["acceptable_alternatives"])
        markdown.append("")
        alternatives = ''.join('<li>' + html.escape(text) + '</li>' for text in gold["acceptable_alternatives"])
        web.append(f'<h3>参考答案 · {html.escape(variant)}</h3><pre>{html.escape(answer)}</pre><p>{html.escape(gold["reasoning"])}</p><p>可接受替代：</p><ul>{alternatives}</ul>')
    references = sorted((BATCH / "reference" / f'{item["direction_id"]:02d}').glob("*"))
    if references:
        markdown.extend(["### 参考产物", ""])
        web.append('<h3>参考产物</h3><ul>')
        for path in references:
            if not path.is_file():
                continue
            relative = str(path.relative_to(BATCH))
            markdown.append(f"- [{path.name}]({relative})")
            web.append(f'<li><a href="{html.escape(relative, quote=True)}">{html.escape(path.name)}</a></li>')
        markdown.append("")
        web.append('</ul>')
    markdown.extend(["### 常见误判", ""] + ["- " + s for s in item["gold"]["common_misjudgments"]] + [""])
    web.append('<h3>常见误判</h3><ul>' + ''.join('<li>' + html.escape(s) + '</li>' for s in item["gold"]["common_misjudgments"]) + '</ul>')
    return markdown, ''.join(web)


def make_documents(items):
    preamble = "21 个方向的合成挑战候选。作者自检已完成；人工审核待做；未进行模型实测。多变体属于同一任务包，不能当作独立难题数。"
    questions = ["# Edu Last Exam · challenge_v2 题目册", "", preamble, "", "题目中的附件均在 stimuli/ 下。评测时只交付对应 prompt 和其 assets；不得向受测 Agent 开放本题库所在整个目录。", ""]
    review = ["# Edu Last Exam · challenge_v2 审阅册", "", preamble, "", "本文件包含参考解。评分按实质能力分项，允许合理替代答案；critical_errors 是审核提示，不触发整题自动归零。", ""]
    articles = []
    for item in items:
        title = f'{item["item_id"]} · {item["title"]}'
        q = [f"## {title}", ""]
        html_prompts = []
        for prompt in item["prompts"]:
            q.extend([f'### 版本 {prompt["prompt_id"]}', "", "**角色说明**", "", prompt["system_prompt"], "", "**题面**", "", prompt["user_prompt"], ""])
            links = []
            for path in prompt["assets"]:
                q.append(f"- [附件：{path}]({path})")
                safe = html.escape(path, quote=True)
                links.append(f'<p><a href="{safe}">{safe}</a></p>')
                if Path(path).suffix.lower() in {".png", ".svg", ".jpg"}:
                    links.append(f'<img src="{safe}" alt="题目附件">')
            q.append("")
            html_prompts.append(f'<h3>版本 {html.escape(prompt["prompt_id"])}</h3><p class="role">{html.escape(prompt["system_prompt"])}</p><pre>{html.escape(prompt["user_prompt"])}</pre>' + "".join(links))
        questions.extend(q)
        rationale = item["challenge_rationale"]
        gold_md, gold_html = gold_documents(item)
        review.extend(q + ["### 为什么可能有挑战", "", rationale["failure_mechanism"], "", rationale["why_not_trivial"], "", "教育后果：" + rationale["educational_consequence"], ""] + gold_md + ["### 评分依据", "", "```json", pretty(item["rubric"]), "```", "", "### 文献及证据边界", ""])
        sources = []
        for source in item["source_evidence"]:
            review.extend([f'- [{source["title"]}]({source["url"]})（{source["year"]}）：{source["supported_mechanism"]} 限制：{source["limits"]}', ""])
            sources.append(f'<p><a href="{html.escape(source["url"], quote=True)}">{html.escape(source["title"])}</a>（{source["year"]}）：{html.escape(source["supported_mechanism"])}<br>证据边界：{html.escape(source["limits"])}</p>')
        article = f'<article id="{item["item_id"]}"><h2>{html.escape(title)}</h2><p class="meta">方向 {item["direction_id"]} · {html.escape(item["direction_name"])}</p>' + "".join(html_prompts)
        article += '<details><summary>查看出题理由、参考解与评分依据</summary>'
        article += f'<h3>出题理由</h3><pre>{html.escape(pretty(rationale))}</pre>' + gold_html + f'<h3>评分</h3><pre>{html.escape(pretty(item["rubric"]))}</pre><h3>来源及限制</h3>' + "".join(sources) + '</details></article>'
        articles.append(article)
    toc = ''.join(f'<li><a href="#{r["item_id"]}">{r["item_id"]} {html.escape(r["title"])}</a></li>' for r in items)
    page = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Edu Last Exam · challenge_v2</title><style>body{font:17px/1.7 system-ui,sans-serif;max-width:1100px;margin:30px auto;padding:20px;color:#172a3a;background:#f5f7fa}article{padding:26px;background:white;margin:28px 0;border:1px solid #d5dfe7;border-radius:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}img{max-width:100%;height:auto;border:1px solid #dde4ea}summary{cursor:pointer;font-weight:bold;color:#075b7d}details{background:#edf4f7;padding:18px;margin-top:24px}.meta,.role{color:#465b6c}a{color:#076688}h2{line-height:1.4}</style><h1>Edu Last Exam · challenge_v2</h1><p>' + preamble + '</p><p>本页含折叠的答案，仅供审阅。评测时使用 prompts.jsonl 与其中指定的 stimuli 附件，并隔离所有参考材料。</p><ol>' + toc + '</ol>' + ''.join(articles) + '</html>'
    return "\n".join(questions), "\n".join(review), page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text())
    drafts = sorted((BATCH / "authored").glob("*.jsonl"))
    items = sorted([r for path in drafts for r in read_jsonl(path)], key=lambda r: r["direction_id"])
    checks = validate(items, spec)
    prompts = [{"item_id": item["item_id"], **prompt} for item in items for prompt in item["prompts"]]
    if not args.validate_only:
        for name, rows in (("items.jsonl", items), ("prompts.jsonl", prompts)):
            (BATCH / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        questions, review, page = make_documents(items)
        for name, content in (("questions.md", questions), ("review.md", review), ("review.html", page)):
            (BATCH / name).write_text(content, encoding="utf-8")
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["item_id", "direction", "title", "prompt_count", "difficulty_status", "author_check", "human_review", "model_evaluation"])
        for item in items:
            writer.writerow([item["item_id"], item["direction_name"], item["title"], len(item["prompts"]), "candidate_not_measured", "passed", "pending", "not_run"])
        (BATCH / "review_sheet.csv").write_text(buf.getvalue(), encoding="utf-8-sig")
        manifest_files = drafts + [BATCH / "cards.jsonl", SPEC] + sorted((BATCH / "stimuli").rglob("*")) + sorted((BATCH / "reference").rglob("*")) + sorted((BATCH / "checks").glob("*.py"))
        hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in manifest_files if p.is_file()}
        manifest = {"status": "authored_candidate", "item_count": len(items), "prompt_count": len(prompts), "human_review": "pending", "model_evaluation": "not_run", "offline_checks": checks, "sha256": hashes}
        (BATCH / "build_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report = ["# challenge_v2 作者检查与导出", "", f"- 任务包：{len(items)}；独立投递 prompt：{len(prompts)}；覆盖方向：21。", "- 材料：合成研究启发题，作者 Codex；未使用受测模型 API 生成。", "- 状态：作者离线自检通过；人工审核 pending；模型实测 not_run。", "- 原 pilot 的 12 题与评测适配器未纳入此次构建。", "- 检查只验证所列数学、程序或材料一致性，不能证明教育有效性或前沿模型难度。", "- 浏览器检查另见 reports/challenge_v2/authoring_checks/；不能从数学检查推定浏览器检查已完成。", "", "## 离线检查", ""]
        report.extend(f'- `{r["path"]}`：{r["output"]}' for r in checks)
        (BATCH / "build_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"status": "validated" if args.validate_only else "exported", "items": len(items), "prompts": len(prompts), "checks": len(checks), "model_evaluation": "not_run"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
