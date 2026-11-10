#!/usr/bin/env python3
"""Run bounded education tasks and optional evidence-checked exploratory judging.

The GLM test model receives public inputs and current environment observations.
References and hidden future branches are not prediction input. No token ceiling.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from datetime import datetime, timezone
import fcntl
import html
import json
import os
from pathlib import Path
import sys
import threading
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage.core import BATCH, digest, execute_episode, prepare_messages, write_json
from scripts.full_coverage.judging import judge_messages, validate_judgment
from scripts.experiments import run_edu_last_exam_challenge_v2 as transport

VERSION = "edu_full_coverage_bounded_environments_v1"


def now():
    return datetime.now(timezone.utc).isoformat()


def prepare(batch, output, args):
    raw = (batch / "prompts.jsonl").read_bytes()
    runtime_raw = (batch / "runtimes.json").read_bytes()
    item_raw = (batch / "items.jsonl").read_bytes()
    manifest = json.loads((batch / "manifest.json").read_text())
    for raw_bytes, key in ((raw, "prediction_export_sha256"), (runtime_raw, "runtime_sha256"), (item_raw, "item_export_sha256")):
        if digest(raw_bytes) != manifest[key]:
            raise ValueError(f"Batch export drift: {key}")
    rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    items = {item["item_id"]: item for item in (json.loads(line) for line in item_raw.decode().splitlines() if line.strip())}
    runtimes = json.loads(runtime_raw)
    tasks = []
    code = {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in [Path(__file__), ROOT / "scripts/experiments/run_edu_last_exam_challenge_v2.py", ROOT / "scripts/eval/minimax_client.py", *sorted((ROOT / "scripts/full_coverage").rglob("*.py"))]}
    prediction_code = {name: value for name, value in code.items() if name not in {
        "scripts/full_coverage/judging.py", "scripts/experiments/run_edu_last_exam_full_coverage.py"}}
    for prompt in rows:
        case_id = prompt["item_id"] + "__" + prompt["prompt_id"]
        messages, assets, unsupported = prepare_messages(batch, prompt, enable_video=not args.disable_video, enable_audio=args.enable_audio)
        for asset in assets:
            if asset["sha256"] != manifest["assets"][asset["path"]]["sha256"]:
                raise ValueError(f"Asset drift: {asset['path']}")
            target = output / "cases" / case_id / "input" / asset["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            source_bytes = (batch / asset["path"]).read_bytes()
            if target.exists() and target.read_bytes() != source_bytes:
                raise ValueError("Run input snapshot differs; choose a fresh output directory")
            target.write_bytes(source_bytes)
        identity = digest({"version": VERSION, "model": args.model, "endpoint": args.endpoint, "messages": messages,
                           "runtime": runtimes[case_id], "assets": assets, "prediction_code": prediction_code})
        task = {"case_id": case_id, "item_id": prompt["item_id"], "direction_id": prompt["direction_id"], "prompt_id": prompt["prompt_id"],
                "request_sha256": identity, "messages": messages, "runtime": runtimes[case_id], "assets": assets, "unsupported": unsupported,
                "interaction_mode": prompt["interaction_mode"], "prompt": prompt}
        record = output / "cases" / case_id / "input_identity.json"
        if record.exists() and json.loads(record.read_text())["request_sha256"] != identity:
            raise ValueError(f"Run identity changed: {case_id}")
        write_json(record, {k: task[k] for k in ("case_id", "item_id", "direction_id", "prompt_id", "request_sha256", "assets", "unsupported", "interaction_mode")})
        tasks.append(task)
    result = {"protocol": VERSION, "model": args.model, "endpoint": args.endpoint, "concurrency": args.concurrency, "token_ceiling": "omitted",
              "total_directions": len({t["direction_id"] for t in tasks}), "total_items": len(items), "total_cases": len(tasks),
              "runtime_modes": sorted({t["runtime"]["mode"] for t in tasks}), "source_hashes": {"prompts": digest(raw), "runtimes": digest(runtime_raw), "items": digest(item_raw)},
              "code_hashes": code, "unsupported_cases": [t["case_id"] for t in tasks if t["unsupported"]],
              "prediction_reads_gold": False, "canonical": False, "same_family_judge": args.with_judge,
              "provider_audio_contract_enabled": args.enable_audio, "provider_video_contract_enabled": not args.disable_video}
    write_json(output / "run_manifest.json", result)
    return tasks, items, result


def api_call(messages, index, task, directory, args, key):
    payload = {"model": args.model, "messages": messages, "stream": True, "stream_options": {"include_usage": True}}
    request_sha = digest({"endpoint": args.endpoint, "payload": payload})
    turn_id = f"turn_{index:03}"
    turn_task = {"case_id": turn_id, "item_id": task["item_id"], "prompt_id": task["prompt_id"], "request_sha256": request_sha,
                 "interaction_mode": task["interaction_mode"], "payload": payload}
    turn_dir = directory / "calls" / "cases" / turn_id
    turn_dir.mkdir(parents=True, exist_ok=True)
    request_file = turn_dir / "request.json"
    if request_file.exists() and json.loads(request_file.read_text())["request_sha256"] != request_sha:
        raise ValueError("Turn input changed during resume")
    write_json(request_file, turn_task)
    cache = turn_dir / "result.json"
    if cache.exists():
        prior = json.loads(cache.read_text())
        if prior["request_sha256"] != request_sha:
            raise ValueError("Turn cache identity mismatch")
        if prior["status"] == "generated":
            return prior
    result = transport.request_one(turn_task, args, key, directory / "calls")
    if result["status"] == "generated" and (not result.get("stream_done_seen") or not result.get("returned_models")):
        result["status"] = "completion_unverified"
        write_json(cache, result)
    return result


def predict(task, args, key, output):
    directory = output / "cases" / task["case_id"]
    identity = {k: task[k] for k in ("case_id", "item_id", "direction_id", "prompt_id", "request_sha256")}
    if task["unsupported"]:
        result = {**identity, "status": "unsupported_input_not_scored", "unsupported": task["unsupported"], "finished_at": now()}
        write_json(directory / "result.json", result)
        return result
    cache = directory / "result.json"
    if cache.exists():
        prior = json.loads(cache.read_text())
        if prior.get("request_sha256") != task["request_sha256"]:
            raise ValueError("Prediction cache input mismatch")
        if prior["status"] in {"generated", "episode_incomplete"}:
            return prior
    started = now()
    try:
        result = execute_episode(task, lambda messages, index: api_call(messages, index, task, directory, args, key), directory)
    except Exception as exc:
        result = {"status": "environment_error_not_scored", "error": str(exc).replace(key, "[REDACTED]")}
        (directory / "environment_error.txt").write_text(traceback.format_exc().replace(key, "[REDACTED]"))
    result = {**identity, **result, "started_at": started, "finished_at": now(), "model": args.model, "judging": "not_run"}
    write_json(cache, result)
    if "transcript" in result:
        write_json(directory / "transcript.json", result["transcript"])
        (directory / "response.md").write_text(result.get("response", ""), encoding="utf-8")
    return result


def score(task, item, result, args, key, output):
    directory = output / "cases" / task["case_id"] / "judging"
    if result["status"] not in {"generated", "episode_incomplete"}:
        return {"case_id": task["case_id"], "status": "not_scored", "reason": result["status"]}
    if item.get("scoring_type") == "continuous":
        checks = result.get("artifact_checks", [])
        valid = bool(checks) and checks[-1].get("passed") is True
        scoring = {"case_id": task["case_id"], "status": "continuous_metrics" if valid else "continuous_output_invalid", "verdict": "continuous_metric_only", "checks": checks, "no_binary_task_accuracy": True}
        write_json(directory / "judgment.json", scoring)
        return scoring
    messages = judge_messages(item, task["prompt"], result)
    identity = digest({"messages": messages, "model": args.model, "endpoint": args.endpoint, "judge_code": Path(sys.modules[validate_judgment.__module__].__file__).read_text()})
    cache = directory / "judgment.json"
    if cache.exists():
        prior = json.loads(cache.read_text())
        if prior.get("judge_request_sha256") == identity and prior.get("status") == "scored_exploratory":
            return prior
    errors = []
    scoring = None
    for attempt in range(2):
        answer = api_call(messages, attempt, task, directory, args, key)
        if answer["status"] != "generated":
            scoring = {"status": "judge_api_error", "reason": answer["status"]}
            break
        try:
            scoring = validate_judgment(answer["response"], item, result, task["prompt_id"])
            break
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(str(exc))
            messages.extend([{"role": "assistant", "content": answer["response"]}, {"role": "user", "content": "评分格式或证据核验未通过：" + str(exc) + "。请重新输出完整JSON；关键错误description必须逐字使用给定列表，引用必须来自实际被评输出。"}])
    if scoring is None:
        scoring = {"status": "judge_invalid_not_scored", "validation_errors": errors}
    scoring = {"case_id": task["case_id"], "direction_id": task["direction_id"], "judge_request_sha256": identity, **scoring}
    write_json(cache, scoring)
    return scoring


def write_report(output, tasks, predictions, scores, summary):
    body = ["<!doctype html><html lang='zh-CN'><meta charset='utf-8'><title>全方向探索运行</title><style>body{font:16px/1.7 system-ui;max-width:1200px;margin:30px auto;padding:20px}td,th{border:1px solid #ccc;padding:8px}table{border-collapse:collapse}pre{white-space:pre-wrap}</style><h1>全方向探索运行</h1><p>作者候选；语义评分为同模型初评，未完成独立教师复核。不跨场景计算总正确率。</p>", "<pre>" + html.escape(json.dumps(summary, ensure_ascii=False, indent=2)) + "</pre>", "<table><tr><th>方向/案例</th><th>环境</th><th>回包</th><th>初评</th><th>原始证据</th></tr>"]
    for task in tasks:
        case = task["case_id"]
        prediction, scoring = predictions.get(case, {}), scores.get(case, {})
        body.append("<tr><td>" + html.escape(task["direction_id"] + " / " + case) + "</td><td>" + html.escape(task["runtime"]["mode"]) + "</td><td>" + html.escape(prediction.get("status", "pending")) + "</td><td>" + html.escape(scoring.get("verdict", scoring.get("status", "not_scored"))) + f'</td><td><a href="cases/{case}/result.json">回包与轨迹</a> · <a href="cases/{case}/judging/judgment.json">评分</a></td></tr>')
    body.append("</table></html>")
    (output / "report.html").write_text(''.join(body), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, default=BATCH)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="GLM-5.3-Flash")
    parser.add_argument("--endpoint", default=transport.ENDPOINT)
    parser.add_argument("--api-key-env", default="GLM_API")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--with-judge", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--enable-audio", action="store_true", help="Only for an explicitly verified audio-capable provider")
    parser.add_argument("--disable-video", action="store_true")
    parser.add_argument("--case-id", action="append")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if not 1 <= args.concurrency <= 4 or (args.limit is not None and args.limit < 1):
        parser.error("Use concurrency 1–4 and a positive limit")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with (output / ".run.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        tasks, items, manifest = prepare(args.batch.resolve(), output, args)
        selected = [t for t in tasks if not args.case_id or t["case_id"] in args.case_id]
        if args.case_id and len(selected) != len(set(args.case_id)):
            raise ValueError("Unknown requested case ID")
        selected = selected[:args.limit] if args.limit else selected
        manifest["selected_cases"] = [t["case_id"] for t in selected]
        write_json(output / "run_manifest.json", manifest)
        if args.dry_run:
            print(json.dumps(manifest, ensure_ascii=False), flush=True)
            return 0
        key = os.environ.get(args.api_key_env)
        if not key:
            raise RuntimeError(f"{args.api_key_env} is not set")
        for marker in ("finished.json", "exit_code.txt", "summary.json"):
            (output / marker).unlink(missing_ok=True)
        started = now()
        write_json(output / "started.json", {"at": started, "pid": os.getpid(), "concurrency": args.concurrency})
        predictions, scores = {}, {}
        active, guard = set(), threading.Lock()

        def progress(phase, final=False):
            with guard:
                running = sorted(active)
            by_direction = {}
            for task in selected:
                row = by_direction.setdefault(task["direction_id"], {"cases": 0, "generated": 0, "unavailable": 0, "verdicts": {}})
                row["cases"] += 1
                prediction = predictions.get(task["case_id"], {})
                if prediction.get("status") == "generated":
                    row["generated"] += 1
                elif prediction and prediction.get("status") != "episode_incomplete":
                    row["unavailable"] += 1
                verdict = scores.get(task["case_id"], {}).get("verdict")
                if verdict:
                    row["verdicts"][verdict] = row["verdicts"].get(verdict, 0) + 1
            counts = {}
            for result in predictions.values():
                counts[result["status"]] = counts.get(result["status"], 0) + 1
            data = {"updated_at": now(), "started_at": started, "phase": phase, "finished": final, "model": args.model, "concurrency": args.concurrency,
                    "total_batch_cases": len(tasks), "selected_cases": len(selected), "prediction_results": len(predictions), "score_results": len(scores),
                    "status_counts": counts, "inflight": running, "directions": by_direction, "all_37_directions_selected": len(by_direction) == 37,
                    "no_cross_scenario_accuracy": True, "independent_teacher_review": "pending", "all_subclaims_directly_measured": False}
            write_json(output / "progress.json", data)
            write_report(output, selected, predictions, scores, data)
            return data

        def run(task, phase):
            with guard:
                active.add(task["case_id"])
            print(f"{now()} {phase} START {task['case_id']}", flush=True)
            try:
                return predict(task, args, key, output) if phase == "prediction" else score(task, items[task["item_id"]], predictions[task["case_id"]], args, key, output)
            finally:
                with guard:
                    active.remove(task["case_id"])

        for phase in (["prediction", "judging"] if args.with_judge else ["prediction"]):
            progress(phase)
            with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
                futures = {pool.submit(run, task, phase): task for task in selected}
                while futures:
                    done, _ = wait(futures, timeout=5, return_when=FIRST_COMPLETED)
                    for future in done:
                        task = futures.pop(future)
                        try:
                            result = future.result()
                        except Exception as exc:
                            result = {"case_id": task["case_id"], "status": "runner_error_not_scored", "error": str(exc).replace(key, "[REDACTED]")}
                            write_json(output / "cases" / task["case_id"] / ("runner_error.json" if phase == "prediction" else "judge_runner_error.json"), result)
                        (predictions if phase == "prediction" else scores)[task["case_id"]] = result
                        print(f"{now()} {phase} {result['status']} {task['case_id']}", flush=True)
                    progress(phase)
        summary = progress("finished", final=True)
        issues = any(r["status"] not in {"generated", "episode_incomplete"} for r in predictions.values()) or any(r["status"] not in {"scored_exploratory", "continuous_metrics"} for r in scores.values())
        summary["run_status"] = "complete_with_issues" if issues else "selected_tasks_complete"
        summary["full_batch_selected"] = len(selected) == len(tasks)
        summary["judging"] = "exploratory_same_model" if args.with_judge else "not_run"
        write_json(output / "summary.json", summary)
        write_json(output / "finished.json", {"at": now(), "exit_code": int(issues), "run_status": summary["run_status"]})
        (output / "exit_code.txt").write_text(str(int(issues)) + "\n")
        for name, data in (("predictions", predictions), ("scores", scores)):
            (output / f"{name}.jsonl").write_text(''.join(json.dumps(data[t["case_id"]], ensure_ascii=False) + "\n" for t in selected if t["case_id"] in data), encoding="utf-8")
        write_report(output, selected, predictions, scores, summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
        return int(issues)


if __name__ == "__main__":
    raise SystemExit(main())
