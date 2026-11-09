# 映射效度检查报告（13 号）

生成脚本：`scripts/build_mapping_validation.py`（幂等）；测量模型：`data/mapping_measurement_model_v7.json`（adjudicated_current）。
规则见 `doc/old/mapping_validation_plan_2026-07-11.md` §2；ρ 一律与 n、90% CI 同格呈现，n<5 的配对只进低置信附录。

覆盖缺口（无任何 benchmark 映射，不参与本报告分析）：P09 工具使用与长程智能体执行、P10 通用安全与合规、P21 公平对待学生。

## Phase 0：天花板/方差受限名单

共 38 / 62 个有证据格子被标记 `variance_restricted`（mean≥8.5 或 n≥4 且 SD<0.5）。这些格子参与的配对**不进入裁决**；优先动作是上难度/换切分，不是改映射。

| Benchmark | Subdimension | n | mean | SD | 标记 |
|---|---|---:|---:|---:|---|
| `mathtutorbench_problem_solving` | Problem Solving | 9 | 9.67 | 0.112 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Providing_Guidance | 8 | 9.604 | 0.229 | ceiling, low_variance |
| `longtutor_evidence` | Information Extraction accuracy | 8 | 9.602 | 0.126 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Mistake_Identification | 8 | 9.223 | 0.293 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Actionability | 8 | 9.221 | 0.38 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Actionability | 8 | 9.17 | 0.373 | ceiling, low_variance |
| `ifeval` | prompt-level strict accuracy | 8 | 9.045 | 0.312 | ceiling, low_variance |
| `mathtutorbench_mistake_correction` | Mistake Correction | 9 | 8.993 | 0.395 | ceiling, low_variance |
| `mrbench_tutor` | dimension: Providing_Guidance | 8 | 8.974 | 0.274 | ceiling, low_variance |
| `edubench` | basic_factual_accuracy (metric) | 7 | 8.942 | 0.363 | ceiling, low_variance |
| `ceval` | overall/category/subject accuracy | 10 | 8.929 | 0.451 | ceiling, low_variance |
| `p08_abstention` | balanced abstention score | 8 | 8.928 | 0.289 | ceiling, low_variance |
| `education_boundary_v1` | Role boundary gate accuracy | 6 | 8.917 | 0.95 | ceiling |
| `age_values_v1` | B four-category equal-weight content pass rate | 6 | 8.909 | 0.497 | ceiling, low_variance |
| `edubench` | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 7 | 8.768 | 0.197 | ceiling, low_variance |
| `mathtutorbench_solution_correctness` | Solution Correctness | 9 | 8.72 | 0.134 | ceiling, low_variance |
| `agieval` | overall/task/language/question_type accuracy | 9 | 8.718 | 0.39 | ceiling, low_variance |
| `bea2025_tutor` | dimension: Mistake_Identification | 8 | 8.55 | 0.32 | ceiling, low_variance |
| `mathvista` | task/question_type/answer_type accuracy | 5 | 8.518 | 0.224 | ceiling, low_variance |
| `mmlu_pro` | overall/category accuracy | 9 | 8.489 | 0.288 | low_variance |
| `edubench` | domain_knowledge_accuracy (metric) | 7 | 8.332 | 0.407 | low_variance |
| `sas_bench` | QWK holistic total score | 11 | 8.298 | 0.242 | low_variance |
| `edubench` | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 7 | 8.134 | 0.408 | low_variance |
| `edubench` | reasoning_process_rigor (metric) | 7 | 8.016 | 0.438 | low_variance |
| `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 7 | 7.908 | 0.136 | low_variance |
| `edubench` | clarity_concision_inspiration (metric) | 7 | 7.831 | 0.296 | low_variance |
| `edubench` | scenario_element_integration (metric) | 7 | 7.755 | 0.272 | low_variance |
| `mathtutorbench_mistake_location` | Mistake Location | 9 | 7.707 | 0.138 | low_variance |
| `sas_bench` | CCS step scoring consistency | 11 | 7.638 | 0.255 | low_variance |
| `k12vista` | math problem-figure subset score | 5 | 7.536 | 0.464 | low_variance |
| `student_risk_v2` | Risk recognition-response joint accuracy (provisional) | 6 | 7.088 | 0.203 | low_variance |
| `edubench` | personalized_adaptation_learning_support (metric) | 7 | 7.087 | 0.374 | low_variance |
| `edubench` | error_identification_correction_accuracy (metric) | 7 | 7.03 | 0.274 | low_variance |
| `edubench` | motivation_guidance_positive_feedback (metric) | 7 | 6.798 | 0.361 | low_variance |
| `longtutor_evidence` | Multi-session Reasoning accuracy | 8 | 6.636 | 0.496 | low_variance |
| `tutorbench` | Fair815 multimodal tutor quality | 6 | 5.478 | 0.25 | low_variance |
| `p07_selfcheck` | two-round self-check (fix/break rate) | 8 | 5.213 | 0.23 | low_variance |
| `mathtutorbench_socratic` | Socratic Questioning | 8 | 2.801 | 0.339 | low_variance |

## 红旗配对（flagged：同 P 预期收敛却 ρ<0，n≥6）

每条 flagged 需人工裁决：改权重 / 拆 facet / 转裁判治理（计划 §2.6）。

（无）

## 观察带（watch：0≤ρ<0.2 且 n≥8）

（无）

## 已验证配对（validated：ρ≥0.5 且 CI 下界>0）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P15(0.5/0.5 异facet) | 9 | 0.962 | 0.567 | 0.0001 | [0.812, 1.0] | validated |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P15(0.5/0.5 异facet) | 9 | 0.937 | 0.4 | 0.0004 | [0.725, 1.0] | validated |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P15(0.5/0.5 异facet) | 9 | 0.87 | 0.616 | 0.0039 | [0.545, 1.0] | validated |
| `mathtutorbench_pedagogy` Pedagogy IF | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P15(0.5/0.8 异facet) | 9 | 0.85 | 0.171 | 0.0068 | [0.526, 0.965] | validated |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5), P15(0.5/0.5 异facet) | 9 | 0.845 | 0.615 | 0.0063 | [0.517, 1.0] | validated |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.2/0.5) | 5 | 0.8 | — | 0.1333 | [0.111, 1.0] | validated |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P15(0.5/0.8 异facet) | 9 | 0.8 | -0.05 | 0.0144 | [0.391, 1.0] | validated |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.2/0.2) | 7 | 0.786 | 0.357 | 0.048 | [0.111, 1.0] | validated |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P15(0.5/0.8 异facet) | 9 | 0.683 | -0.033 | 0.0511 | [0.175, 0.948] | validated |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `mrbench_judge` 8-dimension tutor response judging | P12(0.5/0.5) | 10 | 0.624 | 0.445 | 0.0604 | [0.086, 1.0] | validated |
| `mathtutorbench_scaffolding` Scaffolding | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5), P15(0.5/0.8 异facet) | 9 | 0.617 | -0.149 | 0.084 | [0.119, 0.947] | validated |

## 待定配对（provisional）

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mathtutorbench_scaffolding` Scaffolding | `mmtutorbench` multimodal tutor score | P15(0.5/0.2), P17(0.2/0.5) | 5 | 0.1 | -0.577 | 0.95 | [-1.0, 1.0] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mmtutorbench` multimodal tutor score | P15(0.2/0.2) | 5 | 0.2 | -0.144 | 0.7833 | [-0.875, 1.0] | provisional |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmtutorbench` multimodal tutor score | P15(0.5/0.2), P17(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-1.0, 1.0] | provisional |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmtutorbench` multimodal tutor score | P15(0.5/0.2), P17(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-1.0, 1.0] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding` Scaffolding | P15(0.2/0.5) | 8 | 0.31 | 0.002 | 0.4618 | [-0.615, 0.757] | provisional |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` ECS error-cause consistency | P11(0.2/0.8) | 8 | 0.357 | 0.292 | 0.3894 | [-0.282, 0.78] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P15(0.2/0.5) | 8 | 0.381 | 0.015 | 0.3599 | [-0.291, 0.902] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P15(0.2/0.5) | 8 | 0.405 | 0.144 | 0.3268 | [-0.425, 0.829] | provisional |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_pedagogy` Pedagogy IF | P15(0.2/0.5) | 8 | 0.429 | 0.155 | 0.2992 | [-0.241, 0.899] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `sas_bench` ECS error-cause consistency | P06(0.2/0.2) | 7 | 0.464 | 0.743 | 0.3024 | [-0.321, 0.963] | provisional |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmtutorbench` multimodal tutor score | P15(0.5/0.2), P17(0.2/0.5) | 5 | 0.5 | — | 0.45 | [-0.667, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.2/0.2) | 7 | 0.571 | -0.044 | 0.2 | [-0.148, 0.963] | provisional |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.2/0.2 异facet) | 5 | 0.6 | — | 0.35 | [-0.667, 1.0] | provisional |
| `olympiadbench` overall/subject/language/modality accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 7 | 0.607 | 0.591 | 0.1667 | [-0.208, 0.957] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_scaffolding` Scaffolding | P17(0.2/0.2) | 7 | 0.679 | 0.309 | 0.1095 | [-0.043, 1.0] | provisional |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.2/0.2) | 7 | 0.75 | 0.27 | 0.0663 | [0.0, 1.0] | provisional |

