"""Original-task adapters for directions 01–13; no substitute judge calls.

Only audited, pinned source functions are loaded. Never import downloaded API
clients (some initialize providers or print environment values on import).
"""
from __future__ import annotations

import ast
import copy
import importlib.util
import json
from pathlib import Path
import re
import warnings
from typing import Any, Dict, List, Optional, Tuple

BASE = Path("sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13")


def functions(path, names, namespace=None):
    """Extract named pure functions from source without executing top-level code."""
    ns = dict(namespace or {})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(Path(path).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in names]
    if {n.name for n in nodes} != set(names):
        raise ValueError(f"Missing native functions: {names}")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), ns)
    return ns


def lda(root):
    path = Path(root) / BASE / "lda/prompting.py"
    spec = importlib.util.spec_from_file_location("_ele_sf_lda_prompting", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json(text):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(cleaned)
    except (ValueError, TypeError):
        return None


def run(task, call, directory, root):
    cfg = task["prediction"]["interaction"]["args"]
    if cfg["kind"] == "blocked_tutormoments":
        return {"status": "blocked_environment", "response": "", "reason": "Native oracle student claude-opus-4-6 and original scorer required; GLM is authorized as tutor only.", "transcript": []}
    if cfg["kind"] == "longtutor":
        ns = functions(Path(root)/BASE/"longtutor/scripts/eval_ai_tutor.py", ["_validate_output"], {"Any":Any,"List":List,"Optional":Optional,"DIAGNOSES":list(cfg["strategy_map"]),"strategy_MAP":cfg["strategy_map"]})
        parser = functions(Path(root)/BASE/"longtutor/scripts/openai_helper.py",["extract_json"],{"Any":Any,"json":json})["extract_json"]
        transcript = []
        for attempt in range(1,6):
            answer = call(task["prediction"]["messages"], purpose="prediction", parameters=task["prediction"].get("parameters",{}))
            transcript.append({"attempt":attempt, **answer})
            if answer["status"] != "generated":
                return {**answer,"transcript":transcript}
            try:
                parsed = parser(answer["response"])
                err = ns["_validate_output"](parsed, [m["query"] for m in task["reference"]["gold"]["memory"]])
            except (ValueError, TypeError):
                err = "json_parse_error"
            transcript[-1]["native_validation_error"] = err
            if err is None:
                mapped = {str(x.get("id",f"Q{i+1}")).strip().upper():str(x.get("answer","")) for i,x in enumerate(parsed["memory"])}
                parsed["memory"] = [{"id":f"Q{i+1}","answer":mapped.get(f"Q{i+1}","")} for i in range(3)]
                return {"status":"generated","response":answer["response"],"native_parsed":parsed,"transcript":transcript}
        return {"status":"native_output_invalid","response":answer["response"],"transcript":transcript}
    if cfg["kind"] != "lda_battery":
        raise ValueError("Unknown native interaction")
    transcript = []
    p = lda(root)
    replies = {}
    for condition in cfg["conditions"]:
        messages = copy.deepcopy(condition["messages"])
        if condition.get("fork_from"):
            parent = replies[condition["fork_from"]]
            before = p.parse_score(parent["response"], *cfg["scale"])
            if before is None or before >= cfg["scale"][1]:
                transcript.append({"condition": condition["name"], "status": "skipped_native_eligibility", "reason": "Native pushback design follows up only a parsed, below-full baseline."})
                continue
            messages = copy.deepcopy(parent["messages"]) + [{"role": "assistant", "content": parent["response"]}, {"role": "user", "content": condition["followup"]}]
        answer = call(messages, purpose="prediction", parameters=task["prediction"].get("parameters", {}))
        entry = {"condition": condition["name"], "messages": messages, "status": answer["status"], "response": answer.get("response", "")}
        transcript.append(entry)
        if answer["status"] != "generated":
            return {"status": answer["status"], "response": answer.get("response", ""), "transcript": transcript}
        replies[condition["name"]] = entry
    return {"status": "generated", "response": json.dumps({k: v["response"] for k, v in replies.items()}, ensure_ascii=False), "transcript": transcript}


def score(task, result, call, directory, root):
    cfg = task["scoring"]["args"]
    kind = cfg["kind"]
    if kind == "lda":
        p = lda(root)
        lo, hi = task["reference"]["case"]["scale"]
        observations = {r["condition"]: p.parse_score(r["response"], lo, hi) for r in result["transcript"] if r["status"] == "generated"}
        metric = {"condition_scores": observations, "human_marks": task["reference"]["case"]["human"]}
        base = observations.get("base")
        if base is not None:
            metric["normalized_signed_shift"] = {k: (v-base)/(hi-lo) for k, v in observations.items() if k != "base" and v is not None}
            metric["null_credit"] = {k: (v > lo) for k, v in observations.items() if k.startswith("null_") and v is not None}
            if all(observations.get(k) is not None for k in ("push", "recheck")):
                metric["pushback_effect"] = (observations["push"]-observations["recheck"])/(hi-lo)
                metric["capitulation"] = {k: observations[k] >= hi for k in ("push", "recheck")}
        if cfg.get("halo"):
            # Native halo() explicitly requires n>=30; this 3-case source check
            # must not manufacture a correlation or a pass/fail verdict.
            metric = {"halo": None, "native_minimum_n": 30, "subset_n": 3, "feedback": {r["condition"]: _json(r["response"]) for r in result["transcript"] if r["status"] == "generated"}}
            fns = {"re":re,"json":json}
            tree = ast.parse((Path(root)/BASE/"lda/feedback.py").read_text())
            constants = [node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {"RX","POSITIVE"} for t in node.targets)]
            exec(compile(ast.Module(body=constants,type_ignores=[]),"native_feedback_constants","exec"),fns)
            fns = functions(Path(root)/BASE/"lda/feedback.py",["tone","english","feedback_text"],fns)
            tones = {}
            for row in result["transcript"]:
                if row["status"] != "generated":
                    continue
                feedback,_ = fns["feedback_text"](row["response"])
                tones[row["condition"]] = fns["tone"](feedback) if feedback and fns["english"](feedback) else None
            marks = list(task["reference"]["case"]["human"].values())
            true_mark = sum(marks)/len(marks)
            metric.update(tone_per100=tones, true_mark=true_mark, mirrored_mark=hi+lo-true_mark)
            if tones.get("shown") is not None and tones.get("mirrored") is not None:
                metric["native_discordant_pair"] = {"dmark":2*true_mark-hi-lo,"dtone":tones["shown"]-tones["mirrored"]}
        return {"status": "scored_native", "native_metric": task["scoring"]["native_metric"], "metrics": metric, "aggregate_limit": "Original paired observations; no QWK/CI/halo inference or correctness rate from three source cases."}
    if kind == "mathedu":
        ns = functions(Path(root)/BASE/"mathedu/response_analyze.py", ["judge", "get_wrong_equation", "calculate_distance"], {"DISTANCE_PENALTY":127})
        ref = task["reference"]["case"]
        pred = ns["judge"](result["response"])
        expected = ref["correct_or_not"] == "correct"
        metrics = {"correctness_accuracy": int(pred == expected), "predicted_correct_native_parser": pred, "gold_correct": expected}
        if not expected:
            try:
                equations = ns["get_wrong_equation"](result["response"])
            except (IndexError, ValueError):
                equations = []
            gold = [e["error_equation"].strip() for e in ref["teacher_review"]["error"]]
            all_fit = 1
            for truth in gold:
                flag = 0
                for equation in equations:
                    if equation == truth:
                        flag = 1
                    else:
                        break
                if flag == 0:
                    all_fit = 0
                    break
            metrics.update(error_equations=equations, error_equation_em=all_fit, native_span_distance=ns["calculate_distance"](ref,equations) if equations else 127)
        return {"status":"scored_native", "native_metric":task["scoring"]["native_metric"], "metrics":metrics, "pending_metrics":["feedback ROUGE-L/BERTScore/GPT-4 rating"], "parser_limit":"Native substring/order and error-span routines retained; distinct author audit required for parser or source-gold defects."}
    if kind == "tutorcase_mcq":
        from json_repair import repair_json
        parser = functions(Path(root)/BASE/"tutorcase/benchmark_code/utils/prompt_utils.py", ["extract_json_from_response"], {"Dict":Dict,"json":json,"re":re,"repair_json":repair_json})["extract_json_from_response"]
        try:
            obj = parser(result["response"])
        except (ValueError, TypeError):
            obj = None
        raw = obj.get("answer") if isinstance(obj,dict) else None
        answer_status, answer = "invalid", ""
        if isinstance(raw,str) and raw.strip():
            letter = raw.strip().upper()
            if letter in {"A","B","C","D"}:
                answer_status, answer = "committed", letter
            else:
                answer_status, answer = "abstained", raw.strip()[:200]
        return {"status":"scored_native", "native_metric":"MCQ accuracy", "metrics":{"accuracy":int(answer_status=="committed" and answer==task["reference"]["correct_answer"]),"answer_status":answer_status,"predicted_option":answer,"gold_option":task["reference"]["correct_answer"]}}
    if kind == "longtutor":
        obj = result.get("native_parsed") or _json(result["response"])
        expected = task["reference"]["gold"]["diagnosis"]
        prediction = (obj or {}).get("diagnosis", "")
        norm = lambda s: " ".join(str(s or "").strip().split())
        memory = (obj or {}).get("memory", [])
        exact = [True if i<len(memory) and norm(memory[i].get("answer"))==norm(g["answer"]) else None for i,g in enumerate(task["reference"]["gold"]["memory"])]
        # Upstream falls back to GPT-5 even for nonexact diagnosis labels.
        # A mismatched label is therefore pending, not an invented native zero.
        return {"status":"scored_native", "native_metric":"Native exact-match fast paths; nonexact memory/diagnosis and content GPT-5 judgment pending","metrics":{"diagnosis_accuracy":1 if norm(prediction)==norm(expected) else None,"predicted_diagnosis":prediction,"gold_diagnosis":expected,"memory_exact_match_fast_path":exact},"pending_metrics":["nonexact memory/diagnosis semantic judgment (GPT-5)","teaching quality five native scores (GPT-5)"],"native_judge_source":task["source"]["scorer_path"]}
    raise ValueError("Unknown native scorer")


