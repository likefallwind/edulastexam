# Judge Views

一个判官一套完整结果。评测场切判官时,读的是这里。

主产物(`09_*` / `10_*`)是 **MiniMax-M3** 的视图。

完整性的分母**按判官算**:判官读不了图就判不了 eduillustrate,那些格从它的分母里
扣掉(`judge_incapable`),不是待办。判据是取分行存在,不是目录存在——目录里的冒烟
跑分会被「样本<100」地板剔掉,只看目录会把它误判成已覆盖。

| 判官 | 覆盖 | 可达 | 状态 | 判不了的 benchmark | 自评格 |
|---|---:|---:|---|---|---:|
| `MiniMax-M3` (主) | 213 | 237 | 缺 24 | — | 50 |
| `deepseek-v4-flash` | 205 | 233 | 缺 28 | eduillustrate | 0 |
| `deepseek-v3.2` | 60 | 237 | 缺 177 | — | 0 |
| `MiniMax-M2.7` | 3 | 237 | 缺 234 | — | 0 |

**自评格**:判官就是被测模型本人。多判官的意义正是防「模型给自己打分打高」,
所以自评格必须标出来(证据行的 `self_judged`),但不能剔除——剔了该判官的视图就不完整。

## `MiniMax-M3` 还缺 24 格

- age_values_v1 · A/core content-and-handling pass rate · deepseek-v4-pro
- age_values_v1 · A/core content-and-handling pass rate · doubao-seed-2-0-pro
- age_values_v1 · A/core content-and-handling pass rate · glm-5.2
- age_values_v1 · A/core content-and-handling pass rate · minimax-m2.7
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-5-4b
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-8-27b
- age_values_v1 · B four-category equal-weight content pass rate · deepseek-v4-pro
- age_values_v1 · B four-category equal-weight content pass rate · doubao-seed-2-0-pro
- age_values_v1 · B four-category equal-weight content pass rate · glm-5.2
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m2.7
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-5-4b
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-8-27b
- education_boundary_v1 · Role boundary gate accuracy · deepseek-v4-pro
- education_boundary_v1 · Role boundary gate accuracy · doubao-seed-2-0-pro
- education_boundary_v1 · Role boundary gate accuracy · glm-5.2
- education_boundary_v1 · Role boundary gate accuracy · minimax-m2.7
- education_boundary_v1 · Role boundary gate accuracy · qwen-qwen3-5-4b
- education_boundary_v1 · Role boundary gate accuracy · qwen-qwen3-8-27b
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · deepseek-v4-pro
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · doubao-seed-2-0-pro
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · glm-5.2
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · minimax-m2.7
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · qwen-qwen3-5-4b
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · qwen-qwen3-8-27b

## `deepseek-v4-flash` 还缺 28 格

- age_values_v1 · A/core content-and-handling pass rate · deepseek-v4-pro
- age_values_v1 · A/core content-and-handling pass rate · doubao-seed-2-0-pro
- age_values_v1 · A/core content-and-handling pass rate · glm-5.2
- age_values_v1 · A/core content-and-handling pass rate · minimax-m2.7
- age_values_v1 · A/core content-and-handling pass rate · minimax-m3
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-5-4b
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-8-27b
- age_values_v1 · B four-category equal-weight content pass rate · deepseek-v4-pro
- age_values_v1 · B four-category equal-weight content pass rate · doubao-seed-2-0-pro
- age_values_v1 · B four-category equal-weight content pass rate · glm-5.2
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m2.7
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m3
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-5-4b
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-8-27b
- education_boundary_v1 · Role boundary gate accuracy · deepseek-v4-pro
- education_boundary_v1 · Role boundary gate accuracy · doubao-seed-2-0-pro
- education_boundary_v1 · Role boundary gate accuracy · glm-5.2
- education_boundary_v1 · Role boundary gate accuracy · minimax-m2.7
- education_boundary_v1 · Role boundary gate accuracy · minimax-m3
- education_boundary_v1 · Role boundary gate accuracy · qwen-qwen3-5-4b
- education_boundary_v1 · Role boundary gate accuracy · qwen-qwen3-8-27b
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · deepseek-v4-pro
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · doubao-seed-2-0-pro
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · glm-5.2
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · minimax-m2.7
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · minimax-m3
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · qwen-qwen3-5-4b
- student_risk_v2 · Risk recognition-response joint accuracy (provisional) · qwen-qwen3-8-27b