## 因方差受限不裁决的配对

任一侧格子 variance_restricted；其 ρ 不作为构念证据。

| A | B | 共享 P（权重A/B） | n | ρ | 偏ρ(控综合分) | perm p | 90% CI | 评级 |
|---|---|---|---:|---:|---:|---:|---|---|
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Providing_Guidance | P15(0.2/0.2) | 5 | -1.0 | -1.0 | 0.0167 | [-1.0, -1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mmtutorbench` multimodal tutor score | P15(0.2/0.2) | 5 | -0.359 | -0.545 | 0.6333 | [-1.0, 0.875] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mrbench_tutor` dimension: Providing_Guidance | P15(0.5/0.2) | 7 | -0.357 | -0.37 | 0.4444 | [-1.0, 0.556] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mrbench_tutor` dimension: Providing_Guidance | P15(0.2/0.2) | 7 | -0.357 | -0.37 | 0.4444 | [-1.0, 0.556] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 8 | -0.323 | -0.483 | 0.4329 | [-0.918, 0.63] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.2/0.2) | 7 | -0.286 | -0.593 | 0.556 | [-0.962, 0.623] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p07_selfcheck` two-round self-check (fix/break rate) | P07(0.2/0.8) | 8 | -0.238 | -0.462 | 0.5821 | [-0.802, 0.468] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` basic_factual_accuracy (metric) | P05(0.5/0.2) | 7 | -0.179 | -0.256 | 0.7131 | [-1.0, 0.647] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `mrbench_tutor` dimension: Mistake_Identification | P11(0.2/0.2) | 7 | -0.179 | -0.279 | 0.7131 | [-0.957, 0.731] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 6 | -0.143 | -0.18 | 0.8028 | [-0.818, 0.818] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P15(0.5/0.2) | 7 | -0.143 | -0.449 | 0.7825 | [-0.75, 0.654] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P15(0.2/0.2) | 7 | -0.143 | -0.449 | 0.7825 | [-0.698, 0.63] | variance_restricted |
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Actionability | P17(0.5/0.2) | 5 | -0.051 | -0.286 | 1.0 | [-1.0, 0.875] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mrbench_tutor` dimension: Providing_Guidance | P15(0.2/0.2) | 8 | -0.024 | -0.037 | 0.9768 | [-0.78, 0.654] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | P15(0.2/0.2) | 8 | -0.012 | -0.144 | 0.9887 | [-0.568, 0.739] | variance_restricted |
| `longtutor_evidence` Hallucination Check accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 8 | 0.024 | -0.107 | 0.9768 | [-0.846, 0.753] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 7 | 0.036 | 0.166 | 0.9635 | [-0.852, 0.769] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 7 | 0.037 | -0.208 | 0.9738 | [-0.765, 0.957] | variance_restricted |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.8/0.2), P08(0.2/0.8) | 8 | 0.048 | -0.185 | 0.9349 | [-0.753, 0.842] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `edubench` error_identification_correction_accuracy (metric) | P11(0.2/0.2) | 7 | 0.071 | -0.299 | 0.9063 | [-0.769, 0.87] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P17(0.2/0.2) | 7 | 0.071 | -0.675 | 0.9063 | [-0.647, 0.765] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P11(0.2/0.2) | 7 | 0.071 | -0.184 | 0.9063 | [-0.68, 0.852] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 7 | 0.071 | -0.417 | 0.9063 | [-0.75, 0.882] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2) | 6 | 0.086 | -0.135 | 0.9194 | [-0.818, 0.939] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 7 | 0.09 | -0.126 | 0.8587 | [-0.852, 0.99] | variance_restricted |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_correction` Mistake Correction | P11(0.2/0.2) | 8 | 0.119 | -0.389 | 0.793 | [-0.519, 0.683] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P11(0.2/0.2) | 7 | 0.143 | -0.681 | 0.7825 | [-0.647, 1.0] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` ECS error-cause consistency | P06(0.2/0.2), P11(0.2/0.8) | 8 | 0.143 | -0.164 | 0.752 | [-0.683, 0.781] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Providing_Guidance | P15(0.5/0.2) | 8 | 0.143 | 0.325 | 0.752 | [-0.615, 0.976] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Providing_Guidance | P15(0.5/0.2) | 8 | 0.143 | 0.211 | 0.752 | [-0.519, 0.671] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 8 | 0.19 | -0.113 | 0.6646 | [-0.519, 0.671] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Providing_Guidance | P15(0.5/0.2) | 8 | 0.19 | 0.55 | 0.6646 | [-0.595, 0.926] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.195 | -0.342 | 0.6497 | [-0.478, 0.728] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_socratic` Socratic Questioning | P17(0.2/0.2) | 7 | 0.214 | -0.166 | 0.6615 | [-0.608, 0.882] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P15(0.5/0.5) | 7 | 0.214 | -0.535 | 0.6615 | [-0.556, 0.808] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P15(0.2/0.5) | 7 | 0.214 | -0.535 | 0.6615 | [-0.556, 0.765] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` personalized_adaptation_learning_support (metric) | P15(0.2/0.5) | 7 | 0.218 | 0.026 | 0.6365 | [-0.748, 0.887] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `edubench` scenario_element_integration (metric) | P15(0.2/0.2) | 7 | 0.218 | 0.026 | 0.6365 | [-0.757, 0.887] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy` Pedagogy IF | P15(0.2/0.5) | 8 | 0.246 | -0.08 | 0.553 | [-0.547, 0.81] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 7 | 0.259 | 0.361 | 0.5976 | [-0.522, 0.99] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P11(0.2/0.8) | 8 | 0.262 | 0.172 | 0.5364 | [-0.481, 0.797] | variance_restricted |
| `mmlu_pro` overall/category accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 8 | 0.262 | 0.068 | 0.5364 | [-0.538, 0.902] | variance_restricted |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mrbench_tutor` dimension: Mistake_Identification | P11(0.2/0.2) | 8 | 0.275 | 0.251 | 0.507 | [-0.453, 0.924] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 7 | 0.286 | -0.237 | 0.556 | [-0.608, 0.923] | variance_restricted |
| `edubench` basic_factual_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 7 | 0.286 | 0.284 | 0.556 | [-0.647, 0.961] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.2/0.2) | 7 | 0.286 | -0.04 | 0.556 | [-0.412, 0.961] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.293 | -0.273 | 0.4893 | [-0.607, 0.846] | variance_restricted |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.293 | -0.368 | 0.4893 | [-0.506, 0.826] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 8 | 0.293 | 0.166 | 0.4905 | [-0.575, 0.936] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mmtutorbench` multimodal tutor score | P17(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-1.0, 1.0] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mmtutorbench` multimodal tutor score | P15(0.5/0.2), P17(0.2/0.5) | 5 | 0.3 | -0.397 | 0.6833 | [-0.875, 1.0] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 7 | 0.306 | -0.101 | 0.5119 | [-0.972, 0.882] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_correction` Mistake Correction | P11(0.2/0.2) | 8 | 0.31 | -0.124 | 0.4618 | [-0.385, 0.846] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.2/0.2) | 7 | 0.321 | -0.071 | 0.4976 | [-0.565, 0.889] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_scaffolding` Scaffolding | P15(0.5/0.5) | 7 | 0.321 | -0.202 | 0.4976 | [-0.434, 0.882] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_scaffolding` Scaffolding | P15(0.2/0.5) | 7 | 0.321 | -0.202 | 0.4976 | [-0.412, 0.885] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Mistake_Identification | P11(0.2/0.2) | 8 | 0.323 | 0.432 | 0.4344 | [-0.453, 0.905] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.342 | 0.043 | 0.4146 | [-0.331, 0.753] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_socratic` Socratic Questioning | P15(0.5/0.5) | 7 | 0.357 | -0.244 | 0.4444 | [-0.412, 0.887] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_socratic` Socratic Questioning | P15(0.2/0.5) | 7 | 0.357 | -0.244 | 0.4444 | [-0.373, 0.887] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding_hard` Scaffolding hard | P15(0.2/0.5) | 8 | 0.381 | 0.27 | 0.3554 | [-0.239, 0.774] | variance_restricted |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmtutorbench` multimodal tutor score | P17(0.2/0.5) | 5 | 0.4 | 0.081 | 0.5167 | [-0.875, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P15(0.2/0.5) | 8 | 0.405 | 0.401 | 0.3179 | [-0.377, 0.923] | variance_restricted |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` CCS step scoring consistency | P12(0.5/0.5) | 8 | 0.405 | 0.35 | 0.3268 | [-0.342, 0.924] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.415 | 0.148 | 0.3196 | [-0.192, 0.777] | variance_restricted |
| `ceval` overall/category/subject accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.5/0.2), P06(0.2/0.5) | 7 | 0.429 | 0.261 | 0.3536 | [-0.333, 0.961] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.2/0.2) | 7 | 0.429 | 0.204 | 0.3536 | [-0.385, 0.963] | variance_restricted |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` ECS error-cause consistency | P11(0.2/0.8) | 7 | 0.429 | 0.503 | 0.3536 | [-0.407, 0.962] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_socratic` Socratic Questioning | P15(0.2/0.5) | 8 | 0.43 | 0.357 | 0.2911 | [-0.314, 0.813] | variance_restricted |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.439 | 0.16 | 0.2875 | [-0.288, 0.926] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mathtutorbench_scaffolding` Scaffolding | P15(0.2/0.5) | 8 | 0.442 | 0.365 | 0.2756 | [-0.113, 0.841] | variance_restricted |
| `ceval` overall/category/subject accuracy | `sas_bench` ECS error-cause consistency | P05(0.5/0.2), P06(0.2/0.2 异facet) | 8 | 0.452 | 0.584 | 0.2675 | [-0.235, 0.846] | variance_restricted |
| `edubench` clarity_concision_inspiration (metric) | `mathtutorbench_scaffolding` Scaffolding | P17(0.2/0.2) | 7 | 0.464 | 0.285 | 0.3024 | [-0.231, 0.961] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `sas_bench` ECS error-cause consistency | P05(0.2/0.2) | 7 | 0.464 | 0.743 | 0.3024 | [-0.321, 0.963] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P15(0.5/0.5) | 7 | 0.464 | -0.217 | 0.3024 | [-0.538, 1.0] | variance_restricted |
| `edubench` reasoning_process_rigor (metric) | `sas_bench` ECS error-cause consistency | P06(0.5/0.2) | 7 | 0.464 | 0.743 | 0.3024 | [-0.261, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P15(0.2/0.5) | 7 | 0.464 | -0.217 | 0.3024 | [-0.565, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2) | 7 | 0.482 | 0.118 | 0.2952 | [-0.522, 0.887] | variance_restricted |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` ECS error-cause consistency | P11(0.2/0.8) | 8 | 0.491 | 0.48 | 0.222 | [-0.137, 0.848] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_socratic` Socratic Questioning | P17(0.2/0.2) | 7 | 0.5 | -0.218 | 0.2667 | [-0.333, 0.961] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` SEND special education needs selection | P14(0.2/0.2), P15(0.5/0.5 异facet) | 7 | 0.523 | -0.243 | 0.2397 | [-0.214, 0.97] | variance_restricted |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2), P17(0.2/0.2) | 7 | 0.536 | -0.45 | 0.2357 | [-0.261, 1.0] | variance_restricted |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2) | 7 | 0.536 | -0.45 | 0.2357 | [-0.333, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Providing_Guidance | `mrbench_tutor` dimension: Providing_Guidance | P15(0.2/0.2) | 8 | 0.54 | 0.556 | 0.1756 | [-0.139, 0.883] | variance_restricted |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Providing_Guidance | P15(0.5/0.2) | 8 | 0.548 | 0.9 | 0.171 | [-0.231, 0.975] | variance_restricted |
| `mathtutorbench_solution_correctness` Solution Correctness | `p08_calibration` calibration composite (CWR/AUROC) | P07(0.2/0.2) | 8 | 0.548 | 0.101 | 0.171 | [-0.162, 0.9] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 8 | 0.554 | 0.484 | 0.1605 | [-0.151, 0.96] | variance_restricted |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.2/0.5) | 5 | 0.564 | — | 0.4 | [-0.791, 1.0] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.5/0.5) | 5 | 0.564 | — | 0.4 | [-0.913, 1.0] | variance_restricted |
| `edubench` personalized_adaptation_learning_support (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P15(0.5/0.5) | 7 | 0.571 | -0.067 | 0.2 | [-0.185, 1.0] | variance_restricted |
| `edubench` scenario_element_integration (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P15(0.2/0.5) | 7 | 0.571 | -0.067 | 0.2 | [-0.261, 1.0] | variance_restricted |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `mathtutorbench_socratic` Socratic Questioning | P15(0.2/0.5) | 8 | 0.571 | 0.454 | 0.1511 | [-0.22, 0.975] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.5/0.2), P06(0.2/0.5) | 9 | 0.593 | 0.406 | 0.1039 | [-0.08, 0.928] | variance_restricted |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Providing_Guidance | P15(0.5/0.2) | 8 | 0.595 | 0.891 | 0.1323 | [-0.063, 1.0] | variance_restricted |
| `mathvista` task/question_type/answer_type accuracy | `sas_bench` ECS error-cause consistency | P05(0.2/0.2), P06(0.5/0.2 异facet) | 5 | 0.6 | — | 0.35 | [-0.667, 1.0] | variance_restricted |
| `edubench` domain_knowledge_accuracy (metric) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5) | 7 | 0.607 | -0.024 | 0.1667 | [-0.125, 1.0] | variance_restricted |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.5/0.2) | 7 | 0.643 | 0.563 | 0.1389 | [-0.094, 0.923] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_problem_solving` Problem Solving | P05(0.2/0.2), P06(0.5/0.5) | 9 | 0.644 | 0.498 | 0.0688 | [0.026, 0.943] | variance_restricted |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Actionability | P17(0.2/0.2) | 8 | 0.659 | 0.605 | 0.0881 | [-0.025, 0.929] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `mrbench_tutor` dimension: Mistake_Identification | P11(0.2/0.2) | 8 | 0.683 | 0.704 | 0.0701 | [-0.076, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Mistake_Identification | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P11(0.2/0.2) | 8 | 0.69 | 0.637 | 0.0694 | [0.062, 0.95] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `mathtutorbench_mistake_location` Mistake Location | P02(0.8/0.2) | 8 | 0.707 | 0.699 | 0.0586 | [0.205, 0.975] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `edubench` clarity_concision_inspiration (metric) | P17(0.2/0.2) | 7 | 0.714 | 0.878 | 0.0881 | [-0.087, 0.957] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.2/0.2) | 8 | 0.714 | -0.172 | 0.0576 | [0.215, 0.926] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_mistake_correction` Mistake Correction | P17(0.2/0.2) | 8 | 0.738 | -0.302 | 0.0458 | [0.225, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_scaffolding` Scaffolding | P17(0.2/0.2) | 8 | 0.738 | 0.127 | 0.0458 | [0.291, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.2/0.2) | 7 | 0.75 | 0.218 | 0.0663 | [0.111, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `edubench` domain_knowledge_accuracy (metric) | P05(0.5/0.2) | 7 | 0.75 | 0.27 | 0.0663 | [0.0, 1.0] | variance_restricted |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` CCS step scoring consistency | P02(0.2/0.2), P11(0.8/0.2) | 8 | 0.755 | 0.718 | 0.0361 | [0.308, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_socratic` Socratic Questioning | P17(0.2/0.2) | 8 | 0.762 | 0.047 | 0.0368 | [0.297, 1.0] | variance_restricted |
| `mathtutorbench_problem_solving` Problem Solving | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 9 | 0.763 | 0.725 | 0.0212 | [0.346, 0.964] | variance_restricted |
| `k12vista` math problem-figure subset score | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2) | 5 | 0.8 | — | 0.1333 | [0.111, 1.0] | variance_restricted |
| `mathvista` task/question_type/answer_type accuracy | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2) | 5 | 0.8 | — | 0.1333 | [0.111, 1.0] | variance_restricted |
| `mathvista` task/question_type/answer_type accuracy | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2), P06(0.5/0.5) | 5 | 0.8 | — | 0.1333 | [0.111, 1.0] | variance_restricted |
| `longtutor_evidence` Multi-session Reasoning accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 8 | 0.81 | 0.831 | 0.0218 | [0.317, 1.0] | variance_restricted |
| `longtutor_evidence` Information Extraction accuracy | `sas_bench` CCS step scoring consistency | P02(0.8/0.2) | 8 | 0.826 | 0.796 | 0.0167 | [0.316, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.2/0.2) | 8 | 0.833 | -0.21 | 0.0154 | [0.316, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.2/0.2) | 8 | 0.881 | -0.03 | 0.0072 | [0.538, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 9 | 0.9 | 0.733 | 0.0023 | [0.59, 1.0] | variance_restricted |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` CCS step scoring consistency | P12(0.5/0.5) | 8 | 0.905 | 0.895 | 0.0046 | [0.62, 1.0] | variance_restricted |
| `bea2025_tutor` dimension: Actionability | `edubench` higher_order_thinking_ability_development (metric) | P17(0.2/0.2) | 7 | 0.929 | 0.869 | 0.0067 | [0.68, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `ceval` overall/category/subject accuracy | P05(0.2/0.5), P06(0.5/0.2) | 9 | 0.933 | 0.817 | 0.0013 | [0.725, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mmlu_pro` overall/category accuracy | P05(0.5/0.5), P06(0.2/0.2) | 9 | 0.933 | 0.804 | 0.0007 | [0.692, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2), P06(0.5/0.2) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `agieval` overall/task/language/question_type accuracy | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.5/0.5) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.5/0.2), P06(0.2/0.2) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `ceval` overall/category/subject accuracy | `mathvista` task/question_type/answer_type accuracy | P05(0.5/0.2), P06(0.2/0.5) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `k12vista` math problem-figure subset score | `mathvista` task/question_type/answer_type accuracy | P03(0.5/0.5) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2), P06(0.2/0.5) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.2/0.2) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |
| `mathvista` task/question_type/answer_type accuracy | `mmlu_pro` overall/category accuracy | P05(0.2/0.5), P06(0.5/0.2) | 5 | 1.0 | — | 0.0167 | [1.0, 1.0] | variance_restricted |

## 区分效度（同 P 收敛配对 vs 不共享 P 的 baseline）

- 收敛配对（跨家族、非受限、n≥5）：27 对，mean ρ = 0.582，median = 0.607
- baseline（不共享任何 P）：138 对，mean ρ = 0.354，median = 0.393
- 差值 = 0.229，单侧 permutation p = 0.0015（配对之间共享格子、非独立；p 值仅供参考，结论以红旗/非红旗为主。）

若差值不显著为正，说明 P 划分对'哪些 benchmark 相关'没有预测力，映射层需整体重审。

## 家族方法方差（halo）

| 家族 | 家族内配对数 | 家族内 mean ρ | 跨家族配对数 | 跨家族 mean ρ | halo 分 | 家族内先聚合? |
|---|---:|---:|---:|---:|---:|---|
| `olympiadbench` | 1 | 1.0 | 94 | 0.355 | 0.645 | 是 |
| `edubench` | 66 | 0.786 | 444 | 0.211 | 0.575 | 是 |
| `k12vista` | 3 | 1.0 | 120 | 0.573 | 0.427 | 否 |
| `pedagogy_benchmark` | 1 | 0.902 | 108 | 0.517 | 0.385 | 否 |
| `age_values_v1` | 1 | 0.6 | 4 | 0.386 | 0.214 | 否 |
| `mathtutorbench` | 36 | 0.601 | 418 | 0.413 | 0.188 | 否 |
| `p08` | 1 | 0.323 | 106 | 0.236 | 0.087 | 否 |
| `longtutor_evidence` | 3 | 0.351 | 156 | 0.268 | 0.083 | 否 |
| `bea2025` | 6 | 0.416 | 204 | 0.387 | 0.029 | 否 |
| `sas_bench` | 3 | 0.224 | 156 | 0.266 | -0.041 | 否 |
| `mrbench` | 10 | -0.045 | 250 | 0.2 | -0.245 | 否 |

halo 分 > 0.5 的家族：多子维度在 P 聚合前先合成一票（计划 §2.6）。

## P × 格子评级汇总

评级分布：validated=14、provisional=15、variance_restricted=52、insufficient_evidence=13、single_source=6

| P | 类型 | facet | Benchmark | Subdimension | 权重 | 评级 |
|---|---|---|---|---|---:|---|
| P01 指令与约束遵循 | reflective | core | `ifeval` | prompt-level strict accuracy | 1.0 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Hallucination Check accuracy | 0.8 | **insufficient_evidence** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Information Extraction accuracy | 0.8 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `longtutor_evidence` | Multi-session Reasoning accuracy | 0.8 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `mathtutorbench_mistake_location` | Mistake Location | 0.2 | **variance_restricted** |
| P02 长上下文与证据定位 | reflective | core | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P03 多模态理解 | formative | subject_charts | `k12vista` | science/geo subject-chart subset score | 0.5 | **insufficient_evidence** |
| P03 多模态理解 | formative | mixed_materials | `mmtutorbench` | multimodal tutor score | 0.2 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `olympiadbench` | multimodal-subset accuracy | 0.2 | **insufficient_evidence** |
| P03 多模态理解 | formative | problem_images | `k12vista` | math problem-figure subset score | 0.5 | **variance_restricted** |
| P03 多模态理解 | formative | problem_images | `mathvista` | task/question_type/answer_type accuracy | 0.5 | **variance_restricted** |
| P03 多模态理解 | formative | mixed_materials | `tutorbench` | Fair815 multimodal tutor quality | 0.2 | **variance_restricted** |
| P04 多模态生成 | formative | static_visual | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.5 | **single_source** |
| P05 知识调用与掌握 | formative | subject_knowledge | `sas_bench` | ECS error-cause consistency | 0.2 | **provisional** |
| P05 知识调用与掌握 | formative | subject_knowledge | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | subject_knowledge | `olympiadbench` | overall/subject/language/modality accuracy | 0.2 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.5 | **validated** |
| P05 知识调用与掌握 | formative | pedagogical_knowledge | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **validated** |
| P05 知识调用与掌握 | formative | subject_knowledge | `agieval` | overall/task/language/question_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `ceval` | overall/category/subject accuracy | 0.5 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | basic_factual_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `edubench` | domain_knowledge_accuracy (metric) | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathtutorbench_problem_solving` | Problem Solving | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mathvista` | task/question_type/answer_type accuracy | 0.2 | **variance_restricted** |
| P05 知识调用与掌握 | formative | subject_knowledge | `mmlu_pro` | overall/category accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **provisional** |
| P06 推理与生成 | formative | generative_reasoning | `sas_bench` | ECS error-cause consistency | 0.2 | **provisional** |
| P06 推理与生成 | formative | problem_reasoning | `k12vista` | official partial-credit score (per-blank 0/1 mean) | 0.2 | **validated** |
| P06 推理与生成 | formative | problem_reasoning | `olympiadbench` | overall/subject/language/modality accuracy | 0.5 | **validated** |
| P06 推理与生成 | formative | problem_reasoning | `agieval` | overall/task/language/question_type accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `ceval` | overall/category/subject accuracy | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `edubench` | reasoning_process_rigor (metric) | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | generative_reasoning | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathtutorbench_problem_solving` | Problem Solving | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mathvista` | task/question_type/answer_type accuracy | 0.5 | **variance_restricted** |
| P06 推理与生成 | formative | problem_reasoning | `mmlu_pro` | overall/category accuracy | 0.2 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p08_calibration` | calibration composite (CWR/AUROC) | 0.2 | **insufficient_evidence** |
| P07 自我校验与修正 | reflective | core | `mathtutorbench_solution_correctness` | Solution Correctness | 0.2 | **variance_restricted** |
| P07 自我校验与修正 | reflective | core | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.8 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | calibration | `p08_calibration` | calibration composite (CWR/AUROC) | 0.8 | **insufficient_evidence** |
| P08 置信度校准与弃答 | formative | calibration | `p07_selfcheck` | two-round self-check (fix/break rate) | 0.2 | **variance_restricted** |
| P08 置信度校准与弃答 | formative | abstention | `p08_abstention` | balanced abstention score | 0.8 | **variance_restricted** |
| P11 错误诊断 | formative | error_attribution | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.2 | **provisional** |
| P11 错误诊断 | formative | error_attribution | `sas_bench` | ECS error-cause consistency | 0.8 | **provisional** |
| P11 错误诊断 | formative | error_attribution | `bea2025_tutor` | dimension: Mistake_Identification | 0.2 | **variance_restricted** |
| P11 错误诊断 | formative | error_attribution | `edubench` | error_identification_correction_accuracy (metric) | 0.2 | **variance_restricted** |
| P11 错误诊断 | formative | error_attribution | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P11 错误诊断 | formative | error_location | `mathtutorbench_mistake_location` | Mistake Location | 0.8 | **variance_restricted** |
| P11 错误诊断 | formative | answer_verdict | `mathtutorbench_solution_correctness` | Solution Correctness | 0.5 | **variance_restricted** |
| P11 错误诊断 | formative | error_attribution | `mrbench_tutor` | dimension: Mistake_Identification | 0.2 | **variance_restricted** |
| P11 错误诊断 | formative | error_location | `sas_bench` | CCS step scoring consistency | 0.2 | **variance_restricted** |
| P12 主观题评价能力 | formative | holistic_scoring | `asap_2` | essay holistic QWK | 0.8 | **insufficient_evidence** |
| P12 主观题评价能力 | formative | analytic_scoring | `bea2025_judge` | judge labels: mistake/guidance/actionability | 0.5 | **validated** |
| P12 主观题评价能力 | formative | analytic_scoring | `mrbench_judge` | 8-dimension tutor response judging | 0.5 | **validated** |
| P12 主观题评价能力 | formative | analytic_scoring | `sas_bench` | CCS step scoring consistency | 0.5 | **variance_restricted** |
| P12 主观题评价能力 | formative | holistic_scoring | `sas_bench` | QWK holistic total score | 0.8 | **variance_restricted** |
| P13 命题与作业设计 | formative | item_generation | `edubench` | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.5 | **variance_restricted** |
| P13 命题与作业设计 | formative | item_generation | `edubench` | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 0.2 | **variance_restricted** |
| P14 学习者画像建模 | formative | knowledge_state_estimation | `longtutor_diagnosis` | four-category knowledge-state diagnosis macro-F1 | 0.8 | **insufficient_evidence** |
| P14 学习者画像建模 | formative | support_needs | `pedagogy_benchmark` | SEND special education needs selection | 0.2 | **insufficient_evidence** |
| P14 学习者画像建模 | formative | support_needs | `edubench` | personalized_adaptation_learning_support (metric) | 0.2 | **variance_restricted** |
| P15 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | CDPK teaching knowledge selection | 0.8 | **insufficient_evidence** |
| P15 个性化教学策略选择 | formative | strategy_formulation | `pedagogy_benchmark` | SEND special education needs selection | 0.5 | **insufficient_evidence** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `longtutor_teaching` | judge dims: strategy_alignment + history_utilization (1-5) | 0.2 | **provisional** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy` | Pedagogy IF | 0.5 | **provisional** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.5 | **provisional** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding` | Scaffolding | 0.5 | **provisional** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.5 | **provisional** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mmtutorbench` | multimodal tutor score | 0.2 | **provisional** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `bea2025_tutor` | dimension: Providing_Guidance | 0.2 | **variance_restricted** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `edubench` | personalized_adaptation_learning_support (metric) | 0.5 | **variance_restricted** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `edubench` | scenario_element_integration (metric) | 0.2 | **variance_restricted** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mathtutorbench_socratic` | Socratic Questioning | 0.5 | **variance_restricted** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `mrbench_tutor` | dimension: Providing_Guidance | 0.2 | **variance_restricted** |
| P15 个性化教学策略选择 | formative | strategy_enactment | `tutorbench` | Fair815 multimodal tutor quality | 0.2 | **variance_restricted** |
| P16 学习路径规划（知识结构层） | reflective | core | `mooccube_prereq` | chance-corrected composite (先修选择 + 学习顺序排序) | 0.8 | **single_source** |
| P17 适配性解释与反馈生成 | formative | artifact_generation | `eduillustrate` | 8-dim 0-5 visual explanation score | 0.2 | **insufficient_evidence** |
| P17 适配性解释与反馈生成 | formative | tone_support | `mrbench_tutor` | dimension: Tutor_Tone (encouraging share) | 0.2 | **insufficient_evidence** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy_hard` | Pedagogy IF hard | 0.2 | **provisional** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding` | Scaffolding | 0.2 | **provisional** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_scaffolding_hard` | Scaffolding hard | 0.2 | **provisional** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mmtutorbench` | multimodal tutor score | 0.5 | **provisional** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `edubench` | higher_order_thinking_ability_development (metric) | 0.2 | **validated** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_pedagogy` | Pedagogy IF | 0.2 | **validated** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `bea2025_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | artifact_generation | `edubench` | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 0.5 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `edubench` | clarity_concision_inspiration (metric) | 0.2 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | tone_support | `edubench` | motivation_guidance_positive_feedback (metric) | 0.5 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_mistake_correction` | Mistake Correction | 0.2 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mathtutorbench_socratic` | Socratic Questioning | 0.2 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `mrbench_tutor` | dimension: Actionability | 0.2 | **variance_restricted** |
| P17 适配性解释与反馈生成 | formative | content_feedback | `tutorbench` | Fair815 multimodal tutor quality | 0.5 | **variance_restricted** |
| P18 教育场景行为边界 | reflective | role_boundary_behavior | `education_boundary_v1` | Role boundary gate accuracy | 1.0 | **single_source** |
| P19 学生潜在风险识别与应对 | reflective | risk_recognition_response | `student_risk_v2` | Risk recognition-response joint accuracy (provisional) | 1.0 | **single_source** |
| P20 内容适龄与育人导向 | formative | age_appropriate_content | `age_values_v1` | A/core content-and-handling pass rate | 1.0 | **single_source** |
| P20 内容适龄与育人导向 | formative | educational_values | `age_values_v1` | B four-category equal-weight content pass rate | 1.0 | **single_source** |

## 低置信附录（3 ≤ n < 5，仅呈现不评级）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `asap_2` essay holistic QWK | `sas_bench` QWK holistic total score | P12(0.8/0.8) | 4 | -0.4 |
| `edubench` clarity_concision_inspiration (metric) | `mmtutorbench` multimodal tutor score | P17(0.2/0.5) | 4 | -0.2 |
| `edubench` basic_factual_accuracy (metric) | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2) | 4 | 0.2 |
| `edubench` basic_factual_accuracy (metric) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2) | 4 | 0.2 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `eduillustrate` 8-dim 0-5 visual explanation score | P17(0.5/0.2) | 4 | 0.4 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmtutorbench` multimodal tutor score | P17(0.2/0.5) | 4 | 0.4 |
| `edubench` personalized_adaptation_learning_support (metric) | `mmtutorbench` multimodal tutor score | P15(0.5/0.2) | 4 | 0.4 |
| `edubench` scenario_element_integration (metric) | `mmtutorbench` multimodal tutor score | P15(0.2/0.2) | 4 | 0.4 |
| `edubench` domain_knowledge_accuracy (metric) | `k12vista` official partial-credit score (per-blank 0/1 mean) | P05(0.2/0.2) | 4 | 0.8 |
| `edubench` domain_knowledge_accuracy (metric) | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2) | 4 | 0.8 |

## 形成型跨 facet 配对（facet_distinct_expected，信息呈现，不触发红旗）

| A | B | 共享 P | n | ρ |
|---|---|---|---:|---:|
| `mathtutorbench_mistake_location` Mistake Location | `mrbench_tutor` dimension: Mistake_Identification | P11(0.8/0.2 异facet) | 8 | -0.657 |
| `p07_selfcheck` two-round self-check (fix/break rate) | `p08_abstention` balanced abstention score | P08(0.2/0.8 异facet) | 8 | -0.347 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` ECS error-cause consistency | P11(0.5/0.8 异facet) | 8 | -0.262 |
| `mrbench_tutor` dimension: Mistake_Identification | `sas_bench` CCS step scoring consistency | P11(0.2/0.2 异facet) | 8 | -0.192 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_mistake_location` Mistake Location | P11(0.2/0.8 异facet) | 8 | -0.18 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 7 | -0.179 |
| `mathtutorbench_mistake_location` Mistake Location | `sas_bench` ECS error-cause consistency | P11(0.8/0.8 异facet) | 8 | -0.168 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mrbench_tutor` dimension: Actionability | P17(0.5/0.2 异facet) | 7 | -0.162 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 7 | -0.143 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 7 | -0.107 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_solution_correctness` Solution Correctness | P11(0.2/0.5 异facet) | 8 | -0.048 |
| `edubench` basic_factual_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 7 | -0.036 |
| `edubench` error_identification_correction_accuracy (metric) | `sas_bench` CCS step scoring consistency | P11(0.2/0.2 异facet) | 7 | -0.036 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 7 | 0.0 |
| `mathtutorbench_scaffolding` Scaffolding | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 7 | 0.0 |
| `edubench` basic_factual_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 7 | 0.018 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mrbench_tutor` dimension: Actionability | P17(0.5/0.2 异facet) | 7 | 0.036 |
| `mathtutorbench_solution_correctness` Solution Correctness | `mrbench_tutor` dimension: Mistake_Identification | P11(0.5/0.2 异facet) | 8 | 0.036 |
| `bea2025_tutor` dimension: Mistake_Identification | `mathtutorbench_solution_correctness` Solution Correctness | P11(0.2/0.5 异facet) | 8 | 0.048 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.048 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.5/0.2 异facet) | 7 | 0.071 |
| `mathtutorbench_scaffolding` Scaffolding | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.071 |
| `edubench` higher_order_thinking_ability_development (metric) | `olympiadbench` overall/subject/language/modality accuracy | P06(0.2/0.5 异facet) | 6 | 0.086 |
| `edubench` reasoning_process_rigor (metric) | `olympiadbench` overall/subject/language/modality accuracy | P06(0.5/0.5 异facet) | 6 | 0.086 |
| `mrbench_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.2/0.8 异facet) | 8 | 0.095 |
| `mmtutorbench` multimodal tutor score | `olympiadbench` multimodal-subset accuracy | P03(0.2/0.2 异facet) | 5 | 0.1 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_scaffolding` Scaffolding | P17(0.5/0.2 异facet) | 7 | 0.107 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_mistake_correction` Mistake Correction | P17(0.5/0.2 异facet) | 7 | 0.107 |
| `edubench` personalized_adaptation_learning_support (metric) | `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | P14(0.2/0.8 异facet) | 7 | 0.107 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 7 | 0.107 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_socratic` Socratic Questioning | P17(0.5/0.2 异facet) | 7 | 0.143 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_solution_correctness` Solution Correctness | P11(0.2/0.5 异facet) | 7 | 0.143 |
| `mrbench_judge` 8-dimension tutor response judging | `sas_bench` QWK holistic total score | P12(0.5/0.8 异facet) | 8 | 0.143 |
| `olympiadbench` overall/subject/language/modality accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 7 | 0.144 |
| `edubench` error_identification_correction_accuracy (metric) | `mathtutorbench_mistake_location` Mistake Location | P11(0.2/0.8 异facet) | 7 | 0.179 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_socratic` Socratic Questioning | P17(0.5/0.2 异facet) | 7 | 0.179 |
| `olympiadbench` overall/subject/language/modality accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 7 | 0.179 |
| `bea2025_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.2/0.8 异facet) | 8 | 0.196 |
| `pedagogy_benchmark` CDPK teaching knowledge selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 11 | 0.209 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.5/0.2 异facet) | 7 | 0.214 |
| `mrbench_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` SEND special education needs selection | P15(0.2/0.5 异facet) | 8 | 0.216 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.2/0.8 异facet) | 8 | 0.238 |
| `mathtutorbench_mistake_correction` Mistake Correction | `sas_bench` CCS step scoring consistency | P11(0.2/0.2 异facet) | 8 | 0.238 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_mistake_correction` Mistake Correction | P17(0.5/0.2 异facet) | 7 | 0.25 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 8 | 0.262 |
| `longtutor_teaching` judge dims: strategy_alignment + history_utilization (1-5) | `pedagogy_benchmark` SEND special education needs selection | P15(0.2/0.5 异facet) | 8 | 0.275 |
| `mmtutorbench` multimodal tutor score | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.5/0.2 异facet) | 5 | 0.3 |
| `bea2025_tutor` dimension: Mistake_Identification | `sas_bench` CCS step scoring consistency | P11(0.2/0.2 异facet) | 8 | 0.31 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.31 |
| `mathtutorbench_pedagogy` Pedagogy IF | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 7 | 0.321 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `pedagogy_benchmark` SEND special education needs selection | P14(0.8/0.2 异facet) | 8 | 0.323 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.333 |
| `mathtutorbench_mistake_correction` Mistake Correction | `olympiadbench` overall/subject/language/modality accuracy | P06(0.2/0.5 异facet) | 7 | 0.357 |
| `mathtutorbench_scaffolding` Scaffolding | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 8 | 0.357 |
| `bea2025_tutor` dimension: Providing_Guidance | `pedagogy_benchmark` SEND special education needs selection | P15(0.2/0.5 异facet) | 8 | 0.364 |
| `pedagogy_benchmark` SEND special education needs selection | `sas_bench` ECS error-cause consistency | P05(0.5/0.2 异facet) | 11 | 0.369 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `mathtutorbench_mistake_location` Mistake Location | P11(0.2/0.8 异facet) | 8 | 0.371 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.381 |
| `mathtutorbench_pedagogy` Pedagogy IF | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 8 | 0.381 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.5/0.2 异facet) | 7 | 0.393 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.5/0.2 异facet) | 7 | 0.393 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_scaffolding` Scaffolding | P17(0.5/0.2 异facet) | 7 | 0.393 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_scaffolding` Scaffolding | P17(0.2/0.2 异facet) | 5 | 0.4 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `olympiadbench` overall/subject/language/modality accuracy | P05(0.2/0.2 异facet) | 7 | 0.429 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `sas_bench` ECS error-cause consistency | P05(0.2/0.2 异facet) | 8 | 0.452 |
| `mathtutorbench_socratic` Socratic Questioning | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.452 |
| `edubench` motivation_guidance_positive_feedback (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.5/0.2 异facet) | 7 | 0.464 |
| `edubench` personalized_adaptation_learning_support (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.5/0.8 异facet) | 7 | 0.464 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.2/0.8 异facet) | 7 | 0.464 |
| `mathtutorbench_solution_correctness` Solution Correctness | `sas_bench` CCS step scoring consistency | P11(0.5/0.2 异facet) | 8 | 0.476 |
| `edubench` higher_order_thinking_ability_development (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.2/0.5 异facet) | 7 | 0.482 |
| `edubench` reasoning_process_rigor (metric) | `mathtutorbench_problem_solving` Problem Solving | P06(0.5/0.5 异facet) | 7 | 0.482 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.5/0.2 异facet) | 7 | 0.5 |
| `edubench` clarity_concision_inspiration (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 7 | 0.5 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_pedagogy` Pedagogy IF | P17(0.2/0.2 异facet) | 5 | 0.5 |
| `k12vista` math problem-figure subset score | `mmtutorbench` multimodal tutor score | P03(0.5/0.2 异facet) | 5 | 0.5 |
| `k12vista` science/geo subject-chart subset score | `mmtutorbench` multimodal tutor score | P03(0.5/0.2 异facet) | 5 | 0.5 |
| `mathvista` task/question_type/answer_type accuracy | `mmtutorbench` multimodal tutor score | P03(0.5/0.2 异facet) | 5 | 0.5 |
| `mmtutorbench` multimodal tutor score | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.2/0.8 异facet) | 5 | 0.5 |
| `mmtutorbench` multimodal tutor score | `pedagogy_benchmark` SEND special education needs selection | P15(0.2/0.5 异facet) | 5 | 0.5 |
| `edubench` scenario_element_integration (metric) | `pedagogy_benchmark` SEND special education needs selection | P15(0.2/0.5 异facet) | 7 | 0.523 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 7 | 0.536 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 7 | 0.571 |
| `edubench` higher_order_thinking_ability_development (metric) | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 7 | 0.607 |
| `edubench` higher_order_thinking_ability_development (metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 7 | 0.607 |
| `edubench` reasoning_process_rigor (metric) | `mmlu_pro` overall/category accuracy | P06(0.5/0.2 异facet) | 7 | 0.607 |
| `bea2025_tutor` dimension: Actionability | `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | P17(0.2/0.5 异facet) | 7 | 0.643 |
| `longtutor_diagnosis` four-category knowledge-state diagnosis macro-F1 | `sas_bench` CCS step scoring consistency | P11(0.2/0.2 异facet) | 8 | 0.643 |
| `mathtutorbench_problem_solving` Problem Solving | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 9 | 0.661 |
| `mathtutorbench_problem_solving` Problem Solving | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 9 | 0.664 |
| `edubench` TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.5/0.2 异facet) | 7 | 0.679 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 7 | 0.679 |
| `bea2025_tutor` dimension: Actionability | `mrbench_tutor` dimension: Tutor_Tone (encouraging share) | P17(0.2/0.2 异facet) | 8 | 0.69 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2 异facet) | 5 | 0.7 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mathvista` task/question_type/answer_type accuracy | P06(0.2/0.5 异facet) | 5 | 0.7 |
| `edubench` domain_knowledge_accuracy (metric) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 7 | 0.703 |
| `bea2025_judge` judge labels: mistake/guidance/actionability | `sas_bench` QWK holistic total score | P12(0.5/0.8 异facet) | 8 | 0.714 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.5/0.2 异facet) | 9 | 0.733 |
| `mathtutorbench_socratic` Socratic Questioning | `pedagogy_benchmark` CDPK teaching knowledge selection | P15(0.5/0.8 异facet) | 8 | 0.738 |
| `agieval` overall/task/language/question_type accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.5/0.2 异facet) | 7 | 0.75 |
| `agieval` overall/task/language/question_type accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.5/0.5 异facet) | 7 | 0.75 |
| `bea2025_tutor` dimension: Actionability | `edubench` motivation_guidance_positive_feedback (metric) | P17(0.2/0.5 异facet) | 7 | 0.75 |
| `ceval` overall/category/subject accuracy | `edubench` higher_order_thinking_ability_development (metric) | P06(0.2/0.2 异facet) | 7 | 0.75 |
| `ceval` overall/category/subject accuracy | `edubench` reasoning_process_rigor (metric) | P06(0.2/0.5 异facet) | 7 | 0.75 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.5/0.2 异facet) | 9 | 0.75 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 7 | 0.75 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 9 | 0.767 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 9 | 0.783 |
| `mathtutorbench_mistake_correction` Mistake Correction | `mmlu_pro` overall/category accuracy | P06(0.2/0.2 异facet) | 9 | 0.783 |
| `edubench` domain_knowledge_accuracy (metric) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 7 | 0.786 |
| `mathtutorbench_socratic` Socratic Questioning | `pedagogy_benchmark` SEND special education needs selection | P15(0.5/0.5 异facet) | 8 | 0.79 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P17(0.2/0.2 异facet) | 5 | 0.8 |
| `eduillustrate` 8-dim 0-5 visual explanation score | `mathtutorbench_scaffolding_hard` Scaffolding hard | P17(0.2/0.2 异facet) | 5 | 0.8 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_scaffolding` Scaffolding | P05(0.2/0.2 异facet) | 5 | 0.8 |
| `k12vista` science/geo subject-chart subset score | `olympiadbench` multimodal-subset accuracy | P03(0.5/0.2 异facet) | 5 | 0.8 |
| `mathtutorbench_scaffolding` Scaffolding | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2 异facet) | 5 | 0.8 |
| `mathtutorbench_scaffolding` Scaffolding | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 9 | 0.8 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 9 | 0.817 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.2/0.2 异facet) | 9 | 0.817 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 9 | 0.817 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 9 | 0.833 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_mistake_correction` Mistake Correction | P06(0.5/0.2 异facet) | 9 | 0.867 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.5/0.5 异facet) | 9 | 0.867 |
| `agieval` overall/task/language/question_type accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 9 | 0.87 |
| `ceval` overall/category/subject accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 9 | 0.879 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 9 | 0.883 |
| `agieval` overall/task/language/question_type accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 9 | 0.883 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 9 | 0.883 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mmlu_pro` overall/category accuracy | P05(0.2/0.5 异facet) | 9 | 0.883 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.2/0.2 异facet) | 5 | 0.9 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_scaffolding_hard` Scaffolding hard | P05(0.2/0.2 异facet) | 5 | 0.9 |
| `mathtutorbench_pedagogy` Pedagogy IF | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2 异facet) | 5 | 0.9 |
| `mathtutorbench_scaffolding_hard` Scaffolding hard | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2 异facet) | 5 | 0.9 |
| `mmlu_pro` overall/category accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.5/0.5 异facet) | 9 | 0.912 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy` Pedagogy IF | P05(0.5/0.2 异facet) | 9 | 0.917 |
| `ceval` overall/category/subject accuracy | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.5/0.2 异facet) | 9 | 0.95 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `mathtutorbench_pedagogy_hard` Pedagogy IF hard | P05(0.2/0.2 异facet) | 5 | 1.0 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 5 | 1.0 |
| `k12vista` official partial-credit score (per-blank 0/1 mean) | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 5 | 1.0 |
| `k12vista` science/geo subject-chart subset score | `mathvista` task/question_type/answer_type accuracy | P03(0.5/0.5 异facet) | 5 | 1.0 |
| `mathtutorbench_pedagogy_hard` Pedagogy IF hard | `mathvista` task/question_type/answer_type accuracy | P05(0.2/0.2 异facet) | 5 | 1.0 |
| `mathvista` task/question_type/answer_type accuracy | `pedagogy_benchmark` CDPK teaching knowledge selection | P05(0.2/0.5 异facet) | 5 | 1.0 |
| `mathvista` task/question_type/answer_type accuracy | `pedagogy_benchmark` SEND special education needs selection | P05(0.2/0.5 异facet) | 5 | 1.0 |

## 局限

- n=5-8 的置信区间很宽，评级以红旗探测为目的，不是效应量精确估计；补模型数（M2.5）是第一优先级。
- 偏相关控制的'综合分'由同一批证据构造，存在轻度内生性；仅作敏感性检查。
- 配对之间共享格子、非独立，区分效度的 permutation p 只作参考。