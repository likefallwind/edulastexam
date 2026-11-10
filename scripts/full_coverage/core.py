"""Offline contracts and bounded environments for the full-coverage pilot."""
from __future__ import annotations

import base64
import copy
import hashlib
import importlib
import json
import re
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "private/edu_last_exam_full_coverage_v1"
MODES = {"single_turn", "scripted_dialogue", "branching_dialogue", "artifact", "workspace", "media"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".csv", ".tsv", ".py", ".svg", ".html"}
IMAGE_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def parse_object(text):
    """Accept a JSON object or a single JSON code block, never eval model output."""
    candidate = text.strip()
    if candidate.startswith("```"):
        match = re.fullmatch(r"```(?:json)?\s*\n?(.*?)\n?```", candidate, re.S)
        if match:
            candidate = match.group(1).strip()
    result = json.loads(candidate)
    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object")
    return result


def safe_relative(value):
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\\" in value or "\x00" in value:
        raise ValueError(f"Unsafe relative path: {value!r}")
    return path


def asset_path(batch, value):
    relative = safe_relative(value)
    if relative.parts[0] != "stimuli":
        raise ValueError("Only stimuli assets may enter prediction input")
    resolved = (batch / str(relative)).resolve()
    if not resolved.is_relative_to((batch / "stimuli").resolve()) or not resolved.is_file():
        raise ValueError(f"Missing or external stimulus: {value}")
    return resolved


def runtime_for(item, prompt_id):
    return copy.deepcopy(item.get("runtime", {}).get(prompt_id, {"mode": "single_turn"}))


def criteria_for_prompt(item, prompt_id):
    """Use the same task-view scope when preparing and checking judgments."""
    if prompt_id not in item["gold"]["per_prompt"]:
        raise ValueError(f"Unknown rubric prompt: {prompt_id}")
    criteria = [criterion for criterion in item["rubric"]["criteria"]
                if "applies_to" not in criterion or prompt_id in criterion["applies_to"]]
    if not any(criterion["required"] for criterion in criteria):
        raise ValueError(f"{prompt_id}: no applicable required rubric criteria")
    return criteria


def validate_runtime(runtime):
    mode = runtime.get("mode", "single_turn")
    if mode not in MODES:
        raise ValueError(f"Unknown mode {mode}")
    if mode == "scripted_dialogue":
        if not runtime.get("followups") or not all(isinstance(t, str) and t.strip() for t in runtime["followups"]):
            raise ValueError("Scripted dialogue needs actual follow-up messages")
    if mode == "branching_dialogue":
        states = runtime["states"]
        terminals = set(runtime["terminal_states"])
        initial = runtime["initial_state"]
        if initial not in states or not 1 <= runtime["max_turns"] <= 30:
            raise ValueError("Invalid dialogue initial state/turn budget")
        for state, specification in states.items():
            if state in terminals:
                continue
            if not specification.get("actions"):
                raise ValueError(f"Nonterminal {state} has no actions")
            for action, transition in specification["actions"].items():
                if not isinstance(action, str) or not action:
                    raise ValueError("Invalid action")
                if transition["next_state"] not in states and transition["next_state"] not in terminals:
                    raise ValueError(f"Dangling transition from {state}")
                if not isinstance(transition["observation"], str):
                    raise ValueError("Missing actual observation")
        reachable, queue = set(), [initial]
        while queue:
            state = queue.pop()
            if state in reachable:
                continue
            reachable.add(state)
            if state not in terminals:
                queue.extend(t["next_state"] for t in states[state]["actions"].values())
        if not reachable.intersection(terminals):
            raise ValueError("No reachable dialogue completion")
    if mode == "artifact":
        validator = runtime["validator"]
        if not re.fullmatch(r"\d{2}", validator):
            raise ValueError("Invalid trusted validator ID")
        if not (ROOT / "scripts/full_coverage/directions" / f"d{validator}.py").is_file():
            raise ValueError(f"Missing artifact validator d{validator}")
        if not 0 <= runtime.get("repair_turns", 0) <= 3:
            raise ValueError("Invalid repair budget")
    if mode == "workspace":
        if not isinstance(runtime["initial_files"], dict) or not 1 <= runtime["max_steps"] <= 40:
            raise ValueError("Invalid workspace")
        for name, content in runtime["initial_files"].items():
            safe_relative(name)
            if not isinstance(content, str):
                raise ValueError("Workspace files must contain text")
        for name in runtime["writable_paths"]:
            safe_relative(name)


