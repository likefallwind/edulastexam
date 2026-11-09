# MRBench

**一句话**：AI tutor 回复的 8 维人工标注基准（NAACL 2025 *Unifying AI Tutor Evaluation*）——200 段学生犯错对话 × 至多 9 个模型的 tutor 回复，每条人工标 8 个教学维度。

## 出处与背景

- Maurya、Kochmar 等（MBZUAI），NAACL 2025；repo `kaushal0494/UnifyingAITutorEvaluation`，数据 `MRBench/MRBench_V2.json`。
- 动机：把 tutor 回复质量的评价维度统一成一个分类学（后来直接衍生出 BEA 2025 共享任务）。

## 数据

- 200 段对话（源自 MathDial + Bridge，真实学生数学错误），每段配至多 9 个 tutor 模型的回复，人工标注 8 维。英文。
- 获取：`fetch_eval_datasets.py --benchmark mrbench`（urllib 直下）。

## 任务与判分

- 8 个原生维度：Mistake Identification / Mistake Location / Revealing of the Answer（No / Yes-correct / Yes-incorrect）/ Providing Guidance / Actionability / Coherence / Tutor Tone（鼓励/中性/冒犯）/ Humanlikeness。
- 两个 adapter：
  - **mrbench_judge**：被测模型当裁判逐维贴标签，与人类金标算一致率 + macro-F1 + kappa（测"这个模型做裁判有多像人"）；
  - **mrbench_tutor**：被测模型生成下一句 tutor 回复，固定裁判（`MRBENCH_JUDGE_MODEL`，默认 MiniMax-M3）标 8 维；headline = 关键三维（MI/PG/Actionability）全 Yes 的 pass rate，全部维度分布在 `extra_metrics`。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：mrbench_tutor 四个当前计分格均为 n=8：Mistake_Identification 均分/SD=9.223/0.293、Providing_Guidance 8.974/0.274、Actionability 9.170/0.373，三者均为 ceiling + low_variance；Tutor_Tone (encouraging share) 8.497/1.404，未受限。mrbench_judge 的 8-dimension tutor response judging 格 n=10、均分/SD=5.287/0.539，未受限。旧 tutor 侧 n=3 复合分不再代表当前面板。
- 只有 200 段对话，样本量小，维度级估计噪声大。
- tutor 侧结果依赖固定裁判的标注质量；v7 中 judge 侧已进入 P12 计分，不再标记为 excluded。
- v7 已按单维度分取数，旧复合 pass rate 及其挂载建议只作历史；tutor 的非冒犯占比仅作 P18 related-only sentinel，不参与评分。

## 当前映射

- v7 中 tutor 的识别错误进入 P11，提供引导进入 P15，可执行性与鼓励语气进入 P17；judge 进入 P12。非冒犯语气仅是 P18 的 related-only sentinel，具体 cell 与权重以 v7 JSON 为准。
- 历史构念核对 R2、R3 已落地为单维度取分和 judge 的教学回复评判归属；旧 P 编号及 excluded_judge_task 状态不再适用。
