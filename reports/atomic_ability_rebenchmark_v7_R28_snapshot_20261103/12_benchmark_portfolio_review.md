# Benchmark Portfolio Review

目的：先用两个直观指标判断当前 benchmark 是否还值得继续重点做。

## 两个主指标

1. **所有模型平均分**：对进入最终计算的 canonical score rows，在同一个 benchmark/subdimension 下跨模型取 `score_10` 平均。分数越高，说明当前模型整体越接近解决；分数越低，越有继续区分模型的价值。`NA` 表示该 mapping 目前没有进入最终计分的模型结果。
2. **原子能力有效相关性**：只由 mapping 决定，不看模型表现。公式（R20，无 tier 因子）：`100 × benchmark_weight × Σ(P_priority × ability_weight)`。

辅助列：`P 相关性` 是不乘 benchmark 置信权重的纯 P 能力相关性。

## 先看结论排序

| 建议 | Benchmark | Subdimension | 所有模型平均分 | 原子能力有效相关性 | P 相关性 | 模型数 | P 映射 |
|---|---|---|---:|---:|---:|---:|---|
| 优先继续做 | `sas_bench` SAS-Bench | ECS error-cause consistency | 5.06 | 100.00 | 100.00 | 11 | P05 0.20, P06 0.20, P11 0.80 |
| 优先继续做 | `longtutor_diagnosis` LongTutor 知识状态诊断 | four-category knowledge-state diagnosis macro-F1 | 2.62 | 82.45 | 97.00 | 8 | P11 0.20, P14 0.80 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | calibration composite (CWR/AUROC) | 6.40 | 77.35 | 91.00 | 8 | P07 0.20, P08 0.80 |
| 优先继续做 | `asap_2` ASAP 2.0 | essay holistic QWK | 5.45 | 72.00 | 72.00 | 7 | P12 0.80 |
| 值得继续做 | `student_risk_v2` Student Risk v2 | Risk recognition-response joint accuracy (provisional) | 7.09 | 70.00 | 100.00 | 6 | P19 1.00 |
| 优先继续做 | `mooccube_prereq` MOOCCube 先修关系推理 | chance-corrected composite (先修选择 + 学习顺序排序) | 3.99 | 69.70 | 82.00 | 8 | P16 0.80 |
| 优先继续做 | `tutorbench` TutorBench | Fair815 multimodal tutor quality | 5.48 | 68.42 | 80.50 | 6 | P03 0.20, P15 0.20, P17 0.50 |
| 值得继续做 | `mmtutorbench` MMTutorBench | multimodal tutor score | 6.80 | 68.42 | 80.50 | 5 | P03 0.20, P15 0.20, P17 0.50 |
| 优先继续做 | `p07_selfcheck` P07 两轮自查 | two-round self-check (fix/break rate) | 5.21 | 67.15 | 79.00 | 8 | P07 0.80, P08 0.20 |
| 优先继续做 | `mathtutorbench_socratic` MathTutorBench | Socratic Questioning | 2.80 | 66.50 | 66.50 | 8 | P15 0.50, P17 0.20 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | Scaffolding hard | 2.89 | 65.88 | 77.50 | 10 | P05 0.20, P15 0.50, P17 0.20 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | Scaffolding | 3.10 | 65.88 | 77.50 | 10 | P05 0.20, P15 0.50, P17 0.20 |
| 值得继续做 | `edubench` EduBench | personalized_adaptation_learning_support (metric) | 6.67 | 60.78 | 71.50 | 14 | P14 0.20, P15 0.50 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | CDPK teaching knowledge selection | 8.46 | 103.50 | 103.50 | 15 | P05 0.50, P15 0.80 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | SEND special education needs selection | 7.86 | 99.00 | 99.00 | 15 | P05 0.50, P14 0.20, P15 0.50 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | Mistake Location | 7.71 | 95.00 | 95.00 | 9 | P02 0.20, P11 0.80 |
| 重要但可降频 | `sas_bench` SAS-Bench | CCS step scoring consistency | 7.64 | 83.00 | 83.00 | 11 | P02 0.20, P11 0.20, P12 0.50 |
| 重要但可降频 | `mathvista` MathVista | task/question_type/answer_type accuracy | 8.52 | 78.50 | 78.50 | 5 | P03 0.50, P05 0.20, P06 0.50 |
| 重要但可降频 | `sas_bench` SAS-Bench | QWK holistic total score | 8.30 | 72.00 | 72.00 | 11 | P12 0.80 |
| 重要但可降频 | `age_values_v1` Age Values v1 | A/core content-and-handling pass rate | 8.27 | 70.00 | 100.00 | 6 | P20 1.00 |
| 重要但可降频 | `age_values_v1` Age Values v1 | B four-category equal-weight content pass rate | 8.91 | 70.00 | 100.00 | 6 | P20 1.00 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | Pedagogy IF hard | 7.76 | 65.88 | 77.50 | 10 | P05 0.20, P15 0.50, P17 0.20 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | Pedagogy IF | 8.22 | 65.88 | 77.50 | 10 | P05 0.20, P15 0.50, P17 0.20 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | balanced abstention score | 8.93 | 64.60 | 76.00 | 8 | P08 0.80 |
| 重要但可降频 | `education_boundary_v1` Education Boundary v1 | Role boundary gate accuracy | 8.92 | 63.00 | 90.00 | 6 | P18 1.00 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | Solution Correctness | 8.72 | 62.50 | 62.50 | 9 | P07 0.20, P11 0.50 |
| 不必重点看 | `mathtutorbench_mistake_correction` MathTutorBench | Mistake Correction | 8.99 | 51.00 | 51.00 | 9 | P06 0.20, P11 0.20, P17 0.20 |
| 诊断保留 | `eduillustrate` EduIllustrate | 8-dim 0-5 visual explanation score | 5.67 | 49.00 | 70.00 | 6 | P04 0.50, P17 0.20 |
| 诊断保留 | `bea2025_judge` BEA 2025 Judge | judge labels: mistake/guidance/actionability | 5.10 | 45.00 | 45.00 | 10 | P12 0.50 |
| 诊断保留 | `mrbench_judge` MRBench Judge | 8-dimension tutor response judging | 5.29 | 45.00 | 45.00 | 10 | P12 0.50 |
| 不必重点看 | `ifeval` IFEval | prompt-level strict accuracy | 9.04 | 45.00 | 45.00 | 8 | P01 1.00 |
| 不必重点看 | `olympiadbench` OlympiadBench | overall/subject/language/modality accuracy | 7.13 | 43.50 | 43.50 | 7 | P05 0.20, P06 0.50 |
| 不必重点看 | `agieval` AGIEval | overall/task/language/question_type accuracy | 8.72 | 43.50 | 43.50 | 9 | P05 0.20, P06 0.50 |
| 不必重点看 | `mathtutorbench_problem_solving` MathTutorBench | Problem Solving | 9.67 | 43.50 | 43.50 | 9 | P05 0.20, P06 0.50 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Multi-session Reasoning accuracy | 6.62 | 40.60 | 58.00 | 8 | P02 0.80 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Hallucination Check accuracy | 7.50 | 40.60 | 58.00 | 8 | P02 0.80 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | Information Extraction accuracy | 9.54 | 40.60 | 58.00 | 8 | P02 0.80 |
| 不必重点看 | `mmlu_pro` MMLU-Pro | overall/category accuracy | 8.49 | 40.50 | 40.50 | 9 | P05 0.50, P06 0.20 |
| 不必重点看 | `ceval` C-EVAL | overall/category/subject accuracy | 8.93 | 40.50 | 40.50 | 10 | P05 0.50, P06 0.20 |
| 不必重点看 | `edubench` EduBench | motivation_guidance_positive_feedback (metric) | 6.67 | 40.38 | 47.50 | 14 | P17 0.50 |
| 不必重点看 | `edubench` EduBench | TMG/PCC × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.20 | 40.38 | 47.50 | 14 | P17 0.50 |
| 不必重点看 | `edubench` EduBench | QG × clarity_concision_inspiration + scenario_element_integration (task×metric) | 8.24 | 38.25 | 45.00 | 14 | P13 0.50 |
| 不必重点看 | `k12vista` K12Vista | science/geo subject-chart subset score | 6.60 | 29.75 | 35.00 | 5 | P03 0.50 |
| 不必重点看 | `k12vista` K12Vista | math problem-figure subset score | 7.71 | 29.75 | 35.00 | 5 | P03 0.50 |
| 不必重点看 | `edubench` EduBench | reasoning_process_rigor (metric) | 8.43 | 27.62 | 32.50 | 14 | P06 0.50 |
| 不必重点看 | `edubench` EduBench | higher_order_thinking_ability_development (metric) | 7.52 | 27.20 | 32.00 | 14 | P06 0.20, P17 0.20 |
| 不必重点看 | `k12vista` K12Vista | official partial-credit score (per-blank 0/1 mean) | 6.90 | 20.40 | 24.00 | 5 | P05 0.20, P06 0.20 |
| 不必重点看 | `edubench` EduBench | scenario_element_integration (metric) | 7.90 | 16.15 | 19.00 | 14 | P15 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Tutor_Tone (encouraging share) | 8.25 | 16.15 | 19.00 | 8 | P17 0.20 |
| 不必重点看 | `edubench` EduBench | clarity_concision_inspiration (metric) | 8.28 | 16.15 | 19.00 | 14 | P17 0.20 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Mistake_Identification | 8.85 | 16.15 | 19.00 | 8 | P11 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Providing_Guidance | 9.19 | 16.15 | 19.00 | 8 | P15 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Mistake_Identification | 9.41 | 16.15 | 19.00 | 8 | P11 0.20 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | dimension: Actionability | 9.49 | 16.15 | 19.00 | 8 | P17 0.20 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Actionability | 9.50 | 16.15 | 19.00 | 8 | P17 0.20 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | dimension: Providing_Guidance | 9.72 | 16.15 | 19.00 | 8 | P15 0.20 |
| 不必重点看 | `edubench` EduBench | QG × domain_knowledge_accuracy + basic_factual_accuracy (task×metric) | 9.25 | 15.30 | 18.00 | 14 | P13 0.20 |
| 不必重点看 | `olympiadbench` OlympiadBench | multimodal-subset accuracy | 6.86 | 14.00 | 14.00 | 5 | P03 0.20 |
| 不必重点看 | `longtutor_teaching` LongTutor 教学动作 | judge dims: strategy_alignment + history_utilization (1-5) | 6.61 | 13.30 | 19.00 | 8 | P15 0.20 |
| 不必重点看 | `edubench` EduBench | domain_knowledge_accuracy (metric) | 8.78 | 9.35 | 11.00 | 14 | P05 0.20 |
| 不必重点看 | `edubench` EduBench | basic_factual_accuracy (metric) | 9.21 | 9.35 | 11.00 | 14 | P05 0.20 |
| 不必重点看 | `edubench` EduBench | error_identification_correction_accuracy (metric) | 7.53 | 5.70 | 19.00 | 14 | P11 0.20 |

