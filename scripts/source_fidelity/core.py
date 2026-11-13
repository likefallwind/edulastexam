"""Validate and execute source-preserving tasks without a universal scoring wrapper."""
from __future__ import annotations

import base64
import copy
import hashlib
import html
import importlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BATCH_REL = Path("private/edu_last_exam_source_fidelity_v1")
AUDIT_REL = Path("data/edu_last_exam_source_fidelity_v1")
MODES = {"single_turn", "scripted", "adapter"}
SCORE_MODES = {"exact", "numeric", "native_adapter", "native_judge", "manual_pending"}


def digest(value):
    if not isinstance(value, bytes):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(value).hexdigest()


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def local_path(root, value):
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or "\\" in value:
        raise ValueError(f"Expected repository-relative file: {value}")
    path = (Path(root) / relative).resolve(strict=True)
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
        raise ValueError(f"Asset escapes source snapshot: {value}")
    if any(part.startswith(".env") for part in relative.parts):
        raise ValueError("Environment files cannot be evaluation assets")
    return path


def module(name):
    if not re.fullmatch(r"scripts\.source_fidelity\.group_\d{2}_\d{2}", name):
        raise ValueError(f"Unregistered adapter: {name}")
    return importlib.import_module(name)


def check_parameters(parameters):
    reserved = {"model", "messages", "stream", "stream_options", "api_key", "tools", "tool_choice"}
    if not isinstance(parameters, dict) or reserved.intersection(parameters):
        raise ValueError("Prediction parameters cannot override identity, credentials, or tool protocol")
    if {"max_tokens", "max_completion_tokens", "max_output_tokens"}.intersection(parameters):
        raise ValueError("No token ceiling is authorized for GLM-5.3-Flash")


def prepare_messages(task, root):
    messages = copy.deepcopy(task["prediction"]["messages"])
    allowed = {a["path"] for a in task.get("assets", []) if a["role"] == "prediction"}
    for message in messages:
        if message["role"] not in {"system", "user", "assistant"}:
            raise ValueError("Unrecognized original message role")
        content = message["content"]
        if isinstance(content, str):
            continue
        if not isinstance(content, list):
            raise ValueError("Message content must be original text or multimodal parts")
        for part in content:
            if part.get("type") in {"image_path", "video_path"}:
                value = part["path"]
                if value not in allowed:
                    raise ValueError("Prediction media must be explicitly public; reference assets cannot be delivered")
                path = local_path(root, value)
                mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".mp4": "video/mp4"}.get(path.suffix.lower())
                if mime is None:
                    raise ValueError(f"Unsupported media type: {path.suffix}")
                key = "image_url" if part["type"] == "image_path" else "video_url"
                part.clear()
                part.update(type=key, **{key: {"url": f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()}})
            elif part.get("type") != "text":
                raise ValueError("Unknown/unverified media input; do not substitute transcripts")
    return messages


def validate_task(task, root=ROOT):
    ident = task["case_id"]
    if not re.fullmatch(r"ELE-SF-\d{2}-[A-Za-z0-9_-]+", ident):
        raise ValueError(f"Invalid case identity: {ident}")
    if not task.get("direction_ids") or any(not re.fullmatch(r"(?:0[1-9]|[12]\d|3[0-7])", d) for d in task["direction_ids"]):
        raise ValueError("Invalid scenario attribution")
    if task["origin"] not in {"original_task", "mechanism_authored"}:
        raise ValueError("Keep original tasks and author-constructed tasks separate")
    for key in ("title", "selection_reason", "source", "fidelity", "review"):
        if not task.get(key):
            raise ValueError(f"Missing {key}: {ident}")
    for key in ("task_condition", "input", "output", "scoring", "environment", "scope"):
        if not task["fidelity"].get(key):
            raise ValueError(f"Missing fidelity dimension {key}: {ident}")
    if not isinstance(task["fidelity"].get("deviations"), list):
        raise ValueError("Explicit protocol deviations required, including an empty array when none")
    check_parameters(task["prediction"].get("parameters", {}))
    for asset in task.get("assets", []):
        if asset["role"] not in {"prediction", "scoring", "provenance", "runtime"}:
            raise ValueError("Asset visibility must be explicit")
        if digest(local_path(root, asset["path"]).read_bytes()) != asset["sha256"]:
            raise ValueError(f"Source asset hash mismatch: {asset['path']}")
    interaction = task["prediction"]["interaction"]
    if interaction["mode"] not in MODES:
        raise ValueError("Unsupported interaction protocol")
    if interaction["mode"] == "scripted" and not interaction.get("followups"):
        raise ValueError("Scripted protocol needs original follow-ups")
    if not task["prediction"].get("messages") and interaction["mode"] != "adapter":
        raise ValueError("Original messages must be present")
    prepare_messages(task, root)
    scoring = task["scoring"]
    if scoring["mode"] not in SCORE_MODES or not scoring.get("native_metric"):
        raise ValueError("Original metric and scoring protocol are required")
    if scoring["mode"] == "native_judge" and (not scoring.get("required_model") or "{{MODEL_RESPONSE}}" not in json.dumps(scoring.get("messages", []))):
        raise ValueError("Native judge identity and response insertion point must be retained")
    if scoring["mode"] == "manual_pending" and not scoring.get("reason"):
        raise ValueError("Missing original scoring must explain its blocker")
    adapters = {cfg["module"] for cfg in (interaction, scoring) if cfg.get("module")}
    checks = []
    for name in sorted(adapters):
        adapter = module(name)
        if not hasattr(adapter, "validate"):
            raise ValueError(f"Adapter lacks offline validation: {name}")
        result = adapter.validate(task, root)
        if result.get("passed") is not True:
            raise ValueError(f"Adapter offline checks failed for {ident}: {result}")
        checks.append({"adapter": name, **result})
    return {"case_id": ident, "passed": True, "checks": checks}


