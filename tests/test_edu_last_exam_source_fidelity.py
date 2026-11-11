"""Source fidelity guards: no hidden context, scoring substitution, or unsafe execution."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import threading
import pytest

from scripts.source_fidelity import core, isolation


def task(mode="single_turn"):
    return {"case_id":"ELE-SF-01-001", "direction_ids":["01"], "title":"Source task", "origin":"original_task",
            "source":{"case_id":"original_1"}, "selection_reason":"First published record", "review":{"human_review":"pending"},
            "fidelity":{**{k:"Original preserved" for k in ["task_condition","input","output","scoring","environment","scope"]}, "deviations":[]},
            "prediction":{"messages":[{"role":"user","content":"ORIGINAL_PUBLIC_PROMPT"}], "interaction":{"mode":mode}, "parameters":{}},
            "scoring":{"mode":"exact", "native_metric":"original_exact", "expected":"7"}, "assets":[],
            "reference":{"secret":"PRIVATE_GOLD"}}


def test_original_prompt_has_no_universal_wrapper_or_reference_leak(tmp_path):
    item=task()
    observed=[]
    def call(messages, **kwargs):
        observed.append(copy.deepcopy(messages))
        return {"status":"generated", "response":"7"}
    result=core.predict(item,call,tmp_path,tmp_path)
    assert observed == [[{"role":"user","content":"ORIGINAL_PUBLIC_PROMPT"}]]
    assert "PRIVATE_GOLD" not in json.dumps(observed)
    assert core.score(item,result,call,tmp_path,tmp_path)["metrics"]=={"original_exact":1.0}


def test_scripted_protocol_uses_the_actual_prior_response(tmp_path):
    item=task("scripted")
    item["prediction"]["interaction"]["followups"]=["ORIGINAL_APPEAL"]
    observed=[]
    def call(messages, **kwargs):
        observed.append(copy.deepcopy(messages))
        return {"status":"generated", "response":str(len(observed))}
    core.predict(item,call,tmp_path,tmp_path)
    assert observed[1][-2:]==[{"role":"assistant","content":"1"},{"role":"user","content":"ORIGINAL_APPEAL"}]


def test_original_judge_is_not_silently_replaced_by_tested_model(tmp_path):
    item=task()
    item["scoring"]={"mode":"native_judge","native_metric":"rubric","required_model":"original-judge","messages":[{"role":"user","content":"{{MODEL_RESPONSE}}"}]}
    def forbidden(*args,**kwargs):
        raise AssertionError("Wrong judge must never be called")
    score=core.score(item,{"status":"generated","response":"answer"},forbidden,tmp_path,tmp_path)
    assert score["status"]=="native_score_pending"
    assert "metrics" not in score


def test_private_media_cannot_be_delivered_and_symlinks_cannot_escape(tmp_path):
    image=tmp_path/"gold.png"; image.write_bytes(b"private")
    item=task()
    item["assets"]=[{"path":"gold.png","role":"scoring","sha256":core.digest(b"private")}]
    item["prediction"]["messages"]=[{"role":"user","content":[{"type":"image_path","path":"gold.png"}]}]
    with pytest.raises(ValueError,match="explicitly public"):
        core.prepare_messages(item,tmp_path)
    link=tmp_path/"outside"; link.symlink_to("/etc/passwd")
    with pytest.raises(ValueError,match="escapes"):
        core.local_path(tmp_path,"outside")


@pytest.mark.parametrize("name",["max_tokens","max_completion_tokens","model","tools","api_key"])
def test_parameters_cannot_change_identity_or_add_token_ceiling(name):
    with pytest.raises(ValueError):
        core.check_parameters({name:20})


def test_failed_prediction_is_not_scored_as_wrong(tmp_path):
    score=core.score(task(),{"status":"api_error"},None,tmp_path,tmp_path)
    assert score=={"status":"not_scored","reason":"api_error"}


def test_resume_identity_detects_changes_in_imported_transport(tmp_path):
    from scripts.experiments import run_edu_last_exam_source_fidelity as runner
    for relative in ("scripts/experiments/run_edu_last_exam_source_fidelity.py",
                     "scripts/experiments/run_edu_last_exam_challenge_v2.py",
                     "scripts/eval/minimax_client.py"):
        path=tmp_path/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text("original")
    before=runner.code_identity(tmp_path)
    (tmp_path/"scripts/eval/minimax_client.py").write_text("changed transport")
    assert runner.code_identity(tmp_path)!=before


def test_missing_original_system_or_student_role_never_triggers_api(tmp_path):
    item=task()
    item["execution"]={"eligible":False,"reason":"Original dynamic student unavailable"}
    def forbidden(*args,**kwargs):
        raise AssertionError("Incomplete original condition must not be silently substituted")
    result=core.predict(item,forbidden,tmp_path,tmp_path)
    assert result["status"]=="original_condition_unavailable_not_measured"


def test_execution_isolation_never_inherits_credentials_or_personal_home(tmp_path):
    args=isolation.command_for(["/usr/bin/python3","-V"],tmp_path)
    assert "--unshare-all" in args and "--clearenv" in args
    assert args[args.index("--bind")+1:args.index("--bind")+3]==[str(tmp_path),"/work"]
    with pytest.raises(ValueError,match="Credentials"):
        isolation.command_for(["true"],tmp_path,env={"GLM_API":"private"})
    with pytest.raises(ValueError,match="unsafe"):
        isolation.command_for(["true"],tmp_path,readonly_paths=["/home"])


def test_secondary_model_is_only_an_explicit_original_scoring_role(tmp_path,monkeypatch):
    from scripts.experiments import run_edu_last_exam_source_fidelity as runner
    item=task();item["scoring"]["required_model"]="MiniMax-M3"
    monkeypatch.setenv("MINIMAX_API_KEY","fake-private-credential")
    seen=[]
    def request(request,args,key,output):
        seen.append((request["payload"],args.model,key))
        return {"status":"generated","response":"native score","request_sha256":request["request_sha256"],
                "stream_done_seen":True,"returned_models":[args.model]}
    monkeypatch.setattr(runner.transport,"request_one",request)
    caller=runner.Caller(item,tmp_path,SimpleNamespace(model="GLM-5.3-Flash",endpoint="https://example.test"),"fake-glm",threading.BoundedSemaphore(4))
    messages=[{"role":"user","content":"Original judge prompt"}]
    caller(messages,purpose="judge",model="MiniMax-M3")
    assert seen[0][0]["model"]=="MiniMax-M3"
    assert "fake-private-credential" not in json.dumps(seen[0][0])
    with pytest.raises(ValueError,match="original scoring role"):
        caller(messages,purpose="prediction",model="MiniMax-M3")
