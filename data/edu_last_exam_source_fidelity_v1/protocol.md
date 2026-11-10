# 原始来源与任务保真复测协议

用户要求：逐项核对37方向，有可用原题即保留原任务和评分条件；没有原题先核实原研究的具体失败条件，再据此出题。旧题包与旧实验保持不变。Codex负责取题/改编与复核，GLM-5.3-Flash仅用于试跑，不生成规范题。

## 交付及判断

- `data/edu_last_exam_source_fidelity_v1/directions/NN.json`：37项逐项来源核验。必须读原文/原仓库，不能仅链接旧inventory。
- `private/edu_last_exam_source_fidelity_v1/authored/CASE.json`：独立投递单位。共享原题可用direction_ids交叉标注，不重复计算成独立题。
- `sources/datasets/edu_last_exam_source_fidelity_v1/`：复制的原始记录、原prompt/scorer、下载清单；不提交外部原始数据。
- `scripts/source_fidelity/group_NN_NN.py`：必要的受信适配代码；只做明确授权的预测与原生评分。共同运行器负责并发4、请求日志、缓存身份、退出标记与报告。
- 报告分开原题子集、按机制自建、缺材料/环境/评分者、真实未测子机制。37项审查完成不等于37项都成功复现或跑完。
- 不修改原始任务的语言、信息量、提示强度、模型工具、轮数、反馈和评分门槛以人为提高难度。任何必要差异显式记录，不冒充无改动复现。
- 原金标疑错保留原金标和作者复核两列，不能静默改gold。输入不足、协议不完整或研究只支持相邻结论不得据此制造难题。
- 多题原生统计（QWK、相关性、胜率等）保留其含义；小样本不能换算统一正确率。论文原judge模型不可用时记native_score_pending，不能以不同judge的分数冒充原评分；额外审阅必须独立标识。
- 不使用API调用token上限，除非模型/网关确有要求（deepseek-v3.2既有例外）。不运行模型生成的任意代码到持有凭证/主机文件访问能力的进程中；需要代码执行时使用隔离且无网络、无凭证的运行环境。

## 方向核验JSON

每项至少包含：`direction_id`, `title`, `status`（ready_original / ready_mechanism / blocked_source / blocked_protocol / blocked_environment / evidence_gap）, `sources`（数组，每条含source_id/title/url/local_path/sha256/revision/locator/verified_at/evidence_excerpt；没有的值明确null）, `research_failure`（condition/finding/model_setting/scope/source_id/locator）, `original_task`（available/input_contract/output_contract/scoring_contract/environment_contract/source_case_ids）, `decision`（route/rationale/limitations）, `condition_mapping`（逐条condition/evidence_locator/implementation_locator/preserved/omission_reason）, `task_ids`, `search_log`。可以增加详细字段。

## 任务JSON

```json
{
  "case_id": "ELE-SF-01-001",
  "direction_ids": ["01"],
  "title": "完整原任务",
  "origin": "original_task|mechanism_authored",
  "source": {"url":"...", "revision":"...", "case_id":"...", "record_path":"sources/...", "sha256":"...", "prompt_builder_path":"...", "scorer_path":"..."},
  "fidelity": {"task_condition":"...", "input":"...", "output":"...", "scoring":"...", "environment":"...", "deviations":[], "scope":"native_subset"},
  "selection_reason":"仅按原研究失败条件及公开数据顺序选取，未看当前被测模型回答",
  "prediction": {"messages":[{"role":"user","content":"保留原输入全文"}], "parameters":{}, "interaction":{"mode":"single_turn"}},
  "scoring": {"mode":"native_adapter", "native_metric":"原指标", "module":"scripts.source_fidelity.group_01_13", "args":{}},
  "assets":[{"path":"sources/...", "sha256":"...", "role":"provenance"}],
  "reference": {},
  "review": {"human_review":"pending", "author_offline_check":"pending"}
}
```

`prediction.messages`保留原生消息，不追加统一教学/文件指令；OpenAI多模态content中可用`{"type":"image_path","path":"仓库相对路径"}`，运行器仅编码为data URL，不改图片。需要附件文本时直接依原任务模板将全文放入messages，不能让运行器再添提示。

交互模式：`single_turn`，或`scripted`（`followups`数组为原协议实际后续user消息），或`adapter`（`module`/`args`）。复杂原生环境必须adapter，不能把原实际互动替换成一次写计划。

适配模块可定义：

```python
def run(task, call, directory, root):
    # call(messages, purpose="prediction", parameters=None) -> 标准API回包字典
    # 回包至少status, response；每次实际请求持久化，由父运行器统一限制并发。
    return {"status": "generated", "response": "...", "transcript": [], "artifacts": []}

def score(task, result, call, directory, root):
    # 原生解析/指标，必要的提取调用必须记purpose="extraction"，评分调用记purpose="judge"。
    return {"status": "scored_native", "metrics": {}, "native_metric": "..."}

def validate(task, root):
    # 在任何付费API前做离线正反例/模板身份/素材/运行环境检查。
    return {"passed": True, "checks": []}
```

简单评分可用`exact`（expected、可选pattern及case_sensitive）、`numeric`（expected、pattern、tolerance），但仅当原规则确实如此。不能为方便把原生评分换成自定exact。`native_judge`须包含原judge消息模板（唯一替换标记`{{MODEL_RESPONSE}}`）、required_model、metric、原生parser说明；不同judge不自动执行。`manual_pending`须具体说明缺何种原生评分/参考，不得计通过或失败。

过程遵循cards（方向核验）→authored→export→validate→review→freeze；当前只冻结可复现试跑快照，正式benchmark仍待独立审核及多模型验证。