def load_items(batch=BATCH, require_all=True):
    items = [json.loads(p.read_text()) for p in sorted((batch / "authored").glob("ELE-FC-*.json"))]
    ids = set()
    directions = set()
    for item in items:
        ident = item["item_id"]
        if not re.fullmatch(r"ELE-FC-\d{2}-\d{3}", ident) or ident in ids:
            raise ValueError(f"Invalid/duplicate item {ident}")
        ids.add(ident)
        direction = item["direction_id"]
        if direction != ident.split("-")[2] or not 1 <= int(direction) <= 37:
            raise ValueError("Direction identity mismatch")
        directions.add(direction)
        for key in ("title", "material_origin", "failure_mechanism", "education_consequence", "measurement_claim"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError(f"{ident}: missing {key}")
        for key in ("source_evidence", "adaptations", "limitations", "unmeasured_subclaims", "controls"):
            if not isinstance(item.get(key), list):
                raise ValueError(f"{ident}: invalid {key}")
        if not item["source_evidence"] or not item["controls"]:
            raise ValueError(f"{ident}: provenance and controls required")
        if item["status"].get("frozen") is not False:
            raise ValueError("This builder only exports candidates")
        rubric = item["rubric"]
        criteria = rubric["criteria"]
        if not criteria or len({c["criterion_id"] for c in criteria}) != len(criteria):
            raise ValueError(f"{ident}: duplicate or missing rubric criteria")
        for criterion in criteria:
            if not criterion.get("observable") or not isinstance(criterion.get("required"), bool):
                raise ValueError(f"{ident}: observable rubric and required flags needed")
        if rubric["aggregation"] != "per_direction_and_task_view_only":
            raise ValueError("No cross-construct aggregate permitted")
        prompts = item["prompts"]
        names = [p["prompt_id"] for p in prompts]
        if not names or len(set(names)) != len(names) or set(item["gold"]["per_prompt"]) != set(names):
            raise ValueError(f"{ident}: prompt/gold mismatch")
        for criterion in criteria:
            if "applies_to" in criterion:
                scope = criterion["applies_to"]
                if (not isinstance(scope, list) or not scope
                        or any(not isinstance(name, str) for name in scope)
                        or len(set(scope)) != len(scope) or not set(scope).issubset(names)):
                    raise ValueError(f"{ident}: invalid applies_to for {criterion['criterion_id']}")
        for prompt in prompts:
            if not re.fullmatch(r"[A-Za-z0-9_-]+", prompt["prompt_id"]):
                raise ValueError("Invalid prompt id")
            if not prompt["system_prompt"].strip() or not prompt["user_prompt"].strip():
                raise ValueError("Empty model instructions")
            for relative in prompt["assets"]:
                asset_path(batch, relative)
            gold = item["gold"]["per_prompt"][prompt["prompt_id"]]
            for key in ("reference_answer", "acceptable_alternatives", "critical_errors"):
                if key not in gold:
                    raise ValueError(f"{ident}: missing gold {key}")
            criteria_for_prompt(item, prompt["prompt_id"])
            validate_runtime(runtime_for(item, prompt["prompt_id"]))
    if require_all and directions != {f"{i:02}" for i in range(1, 38)}:
        raise ValueError(f"Incomplete direction coverage: {sorted(directions)}")
    return items


def prepare_messages(batch, prompt, enable_video=True, enable_audio=False):
    """Only public prompt/stimuli are read; no gold, future states or rubrics."""
    text = prompt["user_prompt"]
    parts, assets, unsupported = [], [], []
    for relative in prompt["assets"]:
        path = asset_path(batch, relative)
        raw = path.read_bytes()
        suffix = path.suffix.lower()
        assets.append({"path": relative, "sha256": digest(raw), "bytes": len(raw)})
        if suffix in TEXT_SUFFIXES:
            text += f"\n\n===== 附件 {relative} =====\n" + raw.decode("utf-8")
        elif suffix in IMAGE_MIME:
            parts.append({"type": "image_url", "image_url": {"url": f"data:{IMAGE_MIME[suffix]};base64," + base64.b64encode(raw).decode()}})
        elif suffix == ".mp4" and enable_video:
            parts.append({"type": "video_url", "video_url": {"url": "data:video/mp4;base64," + base64.b64encode(raw).decode()}})
        elif suffix in {".wav", ".mp3"} and enable_audio:
            parts.append({"type": "input_audio", "input_audio": {"data": base64.b64encode(raw).decode(), "format": suffix[1:]}})
        else:
            unsupported.append({"path": relative, "reason": "not_supported_by_selected_provider_contract"})
    content = [{"type": "text", "text": text}, *parts] if parts else text
    return [{"role": "system", "content": prompt["system_prompt"]}, {"role": "user", "content": content}], assets, unsupported


def append_instruction(messages, text):
    """Add only the current environment interface, not future observations."""
    last = messages[-1]["content"]
    if isinstance(last, str):
        messages[-1]["content"] = last + "\n\n" + text
    else:
        last[0]["text"] += "\n\n" + text


def action_menu(runtime, state):
    actions = runtime["states"][state]["actions"]
    descriptions = {k: v.get("description", k) for k, v in actions.items()}
    memory = '另需memory字符串，写入下一次会话可以读取的学习交接记录。' if runtime.get("persist_memory") else ''
    return ('本轮可用行动：' + json.dumps(descriptions, ensure_ascii=False) +
            '。请输出JSON对象 {"action":"行动名","message":"实际给学生/教师的回应"}。选择与message必须一致。' + memory)


def nested_value(value, dotted):
    for part in dotted.split("."):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def validate_workspace(files, runtime):
    checks = []
    specification = runtime.get("submit_checks", {})
    for path, snippets in specification.get("file_contains", {}).items():
        checks.append({"check": "contains:" + path, "passed": path in files and all(v in files[path] for v in snippets)})
    for path, fields in specification.get("file_json_equals", {}).items():
        for key, expected in fields.items():
            try:
                actual = nested_value(json.loads(files[path]), key)
                passed = actual == expected
            except (KeyError, IndexError, ValueError, TypeError):
                passed = False
            checks.append({"check": f"json:{path}:{key}", "passed": passed})
    for path in specification.get("unchanged_paths", []):
        checks.append({"check": "unchanged:" + path, "passed": files.get(path) == runtime["initial_files"].get(path)})
    return {"passed": bool(checks) and all(c["passed"] for c in checks), "checks": checks}


def workspace_action(command, files, runtime):
    action = command.get("action")
    if action == "list":
        return {"files": sorted(files)}, False
    if action == "submit":
        return {"submitted": True}, True
    if action not in {"read", "write"}:
        return {"error": "unknown_action"}, False
    path = str(command.get("path", ""))
    try:
        safe_relative(path)
    except ValueError:
        return {"error": "invalid_path"}, False
    if action == "read":
        return ({"path": path, "content": files[path]} if path in files else {"error": "not_found"}), False
    if path not in runtime["writable_paths"]:
        return {"error": "read_only_path"}, False
    content = command.get("content")
    if not isinstance(content, str):
        return {"error": "content_must_be_text"}, False
    files[path] = content
    return {"written": path, "bytes": len(content.encode())}, False


def artifact_check(runtime, response, output, prompt_id):
    module = importlib.import_module(f"scripts.full_coverage.directions.d{runtime['validator']}")
    output.mkdir(parents=True, exist_ok=True)
    result = module.validate_artifact(response, output, prompt_id)
    if not isinstance(result, dict):
        raise ValueError("Validator must return an object")
    write_json(output / "validation.json", result)
    return result


def execute_episode(task, call, directory):
    """call(messages, index) returns a recorded API result; injectable offline."""
    runtime = copy.deepcopy(task["runtime"])
    mode = runtime.get("mode", "single_turn")
    messages = copy.deepcopy(task["messages"])
    transcript, events, checks = [], [], []
    state = runtime.get("initial_state")
    files = copy.deepcopy(runtime.get("initial_files", {}))
    if mode == "branching_dialogue":
        append_instruction(messages, action_menu(runtime, state))
    if mode == "workspace":
        append_instruction(messages, '工作区工具以JSON交互。每轮只输出一个对象：{"action":"list|read|write|submit","path":"相对路径","content":"write时的完整文本","message":"说明"}。文件列表：' + json.dumps(sorted(files), ensure_ascii=False) + '。可写路径：' + json.dumps(runtime["writable_paths"], ensure_ascii=False))
    rounds = {"single_turn": 1, "media": 1, "scripted_dialogue": 1 + len(runtime.get("followups", [])),
              "artifact": 1 + runtime.get("repair_turns", 0), "branching_dialogue": runtime.get("max_turns", 1),
              "workspace": runtime.get("max_steps", 1)}[mode]
    status = "generated"
    completed = mode not in {"branching_dialogue", "workspace"}
    for index in range(rounds):
        result = call(copy.deepcopy(messages), index)
        transcript.append({"turn": index, "messages": copy.deepcopy(messages), "response": result.get("response", ""), "status": result["status"]})
        if result["status"] != "generated":
            status = result["status"]
            completed = False
            break
        answer = result["response"]
        messages.append({"role": "assistant", "content": answer})
        if mode in {"single_turn", "media"}:
            break
        if mode == "scripted_dialogue":
            if index < len(runtime["followups"]):
                messages.append({"role": "user", "content": runtime["followups"][index]})
            continue
        if mode == "artifact":
            check = artifact_check(runtime, answer, directory / "artifacts" / f"turn_{index:02}", task["prompt_id"])
            checks.append({"turn": index, **check})
            if check.get("environment_error"):
                status = "environment_error_not_scored"
                completed = False
                break
            if check.get("passed") is True or index + 1 >= rounds:
                break
            feedback = check.get("public_feedback", "请依据原任务自行复查并提交完整修订；本轮没有额外公开的检查结果。")
            messages.append({"role": "user", "content": "本轮交付后的公开环境反馈：\n" + (feedback if isinstance(feedback, str) else json.dumps(feedback, ensure_ascii=False)) + "\n请交付完整修订内容。"})
            continue
        try:
            command = parse_object(answer)
        except (ValueError, TypeError):
            events.append({"turn": index, "error": "invalid_json_action"})
            messages.append({"role": "user", "content": '环境无法解析本轮行动。请按公开合同输出单个JSON对象，不附代码块外的文字。'})
            continue
        if mode == "workspace":
            observation, completed = workspace_action(command, files, runtime)
            events.append({"turn": index, "command": command, "observation": observation})
            if completed:
                checks.append(validate_workspace(files, runtime))
                break
            messages.append({"role": "user", "content": "工具结果：" + json.dumps(observation, ensure_ascii=False)})
        else:
            action = command.get("action")
            choices = runtime["states"][state]["actions"]
            if action not in choices or not isinstance(command.get("message"), str) or (runtime.get("persist_memory") and not isinstance(command.get("memory"), str)):
                events.append({"turn": index, "state": state, "error": "invalid_action"})
                messages.append({"role": "user", "content": "行动未执行。" + action_menu(runtime, state)})
                continue
            transition = choices[action]
            events.append({"turn": index, "state": state, "action": action, "message": command["message"], "memory": command.get("memory"), "context_reset": bool(transition.get("reset_context")), "observation": transition["observation"], "next_state": transition["next_state"]})
            if runtime.get("persist_memory"):
                write_json(directory / "persistent_memory.json", {"source_turn": index, "memory": command["memory"]})
            state = transition["next_state"]
            if state in runtime["terminal_states"]:
                completed = True
                break
            observation = transition["observation"] + "\n\n" + action_menu(runtime, state)
            if transition.get("reset_context"):
                if not runtime.get("persist_memory"):
                    raise ValueError("Context reset needs an explicit persistent-memory contract")
                messages = [copy.deepcopy(task["messages"][0]), {"role": "user", "content": "新会话。以下是你上次实际保存的交接记录：\n" + command["memory"] + "\n\n本次新观察：\n" + observation}]
            else:
                messages.append({"role": "user", "content": observation})
    if mode == "workspace":
        for relative, content in files.items():
            safe_relative(relative)
            target = directory / "workspace" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    if status == "generated" and not completed:
        status = "episode_incomplete"
    return {"status": status, "transcript": transcript, "events": events, "artifact_checks": checks,
            "environment_completed": completed, "final_state": state, "response": transcript[-1]["response"] if transcript else "",
            "model_turns": len(transcript), "measurement_mode": mode}