def load(root=ROOT, require_all=True, validation_case_ids=None):
    root = Path(root)
    audits = [json.loads(path.read_text()) for path in sorted((root / AUDIT_REL / "directions").glob("[0-9][0-9].json"))]
    index_file = root / AUDIT_REL / "direction_index.json"
    if index_file.exists():
        index = {row["direction_id"]: row for row in json.loads(index_file.read_text())["directions"]}
        for audit in audits:
            audit["original_direction_scope"] = index[audit["direction_id"]]["original_title"]
    if require_all and {row["direction_id"] for row in audits} != {f"{n:02}" for n in range(1, 38)}:
        raise ValueError("All 37 directions must remain in the audit, including blocked directions")
    tasks = [json.loads(path.read_text()) for path in sorted((root / BATCH_REL / "authored").glob("*.json"))]
    if len({t["case_id"] for t in tasks}) != len(tasks):
        raise ValueError("Duplicate task identity")
    mapping = {t["case_id"]: t for t in tasks}
    for audit in audits:
        for key in ("sources", "research_failure", "original_task", "decision", "condition_mapping", "search_log"):
            if not audit.get(key):
                raise ValueError(f"Direction {audit['direction_id']} lacks original-source review field {key}")
        for case in audit.get("task_ids", []):
            if case not in mapping or audit["direction_id"] not in mapping[case]["direction_ids"]:
                raise ValueError(f"Direction/task attribution mismatch: {case}")
        if audit["status"].startswith("ready_") and not audit.get("task_ids"):
            raise ValueError("A ready direction requires actual task files")
    if require_all:
        for task in tasks:
            if not any(task["case_id"] in a.get("task_ids", []) for a in audits):
                raise ValueError(f"Task missing from direction audit: {task['case_id']}")
    validation_tasks = tasks
    if validation_case_ids is not None:
        requested = set(validation_case_ids)
        validation_tasks = [task for task in tasks if task["case_id"] in requested]
        if len(validation_tasks) != len(requested):
            raise ValueError("Unknown case ID requested for adapter validation")
    validations = [validate_task(task, root) for task in validation_tasks]
    return audits, tasks, validations


def predict(task, call, directory, root=ROOT):
    if task.get("execution", {}).get("eligible") is False:
        return {"status": "original_condition_unavailable_not_measured", "reason": task["execution"]["reason"], "transcript": []}
    cfg = task["prediction"]["interaction"]
    if cfg["mode"] == "adapter":
        return module(cfg["module"]).run(task, call, directory, root)
    messages = prepare_messages(task, root)
    transcript = []
    for number, followup in enumerate([None, *cfg.get("followups", [])]):
        if followup is not None:
            messages.append(followup if isinstance(followup, dict) else {"role": "user", "content": followup})
        answer = call(messages, purpose="prediction", parameters=task["prediction"].get("parameters", {}))
        transcript.append({"turn": number, "messages": copy.deepcopy(messages), "status": answer["status"], "response": answer.get("response", "")})
        if answer["status"] != "generated":
            return {"status": answer["status"], "response": answer.get("response", ""), "transcript": transcript}
        messages.append({"role": "assistant", "content": answer["response"]})
    return {"status": "generated", "response": transcript[-1]["response"], "transcript": transcript}


