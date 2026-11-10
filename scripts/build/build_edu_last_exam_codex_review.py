#!/usr/bin/env python3
"""Validate evidence-linked Codex review records and render a separate audit report.

Offline only. Original model answers, scores and frozen task definitions are read-only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import html
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage.core import criteria_for_prompt, parse_object
from scripts.full_coverage.judging import validate_judgment

RUN = ROOT / "reports/eval/edu_last_exam_full_coverage_v1/_exploratory/20261110_142158_glm53flash/GLM-5.3-Flash"
SOURCE = ROOT / "private/edu_last_exam_full_coverage_v1/reviews/glm53flash_20261110_codex"
OUTPUT = ROOT / "reports/full_coverage_v1/glm53flash_20261110_codex_review"
VERDICTS = {"pass", "fail", "disputed", "continuous_valid", "continuous_invalid", "not_measured"}
ASSESSMENTS = {"met", "not_met", "uncertain", "not_applicable"}
LABELS = {"pass": "通过", "fail": "未通过", "disputed": "争议待审", "continuous_valid": "连续指标有效", "continuous_invalid": "连续指标输出无效", "not_measured": "未测"}
ISSUE_TYPES = {"model_error", "item_or_gold_issue", "judge_issue", "runtime_issue", "minor_issue"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def validate_evidence(evidence, result):
    if not isinstance(evidence, list):
        raise ValueError("Evidence must be a list")
    for entry in evidence:
        if entry.get("kind") == "response":
            turns = {turn["turn"]: turn["response"] for turn in result.get("transcript", [])}
            if entry.get("turn") not in turns:
                raise ValueError("Evidence refers to an unobserved response turn")
            actual = turns[entry["turn"]]
        elif entry.get("kind") in {"event", "artifact_check"}:
            values = result.get("events" if entry["kind"] == "event" else "artifact_checks", [])
            index = entry.get("index")
            if type(index) is not int or not 0 <= index < len(values):
                raise ValueError("Evidence refers to a nonexistent environment record")
            actual = json.dumps(values[index], ensure_ascii=False)
        else:
            raise ValueError("Unknown evidence kind")
        quote = entry.get("quote")
        if not isinstance(quote, str) or not quote.strip() or quote not in actual:
            raise ValueError(f"Quote not present in actual {entry.get('kind')}: {quote!r}")


def validate_record(row, item, prompt, result):
    case_id = item["item_id"] + "__" + prompt["prompt_id"]
    if row.get("case_id") != case_id or row.get("verdict") not in VERDICTS:
        raise ValueError("Invalid case identity or verdict")
    if row.get("confidence") not in {"high", "medium", "low"}:
        raise ValueError("Confidence must be explicit")
    for key in ("summary", "independent_check", "control_notes"):
        if not isinstance(row.get(key), str) or not row[key].strip():
            raise ValueError(f"Missing substantive {key}")
    if not isinstance(row.get("material_checks"), list):
        raise ValueError("Missing material inspection record")
    criteria = row.get("criteria")
    if not isinstance(criteria, list):
        raise ValueError("Missing criterion review")
    unsupported = result["status"] == "unsupported_input_not_scored"
    if unsupported:
        if row["verdict"] != "not_measured" or criteria:
            raise ValueError("Unsupported input must remain unmeasured")
    else:
        if row["verdict"] == "not_measured":
            raise ValueError("A generated response cannot silently become unmeasured")
        expected = {c["criterion_id"]: c for c in criteria_for_prompt(item, prompt["prompt_id"])}
        if len(criteria) != len(expected) or {c.get("criterion_id") for c in criteria} != set(expected):
            raise ValueError("Review must cover every applicable criterion exactly once")
        for criterion in criteria:
            if criterion.get("assessment") not in ASSESSMENTS:
                raise ValueError("Invalid criterion assessment")
            if not isinstance(criterion.get("reason"), str) or not criterion["reason"].strip():
                raise ValueError("Each criterion needs an evidence-based rationale")
            validate_evidence(criterion.get("evidence"), result)
            if criterion["assessment"] == "met" and not criterion["evidence"]:
                raise ValueError("Met criterion needs actual output or environment evidence")
        continuous = item.get("scoring_type") == "continuous"
        if continuous != row["verdict"].startswith("continuous_") and row["verdict"] != "disputed":
            raise ValueError("Continuous metrics must not become binary accuracy")
        obligations = row.get("task_obligation_checks", [])
        if not isinstance(obligations, list):
            raise ValueError("Task obligations must be an array")
        public_texts = [prompt["user_prompt"]]
        for turn in result.get("transcript", []):
            for message in turn.get("messages", []):
                if message.get("role") != "user":
                    continue
                content = message.get("content", "")
                public_texts += [content] if isinstance(content, str) else [part["text"] for part in content if part.get("type") == "text"]
        for obligation in obligations:
            basis = obligation.get("task_basis")
            if not isinstance(basis, str) or not basis.strip() or not any(basis in text for text in public_texts):
                raise ValueError("Additional obligation must quote an actual public task requirement")
            if not obligation.get("check_id") or obligation.get("assessment") not in ASSESSMENTS or not obligation.get("reason"):
                raise ValueError("Malformed explicit task obligation")
            validate_evidence(obligation.get("evidence"), result)
            if not obligation["evidence"]:
                raise ValueError("Additional task obligation needs actual output evidence")
        required = [c for c in criteria if expected[c["criterion_id"]]["required"]] + obligations
        if row["verdict"] == "pass" and any(c["assessment"] != "met" for c in required):
            raise ValueError("Pass contradicts required criterion review")
        if row["verdict"] == "fail" and not any(c["assessment"] == "not_met" for c in required):
            raise ValueError("Failure needs an unmet required criterion")
        final_check = result.get("artifact_checks", [])[-1] if result.get("artifact_checks") else {}
        if row["verdict"] == "pass" and (final_check.get("passed") is False or result.get("environment_completed") is False):
            raise ValueError("Pass conflicts with actual environment outcome; adjudicate explicitly as disputed")
    if not isinstance(row.get("issues"), list):
        raise ValueError("Missing issue list")
    for issue in row["issues"]:
        if issue.get("kind") not in ISSUE_TYPES or not isinstance(issue.get("description"), str) or not issue["description"].strip():
            raise ValueError("Invalid issue")
        validate_evidence(issue.get("evidence"), result)


def recover_initial_judge(score, case_dir, item, result):
    """Read-only format normalization; keep every attempt and reject conflicts."""
    if score.get("status") != "judge_invalid_not_scored":
        return {"verdict": score.get("verdict"), "basis": "original", "attempts": []}
    attempts = []
    for path in sorted((case_dir / "judging/calls/cases").glob("*/result.json")):
        raw = json.loads(path.read_text())
        if raw.get("status") != "generated":
            continue
        attempt = {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}
        try:
            parsed = parse_object(raw["response"])
            attempt["removed_false_error_entries"] = sum(e.get("occurred") is False for e in parsed.get("critical_errors", []))
            parsed["critical_errors"] = [e for e in parsed.get("critical_errors", []) if e.get("occurred") is not False]
            judgment = validate_judgment(json.dumps(parsed, ensure_ascii=False), item, result, result["prompt_id"])
            attempt["verdict"] = judgment["verdict"]
        except (ValueError, KeyError, TypeError) as error:
            attempt["validation_error"] = str(error)
        attempts.append(attempt)
    verdicts = {a["verdict"] for a in attempts if "verdict" in a}
    return {"verdict": next(iter(verdicts)) if len(verdicts) == 1 else None,
            "basis": "read_only_false_error_entries_removed" if len(verdicts) == 1 else "unresolved",
            "attempts": attempts}


def ratio(counts):
    denominator = counts.get("pass", 0) + counts.get("fail", 0)
    return {"pass": counts.get("pass", 0), "fail": counts.get("fail", 0), "denominator": denominator,
            "fraction": counts.get("pass", 0) / denominator if denominator else None}


def link(target, output):
    return os.path.relpath(target, output)


def build(run=RUN, source=SOURCE, output=OUTPUT, check=False, validate_only=False, allow_partial=False):
    batch = run.parent / "source_snapshot/private/edu_last_exam_full_coverage_v1"
    manifest = json.loads((run / "run_manifest.json").read_text())
    items = {i["item_id"]: i for i in jsonl(batch / "items.jsonl")}
    tasks = {i["item_id"] + "__" + p["prompt_id"]: (i, p) for i in items.values() for p in i["prompts"]}
    selected = set(manifest["selected_cases"])
    if selected != set(tasks):
        raise ValueError("Full audit requires the complete frozen batch")
    scores = {x["case_id"]: x for x in jsonl(run / "scores.jsonl")}
    rows, sources = {}, {}
    for path in sorted(source.glob("part_*.json")):
        sources[str(path.relative_to(ROOT))] = sha(path)
        records = json.loads(path.read_text())
        if not isinstance(records, list):
            raise ValueError(f"Expected review array: {path}")
        for row in records:
            case = row["case_id"]
            if case in rows or case not in tasks:
                raise ValueError(f"Duplicate or unknown case: {case}")
            rows[case] = {**row, "review_source": str(path.relative_to(ROOT))}
    missing = sorted(selected - set(rows))
    if missing and not allow_partial:
        raise ValueError(f"Incomplete full review ({len(rows)}/{len(selected)}): {missing}")
    enriched = []
    for case in sorted(rows):
        item, prompt = tasks[case]
        result_path = run / "cases" / case / "result.json"
        result = json.loads(result_path.read_text())
        row = rows[case]
        try:
            validate_record(row, item, prompt, result)
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError(f"{case}: {error}") from error
        initial = scores[case]
        recovered = recover_initial_judge(initial, result_path.parent, item, result)
        inspection_paths = [result_path.parent / "input" / name for name in prompt["assets"]]
        for folder in ("artifacts", "workspace"):
            inspection_paths += [p for p in (result_path.parent / folder).rglob("*") if p.is_file() and p.suffix.lower() in {".png", ".svg", ".html", ".pdf", ".pptx", ".json"}]
        inspection_paths += [p for p in (result_path.parent / "persistent_memory.json",) if p.is_file()]
        if any(not p.is_file() for p in inspection_paths):
            raise ValueError(f"Missing actual inspection asset: {case}")
        enriched.append({**row, "direction_id": item["direction_id"], "title": item["title"],
                         "measurement_claim": item["measurement_claim"], "unmeasured_subclaims": item["unmeasured_subclaims"],
                         "prediction_status": result["status"], "result_sha256": sha(result_path),
                         "frozen_item_sha256": hashlib.sha256(packed(item).encode()).hexdigest(),
                         "original_judge": {"status": initial["status"], "verdict": initial.get("verdict")},
                         "normalized_initial_judge": recovered,
                         "inspection_assets": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in sorted(set(inspection_paths))],
                         "changed_from_initial": recovered["verdict"] in {"pass", "fail"} and row["verdict"] != recovered["verdict"],
                         "result_path": str(result_path.relative_to(ROOT))})
    counts = dict(Counter(r["verdict"] for r in enriched))
    grouped = defaultdict(list)
    for row in enriched:
        grouped[row["direction_id"]].append(row)
    directions = {}
    for direction, group in sorted(grouped.items()):
        count = dict(Counter(r["verdict"] for r in group))
        directions[direction] = {"cases": len(group), "counts": count, "binary_descriptive_tally": ratio(count),
                                 "titles": sorted({r["title"] for r in group}),
                                 "case_ids": [r["case_id"] for r in group]}
    initial_counts = dict(Counter(r["normalized_initial_judge"]["verdict"] for r in enriched if r["normalized_initial_judge"]["verdict"] in {"pass", "fail"}))
    transitions = defaultdict(Counter)
    for row in enriched:
        if row["verdict"] in {"pass", "fail", "disputed"}:
            transitions[row["normalized_initial_judge"]["verdict"] or "unscored"][row["verdict"]] += 1
    summary = {"review_type": "Codex_second_model_author_associated_full_review", "tested_model": manifest["model"],
               "independent_teacher_review": "pending", "benchmark_frozen": False,
               "status": "full_review_complete" if not missing else "partial_review",
               "selected_versions": len(selected), "reviewed_versions": len(enriched),
               "base_cases": len(items), "directions_reviewed": len(directions),
               "reviewed_model_responses": sum(r["prediction_status"] == "generated" for r in enriched),
               "missing_versions": missing, "counts": counts, "directions": directions,
               "batch_descriptive_binary_tally": ratio(counts),
               "tally_boundary": "Unweighted count of determinate binary task versions only; not a unified construct score, independent-item estimate, or real-classroom accuracy.",
               "normalized_initial_binary_tally": ratio(initial_counts),
               "original_judge_status_counts": dict(Counter(r["original_judge"]["status"] for r in enriched)),
               "initial_to_review_binary_transitions": {key: dict(value) for key, value in sorted(transitions.items())},
               "changed_from_initial": [r["case_id"] for r in enriched if r["changed_from_initial"]],
               "filled_initial_score_gaps": [r["case_id"] for r in enriched if r["original_judge"]["status"] in {"judge_api_error", "judge_invalid_not_scored"}],
               "review_sources_sha256": sources,
               "auxiliary_review_artifacts_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sorted(source.rglob("*")) if p.is_file() and p.name not in {".DS_Store"} and str(p.relative_to(ROOT)) not in sources},
               "original_scores_sha256": sha(run / "scores.jsonl"), "original_predictions_sha256": sha(run / "predictions.jsonl"),
               "frozen_items_sha256": sha(batch / "items.jsonl"), "run_manifest_sha256": sha(run / "run_manifest.json"),
               "review_protocol_sha256": sha(ROOT / "data/edu_last_exam_full_coverage_v1/codex_review_protocol_v1.md")}
    md = render_markdown(enriched, summary, run, output)
    page = render_html(enriched, summary, run, output)
    exports = {output / "summary.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
               output / "case_reviews.jsonl": ''.join(json.dumps(r, ensure_ascii=False) + "\n" for r in enriched),
               output / "review.md": md, output / "review.html": page}
    if check:
        for path, contents in exports.items():
            if not path.is_file() or path.read_text() != contents:
                raise ValueError(f"Missing or stale generated report: {path}")
    elif not validate_only:
        output.mkdir(parents=True, exist_ok=True)
        for path, contents in exports.items():
            path.write_text(contents, encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("status", "reviewed_versions", "reviewed_model_responses", "counts", "batch_descriptive_binary_tally", "changed_from_initial")}, ensure_ascii=False))
    return summary


def render_markdown(rows, summary, run, output):
    tally = summary["batch_descriptive_binary_tally"]
    rate = f"{tally['fraction']:.1%}" if tally["fraction"] is not None else "未计算"
    lines = ["# GLM-5.3-Flash 全量 Codex 复核", "", "复核冻结题面、完整回答与实际环境。Codex曾参与候选编写；本报告不是独立教师人审或冻结benchmark结论。", "",
             f"已复核 {summary['reviewed_versions']}/{summary['selected_versions']} 个版本，其中 {summary['reviewed_model_responses']} 份有效模型回答。", "",
             "；".join(f"{label}：{summary['counts'].get(verdict, 0)}" for verdict, label in LABELS.items()) + "。", "",
             f"本批二元任务描述性计数：{tally['pass']}/{tally['denominator']} 通过（{rate}）。争议、连续指标及未测单列；不是统一能力分数或真实课堂总体正确率。", "",
             "初评差异以下表配对展示。原初评的格式异常仅在内存中按协议恢复；未重写原分数。两次有效分母不同，不能直接把两个百分比相减解释为配对降幅。", "",
             "|初评（只读格式恢复后）|复核通过|复核未通过|争议待审|", "|---|---:|---:|---:|"]
    for initial, counts in summary["initial_to_review_binary_transitions"].items():
        lines.append(f"|{LABELS.get(initial, '评分缺口')}|{counts.get('pass',0)}|{counts.get('fail',0)}|{counts.get('disputed',0)}|")
    lines += ["", "## 未通过与争议索引", "", "|版本|复核|具体依据|", "|---|---|---|"]
    for row in rows:
        if row["verdict"] in {"fail", "disputed"}:
            lines.append(f"|{row['case_id']}|{LABELS[row['verdict']]}|{row['summary'].replace('|', ' / ')}|")
    lines += ["", "## 分方向计数", "", "|方向|场景|版本数|通过|未通过|争议|连续有效/无效|未测|", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for direction, data in summary["directions"].items():
        c = data["counts"]
        lines.append(f"|{direction}|{'；'.join(data['titles']).replace('|', ' / ')}|{data['cases']}|{c.get('pass',0)}|{c.get('fail',0)}|{c.get('disputed',0)}|{c.get('continuous_valid',0)}/{c.get('continuous_invalid',0)}|{c.get('not_measured',0)}|")
    for row in rows:
        lines += ["", f"## {row['case_id']} · {LABELS[row['verdict']]}", "", row["summary"], "", "独立核验：" + row["independent_check"], "", "对照：" + row["control_notes"], "",
                  f"原初评：{row['original_judge']}；只读格式恢复后：{row['normalized_initial_judge']['verdict']}；复核信心：{row['confidence']}。", "",
                  f"[原始回包与轨迹]({link(ROOT / row['result_path'], output)}) · [源复核记录]({link(ROOT / row['review_source'], output)})", ""]
        for criterion in row["criteria"]:
            lines += [f"- **{criterion['criterion_id']} / {criterion['assessment']}**：{criterion['reason']}"]
            for evidence in criterion["evidence"]:
                lines.append("  - " + json.dumps(evidence, ensure_ascii=False))
        for issue in row["issues"]:
            lines.append(f"- **{issue['kind']}**：{issue['description']}")
        for obligation in row.get("task_obligation_checks", []):
            lines += [f"- **明确任务义务 {obligation['check_id']} / {obligation['assessment']}**：{obligation['reason']}",
                      "  - 公开依据：" + obligation["task_basis"]]
            lines += ["  - " + json.dumps(e, ensure_ascii=False) for e in obligation["evidence"]]
        if row["inspection_assets"]:
            lines += ["", "实际输入与产物：" + " · ".join(f"[{Path(a['path']).name}]({link(ROOT / a['path'], output)})" for a in row["inspection_assets"])]
        lines += ["", "材料验收：" + "；".join(row["material_checks"]), "", "未测范围：" + "；".join(row["unmeasured_subclaims"])]
    return '\n'.join(lines) + "\n"


def render_html(rows, summary, run, output):
    esc = lambda value: html.escape(str(value))
    tally = summary["batch_descriptive_binary_tally"]
    rate = f"{tally['fraction']:.1%}" if tally["fraction"] is not None else "未计算"
    body = ["<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>GLM-5.3-Flash 全量复核</title>",
            "<style>body{font:16px/1.7 system-ui,sans-serif;max-width:1200px;margin:30px auto;padding:0 20px;color:#192d38;background:#fafbfc}h1,h2{line-height:1.3}table{border-collapse:collapse;width:100%;margin:20px 0;background:white}th,td{border:1px solid #d4dce2;padding:8px;text-align:left}details{background:white;border:1px solid #d4dce2;border-left:5px solid #80939e;padding:14px;margin:16px 0;border-radius:6px}details[data-verdict=fail]{border-left-color:#bc3838}details[data-verdict=pass]{border-left-color:#258554}details[data-verdict=disputed]{border-left-color:#ba8500}summary{cursor:pointer;font-weight:650}blockquote{white-space:pre-wrap;word-break:break-word;background:#f5f7f8;border-left:3px solid #a3b8c3;padding:10px 15px;margin:10px 0;font-size:14px}small,.muted{color:#536574}.card{background:#edf4f8;padding:18px;border-radius:8px}input,select{font:inherit;padding:7px;margin:4px}a{color:#15628d}code{word-break:break-word}.hidden{display:none}li{margin:6px 0}</style>",
            "<h1>GLM-5.3-Flash 全量 Codex 复核</h1><p>依据冻结题面、完整回答与实际环境重新审阅。Codex参与过候选编写；本次不是独立教师审核或正式冻结benchmark结论。</p>",
            f"<div class='card'>复核 <strong>{summary['reviewed_versions']}/{summary['selected_versions']}</strong> 个版本，含 <strong>{summary['reviewed_model_responses']}</strong> 份有效回答。<br>本批二元任务描述性计数：<strong>{tally['pass']}/{tally['denominator']}（{rate}）</strong>。争议、连续指标及未测不纳入该分母；不是统一能力分数或真实课堂总体正确率。</div>",
            "<p>" + "；".join(f"{label}：<strong>{summary['counts'].get(verdict, 0)}</strong>" for verdict, label in LABELS.items()) + "。</p>",
            f"<p><a href='summary.json'>机器可读汇总</a> · <a href='case_reviews.jsonl'>逐题复核</a> · <a href='review.md'>Markdown</a> · <a href='{esc(link(run / 'report.html', output))}'>原始运行报告（保留未改）</a></p>",
            "<h2>与初评的配对差异</h2><p>初评格式异常仅在内存中按协议恢复，原始分数保留。两次有效分母不同，不把百分比差值解释成配对降幅。</p><table><tr><th>初评（只读格式恢复后）</th><th>复核通过</th><th>复核未通过</th><th>争议待审</th></tr>"]
    for initial, counts in summary["initial_to_review_binary_transitions"].items():
        body.append(f"<tr><td>{LABELS.get(initial, '评分缺口')}</td><td>{counts.get('pass',0)}</td><td>{counts.get('fail',0)}</td><td>{counts.get('disputed',0)}</td></tr>")
    body += ["</table><h2>未通过与争议索引</h2><table><tr><th>版本</th><th>复核</th><th>具体依据</th></tr>"]
    for row in rows:
        if row["verdict"] in {"fail", "disputed"}:
            body.append(f"<tr><td><a href='#{esc(row['case_id'])}'>{esc(row['case_id'])}</a></td><td>{LABELS[row['verdict']]}</td><td>{esc(row['summary'])}</td></tr>")
    body += ["</table><h2>按方向查看</h2><table><tr><th>方向</th><th>场景</th><th>版本</th><th>通过</th><th>未通过</th><th>争议</th><th>连续有效/无效</th><th>未测</th></tr>"]
    for direction, data in summary["directions"].items():
        c = data["counts"]
        body.append(f"<tr><td>{direction}</td><td>{esc('；'.join(data['titles']))}</td><td>{data['cases']}</td><td>{c.get('pass',0)}</td><td>{c.get('fail',0)}</td><td>{c.get('disputed',0)}</td><td>{c.get('continuous_valid',0)}/{c.get('continuous_invalid',0)}</td><td>{c.get('not_measured',0)}</td></tr>")
    body += ["</table><h2>逐份依据</h2><label>筛选 <select id='verdict'><option value=''>全部判定</option>", *[f"<option value='{v}'>{label}</option>" for v, label in LABELS.items()], "</select></label><input id='query' aria-label='搜索题号、场景与问题' placeholder='搜索题号、场景与问题'><span id='visible'></span>"]
    for row in rows:
        body += [f"<details class='case' data-verdict='{row['verdict']}' id='{esc(row['case_id'])}'><summary>{esc(row['case_id'])} · {LABELS[row['verdict']]} · {esc(row['title'])}</summary>",
                 f"<p>{esc(row['summary'])}</p><p><strong>独立核验：</strong>{esc(row['independent_check'])}</p><p><strong>对照：</strong>{esc(row['control_notes'])}</p>",
                 f"<p class='muted'>原初评：{esc(row['original_judge'])}；只读格式恢复后：{esc(row['normalized_initial_judge']['verdict'])}；复核信心：{esc(row['confidence'])}。</p>",
                 f"<p><a href='{esc(link(ROOT / row['result_path'], output))}'>原始回包与轨迹</a> · <a href='{esc(link(ROOT / row['review_source'], output))}'>源复核记录</a></p>"]
        for criterion in row["criteria"]:
            body.append(f"<p><strong>{esc(criterion['criterion_id'])} / {esc(criterion['assessment'])}</strong>：{esc(criterion['reason'])}</p>")
            for evidence in criterion["evidence"]:
                body.append(f"<blockquote><small>{esc(evidence['kind'])} {evidence.get('turn', evidence.get('index', ''))}</small><br>{esc(evidence['quote'])}</blockquote>")
        for issue in row["issues"]:
            body.append(f"<p><strong>{esc(issue['kind'])}</strong>：{esc(issue['description'])}</p>")
            for evidence in issue["evidence"]:
                body.append(f"<blockquote>{esc(evidence['quote'])}</blockquote>")
        for obligation in row.get("task_obligation_checks", []):
            body.append(f"<p><strong>明确任务义务 {esc(obligation['check_id'])} / {esc(obligation['assessment'])}</strong>：{esc(obligation['reason'])}<br>公开依据：{esc(obligation['task_basis'])}</p>")
            for evidence in obligation["evidence"]:
                body.append(f"<blockquote>{esc(evidence['quote'])}</blockquote>")
        if row["inspection_assets"]:
            body.append("<p><strong>实际输入与产物：</strong>" + " · ".join(f"<a href='{esc(link(ROOT / a['path'], output))}'>{esc(Path(a['path']).name)}</a>" for a in row["inspection_assets"]) + "</p>")
        body += [f"<p><strong>材料验收：</strong>{esc('；'.join(row['material_checks']))}</p><p class='muted'>测量范围：{esc(row['measurement_claim'])}<br>未测：{esc('；'.join(row['unmeasured_subclaims']))}</p></details>"]
    body.append("<script>const cards=[...document.querySelectorAll('.case')],q=document.querySelector('#query'),v=document.querySelector('#verdict');function filter(){let n=0;for(const c of cards){const show=(!v.value||c.dataset.verdict===v.value)&&c.textContent.toLowerCase().includes(q.value.toLowerCase());c.classList.toggle('hidden',!show);if(show)n++;}document.querySelector('#visible').textContent='显示 '+n+' 个版本';}q.addEventListener('input',filter);v.addEventListener('change',filter);filter();</script></html>")
    return ''.join(body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=RUN)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--allow-partial", action="store_true", help="Development only; report explicitly partial")
    args = parser.parse_args()
    build(args.run.resolve(), args.source.resolve(), args.output.resolve(), args.check, args.validate_only, args.allow_partial)


if __name__ == "__main__":
    main()
