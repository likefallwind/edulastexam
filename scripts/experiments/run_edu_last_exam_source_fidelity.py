#!/usr/bin/env python3
"""Run original-source tasks with at most four API calls in flight, then native scoring."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import html
import json
import os
from pathlib import Path
import sys
import threading
import traceback
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.source_fidelity import core
from scripts.experiments import run_edu_last_exam_challenge_v2 as transport


def now():
    return datetime.now(timezone.utc).isoformat()


def code_identity(root):
    """Include imported transport code when validating a resumed run."""
    root = Path(root)
    files = [root / "scripts/experiments/run_edu_last_exam_source_fidelity.py",
             root / "scripts/experiments/run_edu_last_exam_challenge_v2.py",
             root / "scripts/eval/minimax_client.py",
             *sorted((root / "scripts/source_fidelity").rglob("*.py"))]
    return {str(path.relative_to(root)): core.digest(path.read_bytes()) for path in files}


class Caller:
    def __init__(self, task, directory, args, key, gate):
        self.task, self.directory, self.args, self.key, self.gate = task, directory, args, key, gate
        self.counter = Counter()
        self.lock = threading.Lock()

    def supports_model(self, model):
        return model.casefold() == self.args.model.casefold() or (
            model.casefold() == "minimax-m3" and bool(os.environ.get("MINIMAX_API_KEY")))

    def __call__(self, messages, purpose="prediction", parameters=None, model=None):
        if purpose not in {"prediction", "extraction", "judge", "student"}:
            raise ValueError("API role must be explicitly recorded")
        parameters = parameters or {}
        core.check_parameters(parameters)
        requested_model = model or self.args.model
        call_args, call_key = self.args, self.key
        if requested_model.casefold() != self.args.model.casefold():
            declared = self.task["scoring"].get("required_model")
            if purpose not in {"judge", "extraction"} or declared != requested_model:
                raise ValueError("Secondary models may only fulfill an explicitly declared original scoring role")
            if not self.supports_model(requested_model):
                raise ValueError("Original scoring model is unavailable; do not substitute another model")
            call_args = SimpleNamespace(**{**vars(self.args), "model": requested_model,
                "endpoint": "https://api.minimaxi.com/v1/text/chatcompletion_v2"})
            call_key = os.environ["MINIMAX_API_KEY"]
        with self.lock:
            index = self.counter[purpose]
            self.counter[purpose] += 1
        ident = f"{purpose}_{index:03}"
        payload = {"model": requested_model, "messages": messages, "stream": True,
                   "stream_options": {"include_usage": True}, **parameters}
        request = {"case_id": ident, "item_id": self.task["case_id"], "prompt_id": purpose,
                   "interaction_mode": self.task["prediction"]["interaction"]["mode"], "payload": payload,
                   "endpoint": call_args.endpoint,
                   "request_sha256": core.digest({"endpoint": call_args.endpoint, "payload": payload})}
        output = self.directory / "calls"
        folder = output / "cases" / ident
        path = folder / "request.json"
        if path.exists() and json.loads(path.read_text())["request_sha256"] != request["request_sha256"]:
            raise ValueError("Call identity changed; choose an isolated new run")
        core.write_json(path, request)
        cache = folder / "result.json"
        if cache.exists():
            prior = json.loads(cache.read_text())
            if prior.get("request_sha256") != request["request_sha256"]:
                raise ValueError("Call cache input mismatch")
            if prior["status"] == "generated":
                return prior
        with self.gate:
            result = transport.request_one(request, call_args, call_key, output)
        if result["status"] == "generated" and (not result.get("stream_done_seen") or not result.get("returned_models")):
            result["status"] = "completion_unverified"
            core.write_json(cache, result)
        return result


def execute(task, args, key, gate):
    directory = args.output / "cases" / task["case_id"]
    directory.mkdir(parents=True, exist_ok=True)
    identity = core.digest({"task": task, "model": args.model, "endpoint": args.endpoint})
    path = directory / "result.json"
    caller = Caller(task, directory, args, key, gate)
    if path.exists():
        prior = json.loads(path.read_text())
        if prior.get("request_sha256") != identity:
            raise ValueError("Prediction input changed during resume")
        if prior["status"] == "generated":
            return prior
    try:
        result = core.predict(task, caller, directory, ROOT)
    except Exception as exc:
        message = str(exc).replace(key, "[REDACTED]")
        result = {"status": "environment_error_not_scored", "error": message}
        (directory / "error.txt").write_text(traceback.format_exc().replace(key, "[REDACTED]"))
    result = {"case_id": task["case_id"], "direction_ids": task["direction_ids"], "origin": task["origin"],
              "request_sha256": identity, "model": args.model, "finished_at": now(), **result}
    core.write_json(path, result)
    if result.get("response"):
        (directory / "response.md").write_text(result["response"])
    return result


def evaluate(task, result, args, key, gate):
    directory = args.output / "cases" / task["case_id"] / "scoring"
    identity = core.digest({"task": task, "prediction": result, "model": args.model})
    cache = directory / "score.json"
    if cache.exists():
        previous = json.loads(cache.read_text())
        if previous.get("scoring_identity") != identity:
            raise ValueError("Scoring identity changed during resume")
        if previous.get("status") in {"scored_native", "native_score_pending"}:
            return previous
    try:
        score = core.score(task, result, Caller(task, directory, args, key, gate), directory, ROOT, args.model)
    except Exception as exc:
        score = {"status": "scoring_error_not_scored", "error": str(exc).replace(key, "[REDACTED]")}
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "error.txt").write_text(traceback.format_exc().replace(key, "[REDACTED]"))
    score = {"case_id": task["case_id"], "direction_ids": task["direction_ids"], "scoring_identity": identity, **score}
    core.write_json(cache, score)
    return score


def save(args, audits, tasks, predictions, scores, state, inflight=()):
    summary = {"updated_at": now(), "state": state, "model": args.model, "concurrency": args.concurrency,
               "directions_audited": len(audits), "direction_status_counts": dict(Counter(a["status"] for a in audits)),
               "selected_cases": len(tasks), "prediction_records": len(predictions), "score_records": len(scores),
               "prediction_eligible_cases": sum(t.get("execution", {}).get("eligible") is not False for t in tasks),
               "prediction_status_counts": dict(Counter(x["status"] for x in predictions.values())),
               "score_status_counts": dict(Counter(x["status"] for x in scores.values())), "queued_or_running_cases": list(inflight),
               "pending_predictions": len(tasks) - len(predictions), "pending_scores": len(tasks) - len(scores),
               "cross_direction_total_score": False, "canonical": False, "human_review": "pending"}
    coverage = Counter()
    for scoring in scores.values():
        if scoring["status"] == "scored_native" and not scoring.get("pending_metrics"):
            coverage["complete"] += 1
        elif scoring.get("metrics"):
            coverage["partial"] += 1
        else:
            coverage["pending_or_unmeasured"] += 1
    summary["native_scoring_coverage"] = dict(coverage)
    if state.startswith("complete"):
        aggregates = {}
        for name in sorted({t["scoring"]["module"] for t in tasks if t["scoring"].get("module")}):
            adapter = core.module(name)
            if hasattr(adapter, "aggregate"):
                try:
                    aggregates[name] = adapter.aggregate(list(scores.values()), ROOT)
                except Exception as error:
                    aggregates[name] = {"status": "aggregation_error", "error": str(error)}
        summary["native_within_view_aggregates"] = aggregates
        core.write_json(args.output / "native_metrics.json", aggregates)
    for filename, values in (("predictions.jsonl", predictions), ("scores.jsonl", scores)):
        path = args.output / filename
        temporary = path.with_suffix(".jsonl.tmp")
        temporary.write_text(''.join(json.dumps(values[key], ensure_ascii=False) + "\n" for key in sorted(values)))
        temporary.replace(path)
    core.write_json(args.output / "summary.json", summary)
    esc = lambda x: html.escape(str(x))
    page = ["<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>原始任务复测运行</title><style>body{font:16px/1.7 system-ui;max-width:1250px;margin:30px auto;padding:20px}pre{white-space:pre-wrap}td,th{padding:9px;border:1px solid #ccd5dc}table{border-collapse:collapse}</style><h1>GLM-5.3-Flash · 原始任务复测</h1><p>按原任务指标分别报告；原judge或环境缺失不算答错。只运行已具备输入与协议的任务，其余方向仍列审查缺口。</p><pre>", esc(json.dumps(summary, ensure_ascii=False, indent=2)), "</pre><table><tr><th>任务</th><th>来源</th><th>预测</th><th>原生指标</th><th>评分</th><th>证据</th></tr>"]
    for task in tasks:
        ident = task["case_id"]
        p, s = predictions.get(ident, {}), scores.get(ident, {})
        page.append(f"<tr><td>{esc(ident)} {esc(task['title'])}</td><td>{esc(task['origin'])}</td><td>{esc(p.get('status','pending'))}</td><td>{esc(task['scoring']['native_metric'])}</td><td>{esc(json.dumps(s.get('metrics',s.get('status','pending')),ensure_ascii=False))}</td><td><a href='cases/{ident}/result.json'>完整回答</a> · <a href='cases/{ident}/scoring/score.json'>评分</a></td></tr>")
    page.append("</table></html>")
    (args.output / "report.html").write_text(''.join(page))
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="GLM-5.3-Flash")
    parser.add_argument("--endpoint", default=transport.ENDPOINT)
    parser.add_argument("--api-key-env", default="GLM_API")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.model != "GLM-5.3-Flash" or not 1 <= args.concurrency <= 4:
        parser.error("This run is authorized for GLM-5.3-Flash with concurrency at most four")
    audits, tasks, checks = core.load(ROOT)
    batch_manifest = json.loads((ROOT / core.BATCH_REL / "manifest.json").read_text())
    if batch_manifest["task_sha256"] != {t["case_id"]: core.digest(t) for t in tasks}:
        raise ValueError("Task export changed after offline validation")
    if batch_manifest["audit_sha256"] != {a["direction_id"]: core.digest(a) for a in audits}:
        raise ValueError("Source audit changed after offline validation")
    if batch_manifest["protocol_sha256"] != core.digest((ROOT / core.AUDIT_REL / "protocol.md").read_bytes()):
        raise ValueError("Source fidelity protocol changed after offline validation")
    if not tasks:
        raise ValueError("No source-verified executable tasks")
    if args.dry_run:
        print(json.dumps({"status": "dry_run_passed", "directions": len(audits), "cases": len(tasks), "offline_checks": len(checks), "max_tokens": "omitted", "concurrency": args.concurrency}))
        return
    key = os.environ.get(args.api_key_env)
    if not key:
        raise ValueError(f"Required credential environment variable is absent: {args.api_key_env}")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    lock = (args.output / ".run.lock").open("w")
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    run_manifest = {"model": args.model, "endpoint": args.endpoint, "concurrency": args.concurrency, "token_ceiling": "omitted",
                    "task_sha256": batch_manifest["task_sha256"], "audit_sha256": batch_manifest["audit_sha256"],
                    "code_sha256": code_identity(ROOT),
                    "selected_cases": [t["case_id"] for t in tasks], "prediction_reads_reference": False, "canonical": False}
    manifest_path = args.output / "run_manifest.json"
    if manifest_path.exists() and json.loads(manifest_path.read_text()) != run_manifest:
        raise ValueError("Run identity differs; do not overwrite existing evidence")
    core.write_json(manifest_path, run_manifest)
    predictions, scores = {}, {}
    gate = threading.BoundedSemaphore(args.concurrency)
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(execute, task, args, key, gate): task for task in tasks}
        save(args, audits, tasks, predictions, scores, "predicting", [t["case_id"] for t in tasks])
        for future in as_completed(futures):
            task = futures[future]
            predictions[task["case_id"]] = future.result()
            save(args, audits, tasks, predictions, scores, "predicting", [t["case_id"] for f,t in futures.items() if not f.done()])
    core.write_json(args.output / "prediction_finished.json", {"at": now(), "records": len(predictions)})
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(evaluate, task, predictions[task["case_id"]], args, key, gate): task for task in tasks}
        for future in as_completed(futures):
            task = futures[future]
            scores[task["case_id"]] = future.result()
            save(args, audits, tasks, predictions, scores, "scoring", [t["case_id"] for f,t in futures.items() if not f.done()])
    issues = any(p["status"] != "generated" for p in predictions.values()) or any(s["status"] != "scored_native" for s in scores.values())
    state = "complete_with_unmeasured_or_pending" if issues else "complete"
    summary = save(args, audits, tasks, predictions, scores, state)
    core.write_json(args.output / "finished.json", {"at": now(), "state": state, "selected_cases": len(tasks), "prediction_records": len(predictions), "score_records": len(scores)})
    print(json.dumps(summary, ensure_ascii=False))
    # Missing original judges are declared evidence gaps, not process crashes.
    return 0


if __name__ == "__main__":
    sys.exit(main())
