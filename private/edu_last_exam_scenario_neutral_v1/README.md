# 中性题面对照 · 2026-11-10

由[原候选批次](../edu_last_exam_scenario_v1/README.md)派生：5个任务包、12个版本，10个文本、2个原图。仅改变系统与任务指令；学生作品、参考稿、图像、历史记录、答案、rubric和包内对照均保留。不是新扩充的12道独立题，也不是真实多轮。

- [中性题册](questions.html)
- [原题面与中性题面对照](prompt_comparison.html)
- [沿用的参考答案与评分标准](review.html)：不投递给被测模型。
- 作者源：[`prompt_control.json`](../../data/edu_last_exam_scenario_neutral_v1/prompt_control.json)。候选卡继承原批次，`authored/`及其余导出物由脚本生成。

去掉对变量含义、两种单位解释、援助与掌握关系等检查方向的直接提示。保留完整电路条件、相位简写规则、计算容差、援助字段语义及交付要求。批改草稿是待评对象，保持不变；文本转写中的事实说明也保持不变。电路包必须保留较多条件，本轮主要改变其系统指令，不能声称各包的提示删减强度相同。

```bash
python3 scripts/build/build_edu_last_exam_scenario_neutral.py
python3 scripts/build/build_edu_last_exam_scenario_neutral.py --validate-only
```

构建固定父批次的prompt/manifest哈希，验证所有附件及金标不变，并复用5项数学/对照检查。缺少原图时先按父批次说明获取；禁止悄悄替换为转写。图片沿用原许可边界，忽略入Git，公开再分发尚待确认。

工作流为 `继承cards -> 中性指令源 -> authored/export -> validate -> review -> freeze`。当前为作者离线核验候选，教师审核pending、未冻结。运行状态另存隔离实验目录，不由构建器伪造“已测难度”。

基线为[原GLM试跑](../../reports/eval/edu_last_exam_scenario_v1/_exploratory/20261110_102728_glm/summary.json)。新试跑使用相同模型、接口、并发与投递器。GLM-5.3的原图基线为接口失败；图片与转写分开报告。每模型每版本仅一次，不把随机波动或接口差异直接解释成提示效应。

后续沿用原参考解与rubric逐项审阅；不因模型未复述已删除的提示语、未命名错误类别而判为关键错误，也不设置新的隐含格式要求。模型回答生成、作者审阅、教师校准和正式评分是不同状态。本批不产生跨场景总分。
