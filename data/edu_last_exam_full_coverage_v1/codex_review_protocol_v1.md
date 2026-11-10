# GLM-5.3-Flash 全量 Codex 复核协议

对象为 `20261110_142158_glm53flash` 的82个投递版本，其中80个有效模型回答、2个音频未测。本次是Codex对冻结题面、原始回答及实际轨迹的另一模型审阅，不是独立教师人审；Codex也参与过候选编写，保留这一作者关联。禁止修改原始回包、原始GLM评分、冻结题面或运行环境；不调用被测模型补答。

逐份先读冻结题面、附件、gold、适用rubric、完整transcript及实际产物/环境记录，形成判断，再比较原始初评。不能仅复制GLM结论。gold有疑问时独立核算；输入不足、评分标准不合理或缺观察时明确记争议，不制造错误。多轮题区分中途问题与允许修复后的最终结果；合约格式、教育内容、实际交付分别说明。对照是否支持鲁棒性等结论另作成对核验。

源复核记录写入 `private/edu_last_exam_full_coverage_v1/reviews/glm53flash_20261110_codex/part_NN_NN.json`。生成报告只能由脚本生成，不手改 `reports/`。

每份记录包含：

```json
{
  "case_id": "ELE-FC-01-001__errors",
  "verdict": "pass|fail|disputed|continuous_valid|continuous_invalid|not_measured",
  "confidence": "high|medium|low",
  "summary": "具体结论及边界",
  "independent_check": "独立计算、依据或执行检查，不能只说与gold一致",
  "criteria": [{"criterion_id":"c1","assessment":"met|not_met|uncertain|not_applicable","reason":"可观察依据","evidence":[{"kind":"response","turn":0,"quote":"逐字短引文"}]}],
  "issues": [{"kind":"model_error|item_or_gold_issue|judge_issue|runtime_issue|minor_issue","description":"具体问题","evidence":[]}],
  "control_notes": "与哪些配对版本比较，或本题无额外成对判据",
  "material_checks": ["实际读过的附件、媒体或产物路径及查看方式"]
}
```

`evidence` 只接受实际结果里的短引文：`kind=response` 配 `turn`，引用 `transcript[turn].response`；`kind=event` 或 `artifact_check` 配 `index`，引用对应对象 `json.dumps(...,ensure_ascii=False)` 中的片段。每个met需有证据；因缺少动作/内容判not_met时可列观察到的邻近动作，并在reason说明缺失。不能把参考答案或用户题面当成模型回答引用。

普通评分版本逐项覆盖适用criteria（依据applies_to）；所有required met且无实质失败才pass；确定未满足required为fail；无法可靠定性或gold/输入有实质争议为disputed。minor不自动导致整题fail。连续指标任务17单列指标与输出合同，不将其MAE阈值化为正确率。音频未测保留2个占位，criteria可空。

最终报告先列每方向和每版本，再给用户所需的本批次描述性通过比例：仅统计已有明确pass/fail的二元任务版本，另列争议、连续指标及未测分母。它不是跨构念的统一能力分数，也不估计真实课堂总体正确率。保留原初评与复核的差异及待教师审阅范围。