## 按 benchmark 聚合

聚合口径：同一 benchmark 的多个 subdimension 先各自计算平均分和相关性，再在 benchmark 内做简单平均；只用于概览，具体判断仍看上面的 subdimension 明细。

| 建议 | Benchmark | Subdimension 数 | benchmark 平均分 | 平均原子相关性 | P 覆盖 |
|---|---|---:|---:|---:|---|
| 优先继续做 | `longtutor_diagnosis` LongTutor 知识状态诊断 | 1 | 2.62 | 82.45 | P11, P14 |
| 优先继续做 | `p08_calibration` P08 置信度校准 | 1 | 6.40 | 77.35 | P07, P08 |
| 优先继续做 | `asap_2` ASAP 2.0 | 1 | 5.45 | 72.00 | P12 |
| 值得继续做 | `student_risk_v2` Student Risk v2 | 1 | 7.09 | 70.00 | P19 |
| 优先继续做 | `mooccube_prereq` MOOCCube 先修关系推理 | 1 | 3.99 | 69.70 | P16 |
| 优先继续做 | `tutorbench` TutorBench | 1 | 5.48 | 68.42 | P03, P15, P17 |
| 值得继续做 | `mmtutorbench` MMTutorBench | 1 | 6.80 | 68.42 | P03, P15, P17 |
| 优先继续做 | `p07_selfcheck` P07 两轮自查 | 1 | 5.21 | 67.15 | P07, P08 |
| 优先继续做 | `mathtutorbench_socratic` MathTutorBench | 1 | 2.80 | 66.50 | P15, P17 |
| 优先继续做 | `mathtutorbench_scaffolding_hard` MathTutorBench | 1 | 2.89 | 65.88 | P05, P15, P17 |
| 优先继续做 | `mathtutorbench_scaffolding` MathTutorBench | 1 | 3.10 | 65.88 | P05, P15, P17 |
| 重要但可降频 | `pedagogy_benchmark` Pedagogy Benchmark | 2 | 8.16 | 101.25 | P05, P14, P15 |
| 重要但可降频 | `mathtutorbench_mistake_location` MathTutorBench | 1 | 7.71 | 95.00 | P02, P11 |
| 重要但可降频 | `sas_bench` SAS-Bench | 3 | 7.00 | 85.00 | P02, P05, P06, P11, P12 |
| 重要但可降频 | `mathvista` MathVista | 1 | 8.52 | 78.50 | P03, P05, P06 |
| 重要但可降频 | `age_values_v1` Age Values v1 | 2 | 8.59 | 70.00 | P20 |
| 重要但可降频 | `mathtutorbench_pedagogy_hard` MathTutorBench | 1 | 7.76 | 65.88 | P05, P15, P17 |
| 重要但可降频 | `mathtutorbench_pedagogy` MathTutorBench | 1 | 8.22 | 65.88 | P05, P15, P17 |
| 重要但可降频 | `p08_abstention` P08 能力性弃答 | 1 | 8.93 | 64.60 | P08 |
| 重要但可降频 | `education_boundary_v1` Education Boundary v1 | 1 | 8.92 | 63.00 | P18 |
| 重要但可降频 | `mathtutorbench_solution_correctness` MathTutorBench | 1 | 8.72 | 62.50 | P07, P11 |
| 不必重点看 | `mathtutorbench_mistake_correction` MathTutorBench | 1 | 8.99 | 51.00 | P06, P11, P17 |
| 诊断保留 | `eduillustrate` EduIllustrate | 1 | 5.67 | 49.00 | P04, P17 |
| 诊断保留 | `bea2025_judge` BEA 2025 Judge | 1 | 5.10 | 45.00 | P12 |
| 诊断保留 | `mrbench_judge` MRBench Judge | 1 | 5.29 | 45.00 | P12 |
| 不必重点看 | `ifeval` IFEval | 1 | 9.04 | 45.00 | P01 |
| 不必重点看 | `agieval` AGIEval | 1 | 8.72 | 43.50 | P05, P06 |
| 不必重点看 | `mathtutorbench_problem_solving` MathTutorBench | 1 | 9.67 | 43.50 | P05, P06 |
| 不必重点看 | `longtutor_evidence` LongTutor 证据抽取 | 3 | 7.89 | 40.60 | P02 |
| 不必重点看 | `mmlu_pro` MMLU-Pro | 1 | 8.49 | 40.50 | P05, P06 |
| 不必重点看 | `ceval` C-EVAL | 1 | 8.93 | 40.50 | P05, P06 |
| 不必重点看 | `olympiadbench` OlympiadBench | 2 | 6.99 | 28.75 | P03, P05, P06 |
| 不必重点看 | `k12vista` K12Vista | 3 | 7.07 | 26.63 | P03, P05, P06 |
| 不必重点看 | `edubench` EduBench | 12 | 8.06 | 25.55 | P05, P06, P11, P13, P14, P15, P17 |
| 不必重点看 | `mrbench_tutor` MRBench Tutor | 4 | 9.08 | 16.15 | P11, P15, P17 |
| 不必重点看 | `bea2025_tutor` BEA 2025 Tutor | 3 | 9.36 | 16.15 | P11, P15, P17 |
| 不必重点看 | `longtutor_teaching` LongTutor 教学动作 | 1 | 6.61 | 13.30 | P15 |

## 校准提示

- `所有模型平均分` 高但 `原子能力有效相关性` 低：通常不需要重点看，适合做门槛或背景参考。
- `所有模型平均分` 低且 `原子能力有效相关性` 高：优先继续做，因为它既重要又还没被解决好。
- `NA` 且相关性高：说明 mapping 认为它重要，但当前主计分层缺结果，应该优先补跑或确认数据源。
- foundation gate 不等于没用，只是不应主导教育能力判断；它更适合筛掉基础能力不足的模型。
