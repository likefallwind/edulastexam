# 37方向证据路线矩阵与逐题确定计划

本轮先完成证据和运行产物盘点，再逐项确定题目和评分。当前矩阵不是冻结题单；它把“有原题”“可借用候选”“机制自建”和“条件不足”分开。

## 已盘点的产物

- [逐方向路线矩阵](../../data/edu_last_exam_evidence_route_matrix_v1/route_matrix.json)：37 行，包含来源、benchmark、评分 oracle、历史困难证据、控制和晋级门槛。
- [逐方向/benchmark inventory](../../reports/edu_last_exam_evidence_inventory_v1/inventory.json)：24 个与37方向直接相关的 benchmark，含原始任务目录、mini/frontier 逐题 scored 文件、full eval 产物、judge 模型和重复 identity 计数。
- [生成后的方向矩阵](../../reports/edu_last_exam_evidence_inventory_v1/direction_route_matrix.json)：在路线矩阵上补入当前 source-fidelity card、task IDs、原任务可用性、评分合同和 condition mapping 数量。
- [历史模型错误索引](../../reports/difficulty_mining_v1/summary.json)：对已有 mini/frontier 选题的 36 个 benchmark 做逐题聚合；C-Eval/MOOCCube 另保留 full eval。这里只记录 `historical_model_error`，不把它写成 human difficulty 或冻结结论。
- [逐题候选队列](../../reports/edu_last_exam_item_selection_v1/selection_queue.json)：把81个 source-fidelity task card 和已有 benchmark 候选 item 关联起来；当前全部仍需题面、gold、协议和构念审计。

`edubenchmark` 既有的 [frontier selection report](../../../edubenchmark/reports/frontier_selection_v1/selection_report.md)、[mini selection report](../../../edubenchmark/reports/mini_selection_v2/selection_report.md)、[EduBench item-level analysis](../../../edubenchmark/reports/eval/edubench/_analysis/item_level_analysis.json)、[judge swap](../../../edubenchmark/reports/eval/edubench/_judge_swap/agreement.json) 和 [student-risk 人工错误统计](../../../edubenchmark/reports/eval/student_risk_v2/_audit/codex-manual-error-stats.json) 已挂入 inventory，后续直接复用其统计和限制，不重复造一套全错计数。

## 证据路线

|路线|方向|下一步|
|---|---|---|
|`reuse_original`|01、02、03–08、11、12、16、18–23、28、31、32、37|从原题/公开示例和现有 scored 结果中恢复 item identity、原评分和关键错误；通过 gold、输入和媒体检查后再选题。|
|`benchmark_adaptation`|24、25、26、27|保留原 benchmark 的任务边界，补教育构念、控制和评分；C-Eval/MOOCCube只作相应候选，不扩张成教学能力结论。|
|`mechanism_authored`|09、10、36|按论文中明确的失败条件自建，记录 condition mapping、原始研究定位和改编部分；不称为原论文原题。|
|`blocked`|13–15、17、29、30、33–35|补真实多轮、文件/LMS、学生难度、人类安全量尺或原始协议；不能用静态文本代理填空。|

## 逐项确定题目和评分

对每个方向按以下顺序处理：

1. 从 source-fidelity card 和原始 benchmark 取出候选 item、原始输入、版本和评分合同；记录 `source_item_id`，不把同一案例的对照版本重复算成独立题。
2. 审核 identity、输入完整性、gold/允许答案、重复项、多合法拓扑序、媒体和工具依赖。K12Bench 旧 full 输出存在重复 ID，修复 adapter 后重跑前不进入候选；MOOCCube 先修边逐条查方向和定义。
3. 为每个候选写 `critical_errors`、`acceptable_answers`、`controls` 和 `scoring_mode`。规则题使用原生 scorer；开放题使用原始 rubric 加独立人工/换 judge；artifact 题必须检查渲染或执行结果；stateful 题保存逐轮状态。
4. 把现有结果分成 `unanimous_failure`、`mixed_outcome`、`unanimous_pass`、`incomplete_panel`。只把前两类作为候选排序，不因 frontier 的富集选择把比例当总体难度。
5. 由未参与筛选的模型复测；需要时做重复运行、judge swap 和教师小样本复核。只有 gold、协议、控制和复测稳定，才从 `candidate` 晋级 `freeze`。

## 当前不要做的替代

- 不用 C-Eval 正确率代替学生群体真实难度（17）。
- 不用单轮 LongTutor 或教学对话代替长期学习效果（30）。
- 不用一段计划文字代替 TeachArena 的文件/LMS 写入（14、15、29）。
- 不用 OCR、转写、黑屏/冻结媒体失败代替多模态教育判断（07、08、37）。
- 不用单一 LLM judge 的低分代替教师或人类评分（09–13、21、23、27、28、33、35）。