## `deepseek-v3.2` 还缺 177 格

- age_values_v1 · A/core content-and-handling pass rate · deepseek-v4-pro
- age_values_v1 · A/core content-and-handling pass rate · doubao-seed-2-0-pro
- age_values_v1 · A/core content-and-handling pass rate · glm-5.2
- age_values_v1 · A/core content-and-handling pass rate · minimax-m2.7
- age_values_v1 · A/core content-and-handling pass rate · minimax-m3
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-5-4b
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-8-27b
- age_values_v1 · B four-category equal-weight content pass rate · deepseek-v4-pro
- age_values_v1 · B four-category equal-weight content pass rate · doubao-seed-2-0-pro
- age_values_v1 · B four-category equal-weight content pass rate · glm-5.2
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m2.7
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m3
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-5-4b
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Actionability · deepseek-v4-pro
- bea2025_tutor · dimension: Actionability · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Actionability · glm-5.2
- bea2025_tutor · dimension: Actionability · minimax-m2.7
- bea2025_tutor · dimension: Actionability · minimax-m3
- bea2025_tutor · dimension: Actionability · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Actionability · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Mistake_Identification · deepseek-v4-pro
- bea2025_tutor · dimension: Mistake_Identification · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Mistake_Identification · glm-5.2
- bea2025_tutor · dimension: Mistake_Identification · minimax-m2.7
- bea2025_tutor · dimension: Mistake_Identification · minimax-m3
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Providing_Guidance · deepseek-v4-pro
- bea2025_tutor · dimension: Providing_Guidance · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Providing_Guidance · glm-5.2
- bea2025_tutor · dimension: Providing_Guidance · minimax-m2.7
- bea2025_tutor · dimension: Providing_Guidance · minimax-m3
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-8-27b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-5-4b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-8-27b
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · qwen-qwen3-5-4b
- edubench · QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) · qwen-qwen3-8-27b
- edubench · TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) · qwen-qwen3-5-4b

## `MiniMax-M2.7` 还缺 234 格

- age_values_v1 · A/core content-and-handling pass rate · deepseek-v4-pro
- age_values_v1 · A/core content-and-handling pass rate · doubao-seed-2-0-pro
- age_values_v1 · A/core content-and-handling pass rate · glm-5.2
- age_values_v1 · A/core content-and-handling pass rate · minimax-m2.7
- age_values_v1 · A/core content-and-handling pass rate · minimax-m3
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-5-4b
- age_values_v1 · A/core content-and-handling pass rate · qwen-qwen3-8-27b
- age_values_v1 · B four-category equal-weight content pass rate · deepseek-v4-pro
- age_values_v1 · B four-category equal-weight content pass rate · doubao-seed-2-0-pro
- age_values_v1 · B four-category equal-weight content pass rate · glm-5.2
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m2.7
- age_values_v1 · B four-category equal-weight content pass rate · minimax-m3
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-5-4b
- age_values_v1 · B four-category equal-weight content pass rate · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Actionability · deepseek-v4-pro
- bea2025_tutor · dimension: Actionability · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Actionability · glm-5.2
- bea2025_tutor · dimension: Actionability · minimax-m2.7
- bea2025_tutor · dimension: Actionability · minimax-m3
- bea2025_tutor · dimension: Actionability · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Actionability · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Mistake_Identification · deepseek-v4-pro
- bea2025_tutor · dimension: Mistake_Identification · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Mistake_Identification · glm-5.2
- bea2025_tutor · dimension: Mistake_Identification · minimax-m2.7
- bea2025_tutor · dimension: Mistake_Identification · minimax-m3
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Mistake_Identification · qwen-qwen3-8-27b
- bea2025_tutor · dimension: Providing_Guidance · deepseek-v4-pro
- bea2025_tutor · dimension: Providing_Guidance · doubao-seed-2-0-pro
- bea2025_tutor · dimension: Providing_Guidance · glm-5.2
- bea2025_tutor · dimension: Providing_Guidance · minimax-m2.7
- bea2025_tutor · dimension: Providing_Guidance · minimax-m3
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-5-4b
- bea2025_tutor · dimension: Providing_Guidance · qwen-qwen3-8-27b
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · deepseek-v4-pro
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · doubao-seed-2-0-pro
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · glm-5.2
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · minimax-m2.7
- edubench · QG × clarity_concision_inspiration + scenario_element_integration (task×metric) · minimax-m3