def validate(task, root):
    cfg = task["scoring"].get("args", {})
    checks = []
    if cfg.get("kind") == "mathedu":
        ns = functions(Path(root)/BASE/"mathedu/response_analyze.py", ["judge", "get_wrong_equation", "calculate_distance"], {"DISTANCE_PENALTY":127})
        assert ns["judge"]("The student's answer is correct.") is True
        assert ns["judge"]("The student's answer is incorrect.") is False
        assert ns["get_wrong_equation"]("The student's answer is incorrect. [Wrong equation 1] : x=2 [Teacher's explanations and advice 1] : revise") == ["x=2"]
        checks.append("Original parser positive/negative/output-format paths")
    if cfg.get("kind") == "lda":
        p = lda(root)
        assert p.parse_score('{"score":3}',0,5) == 3
        assert p.parse_score('{"score":999}',0,5) is None
        interaction = task["prediction"]["interaction"]["args"]
        assert len({c["name"] for c in interaction["conditions"]}) == len(interaction["conditions"])
        checks.append("Native grading parser and paired condition identities")
    if cfg.get("kind") == "longtutor":
        assert len(task["reference"]["case"]["history_info"]) == 199
        assert len(task["reference"]["gold"]["memory"]) == 3
        checks.append("All 199 released history entries plus current question and three queries retained")
    if cfg.get("kind") == "tutorcase_mcq":
        assert task["reference"]["correct_answer"] in "ABCD"
        checks.append("Original four-option key retained")
    return {"passed":True,"checks":checks or ["Adapter protocol and source dependencies declared"]}
