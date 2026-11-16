# 方向31完整探索试验复盘

两类原创合成编程作业，各三依赖条件，完整重复两轮。作者关联语义复核，独立教师审核pending，未冻结。

## 结果

共12条实际轨迹，12条通过全部预设功能探针；多错误目标条件4/4条正确识别并修复两个根因。本批未复现“只修首错而遗漏后错”的目标失败；当前难度尚未建立。

|材料/条件|角色|首轮完整量尺|重复轮完整量尺|预设功能探针通过|
|---|---|---|---|---|
|ELE-V2-31-001__v1|target|fail_author_reviewed|pass_author_reviewed|2/2|
|ELE-V2-31-001__v2|single_error_counterfactual|pass_author_reviewed|pass_author_reviewed|2/2|
|ELE-V2-31-001__v3|correct_control|pass_author_reviewed|pass_author_reviewed|2/2|
|ELE-V2-31-002__v1|target|pass_author_reviewed|pass_author_reviewed|2/2|
|ELE-V2-31-002__v2|single_error_counterfactual|pass_author_reviewed|pass_author_reviewed|2/2|
|ELE-V2-31-002__v3|correct_control|pass_author_reviewed|pass_author_reviewed|2/2|

## 附加问题与判断边界

附加反馈错误、报告格式瑕疵及可恢复JSON动作错误分别记录，不把它们冒充目标机制的复现。
- 第1轮 `ELE-V2-31-001__v1`：final、total均不是Python内建名称，原学生程序也没有final变量。该提醒不影响根因集合或执行结果，不能作为多错误遮蔽机制复现的证据。
- 第1轮 `ELE-V2-31-001__v2`：counterexample字段写成[[1,2,3]]，正文清楚说明输入为[1,2,3]，语义反例有效；不将这个可辨格式瑕疵认作目标机制错误。

## 运行与评分

- GLM-5.3-Flash，原coding plan endpoint；无token上限，无GLM自评。
- 首轮并发3触发429后，归档接口失败汇总并降到2恢复；成功回包保留，失败调用按原请求身份重试。第二轮仍全量六条件。
- 两轮题包、运行代码和请求身份均冻结；每轮有summary、完成标记、进程退出码、SSE结束与返回模型核验。
- 统计题3910个、连续记录题368个预先固定探针，覆盖所有长度0–5的指定短序列及长/边界例；不穷尽全部长度20输入。
- 私有探针不进入模型输入；真实run动作仅运行公开示例，报告中的其他边界应明确为推演。

## 对后续出题的启发

本轮输入明示重复观测与缺测边界，首个异常和第二根因也均可通过静态代码审查定位；模型成功时应保留为成功控制。两材料小样本尚不足以形成方向31的总体AI难度结论。
后续若继续方向31，应以新的批次检验更真实的状态变化、相互影响的修复路径或经核验的真实学生程序，并保留本批成功控制。新题需要重新完成离线核验与独立复测，不能在看过输出的同一题包内反复改题制造失败。

## 原始报告

- [20261113_glm53flash_run01](./20261113_glm53flash_run01/result_analysis.html)
- [20261113_glm53flash_run02](./20261113_glm53flash_run02/result_analysis.html)
