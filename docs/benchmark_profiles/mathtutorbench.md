# MathTutorBench

**一句话**：数学辅导能力全家桶——7 个任务 + 2 个 hard 变体，从"会不会做题"一路测到"会不会搭脚手架引导学生"，是"会答题≠会教"命题的最直接载体。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 动机：基于学习科学理论把"辅导"拆成可分别测量的任务；原版配套一个专家级奖励模型（能区分专家/新手教师回复）判开放式任务。

## 数据

- 题源组合：GSM8K（解题类）、MathDial（对话辅导类）、eth-nlped/stepverify（学生解验证类）。英文。
- 本地可用，数据随评测直接拉取。

## 任务与判分（9 个 adapter + 1 个裁判校准）

| 任务 | 测什么 | 判分 |
|---|---|---|
| problem_solving | 解题正确率 | 规则（数值匹配） |
| solution_correctness | 判学生解对错 | 规则（移植官方 parse） |
| mistake_location | 定位第一处错误步骤 | 规则 |
| mistake_correction | 给出修正后的正确答案 | 规则（从回复提取答案） |
| socratic_questioning | 生成引导性提问 | SacreBLEU 对金标问题取最佳匹配 |
| scaffolding / scaffolding_hard | 生成下一步辅导回复 | 与参考回复比较的 win-rate |
| pedagogy / pedagogy_hard | 按教学法指令生成回复 | win-rate |

- 官方开放任务用 GPU 奖励模型判；本仓库用 **LLM 裁判 win-rate 替代**（`MATHTUTORBENCH_JUDGE_MODEL`，pairwise prompt 有版本号与 sha256 记录）——绝对分不可与论文对照，横向比较可用。
- `mathtutorbench_judge_calibration` 单独校准裁判与官方奖励模型的一致性。

## 局限与注意（v7/R28，2026-11-02）

以下是各 **subdimension cell** 的 0–10 分描述统计，取自 `reports/atomic_ability_rebenchmark/13_mapping_validation_cells.jsonl`。n 是该 cell 实际可用的模型数，不是全家族统一面板；不同 cell 的面板不完全相同，配对分析另取共同模型。它们是分任务证据，不是 BHI 排名，也不能用 BHI 排名代替。

| 计分 cell | n | mean | SD | min–max | 当前标记 |
|---|---:|---:|---:|---:|---|
| problem_solving | 9 | 9.670 | 0.112 | 9.477–9.803 | ceiling + low_variance |
| solution_correctness | 9 | 8.720 | 0.134 | 8.567–8.952 | ceiling + low_variance |
| mistake_location | 9 | 7.707 | 0.138 | 7.450–7.919 | low_variance |
| mistake_correction | 9 | 8.993 | 0.395 | 8.303–9.421 | ceiling + low_variance |
| socratic_questioning | 8 | 2.801 | 0.339 | 2.131–3.226 | low_variance |
| pedagogy | 10 | 8.045 | 0.619 | 6.935–8.670 | 未标记方差受限 |
| pedagogy_hard | 10 | 7.642 | 0.866 | 6.284–8.639 | 未标记方差受限 |
| scaffolding | 10 | 2.858 | 1.565 | 1.100–5.948 | 未标记方差受限 |
| scaffolding_hard | 10 | 2.631 | 1.394 | 1.101–5.612 | 未标记方差受限 |

- 五个带标记的 cell 均为 `variance_restricted`。按 13 号检查规则，任一侧受限的配对不进入构念裁决；因此不能用这些配对的相关值证明或否定映射，优先动作仍是提高难度或更换切分。socratic 是低均值但低方差，不应把低分写成天花板。
- scaffolding 两个 cell 在家族内离散度最高，pedagogy_hard 的 SD 也高于常规版；这些结论只描述当前面板，不能由 SD 外推全体系区分度排名。未标记方差受限也不等于已完成效度验证。
- win-rate 类分数依赖裁判，且与参考回复风格相关；SacreBLEU 对短问句也是弱指标。

## 当前映射（v7/R28）

- 九个计分 cell 均已进入当前映射，权重以 `data/mapping_measurement_model_v7.json` 和上述 cell 数据为准。socratic_questioning 已挂 P15 与 P17，不再是“本地跑过但待补挂”的状态。
- 解题与诊断侧分别覆盖 P02/P05/P06/P07/P11；P11 内仍是 answer_verdict（判对）、error_location（定位）、error_attribution（纠错）三个 facet。开放辅导侧挂 P15 strategy_enactment 与 P17 content_feedback；scaffolding/pedagogy 及其 hard 变体另有 P05 pedagogical_knowledge 弱信号。