def score(task, result, call, directory, root=ROOT, model="GLM-5.3-Flash"):
    cfg = task["scoring"]
    if result["status"] != "generated":
        return {"status": "not_scored", "reason": result["status"]}
    if cfg["mode"] == "native_adapter":
        return module(cfg["module"]).score(task, result, call, directory, root)
    if cfg["mode"] == "manual_pending":
        return {"status": "native_score_pending", "reason": cfg["reason"], "native_metric": cfg["native_metric"]}
    if cfg["mode"] == "native_judge":
        available = getattr(call, "supports_model", lambda value: value.casefold() == model.casefold())
        if not available(cfg["required_model"]):
            return {"status": "native_score_pending", "reason": "Original judge model unavailable in this authorized GLM-only run", "required_model": cfg["required_model"], "native_metric": cfg["native_metric"]}
        messages = copy.deepcopy(cfg["messages"])
        for message in messages:
            message["content"] = message["content"].replace("{{MODEL_RESPONSE}}", result["response"])
        judged = call(messages, purpose="judge", parameters=cfg.get("parameters", {}), model=cfg["required_model"])
        return {"status": "native_judge_parse_pending" if judged["status"] == "generated" else "judge_api_error", "native_metric": cfg["native_metric"], "judge_response": judged.get("response", "")}
    answer = result["response"].strip()
    if cfg.get("pattern"):
        match = re.search(cfg["pattern"], answer, flags=re.S)
        if not match:
            return {"status": "native_output_unparsed", "native_metric": cfg["native_metric"]}
        answer = match.group(1)
    if cfg["mode"] == "numeric":
        try:
            answer = float(answer)
        except ValueError:
            return {"status": "native_output_unparsed", "native_metric": cfg["native_metric"]}
        correct = abs(answer - float(cfg["expected"])) <= cfg.get("tolerance", 0)
    else:
        expected = str(cfg["expected"])
        correct = answer == expected if cfg.get("case_sensitive", True) else answer.casefold() == expected.casefold()
    return {"status": "scored_native", "native_metric": cfg["native_metric"], "metrics": {cfg["native_metric"]: float(correct)}, "extracted": answer}


def report(audits, tasks, summary):
    esc = lambda value: html.escape(str(value))
    body = ["<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>原始任务保真核验</title><style>body{font:16px/1.7 system-ui;max-width:1250px;margin:30px auto;padding:0 20px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd5dc;padding:9px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{border:1px solid #ccd5dc;padding:16px;margin:12px 0}a{color:#176592}</style><h1>37方向：原始任务、失败条件与复测</h1><p>原题子集与按机制自建分别记录。保留原生评分；原评分模型或环境缺失不算模型答错。本轮不是原论文完整复现或冻结benchmark结论。</p><pre>", esc(json.dumps(summary, ensure_ascii=False, indent=2)), "</pre><table><tr><th>方向</th><th>场景</th><th>来源路线/状态</th><th>任务数</th><th>决定依据</th></tr>"]
    for audit in audits:
        body.append(f"<tr><td>{esc(audit['direction_id'])}</td><td><strong>{esc(audit.get('original_direction_scope', audit['title']))}</strong><br>本轮视图：{esc(audit['title'])}</td><td>{esc(audit['decision']['route'])}<br>{esc(audit['status'])}</td><td>{len(audit.get('task_ids', []))}</td><td>{esc(audit['decision']['rationale'])}<br>边界：{esc('；'.join(audit['decision'].get('limitations', [])))}</td></tr>")
    body.append("</table><h2>原始来源与条件映射</h2>")
    for audit in audits:
        body.append(f"<details><summary>{esc(audit['direction_id'])} {esc(audit['title'])}</summary><pre>{esc(json.dumps(audit, ensure_ascii=False, indent=2))}</pre></details>")
    body.append("<h2>实际投递任务与评分条件</h2>")
    for task in tasks:
        body.append(f"<details><summary>{esc(task['case_id'])} · {esc(task['title'])} · {esc(task['origin'])}</summary><pre>{esc(json.dumps(task, ensure_ascii=False, indent=2))}</pre></details>")
    return ''.join(body) + "</html>"
