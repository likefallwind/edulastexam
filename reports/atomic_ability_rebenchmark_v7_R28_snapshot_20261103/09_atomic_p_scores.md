# Atomic P Scores

P-score rows: 219
Covered P codes: P01, P02, P03, P04, P05, P06, P07, P08, P11, P12, P13, P14, P15, P16, P17, P18, P19, P20
Missing P codes: P09, P10, P21
P rows reported as 未测过 (score_10 = null): 18
Capability-gap zero cells (score_10 = 0, counted): 36
Untested cells (not counted; see `09_atomic_p_untested_cells.jsonl`): 52

`score_10`: facet-weighted average with effective weight = relevance × confidence (R25 rule-derived weights). Coverage completeness is reported separately and is not folded back into the score.

## Missing-cell policy (R26, 2026-08-04)

The R22 rule -- fill a panel model's missing cell with the lowest score any tested
model got there -- is **removed**. A missing cell is now classified:

- `untested`: never run. No score, no denominator, reported as 未测过. A P whose
  cells are all untested gets `score_10: null`, **not** 0.
- `capability_gap`: the model lacks a capability the cell requires for *every* item
  (vision only so far; see `MODEL_CAPABILITIES` / `CELL_CAPABILITY_REQUIREMENTS`).
  That is a real capability gap rather than a scheduling gap, so it scores **0** and counts.

Cells where only *some* items need the capability (tutorbench, olympiadbench overall)
stay `untested`: a text-only model earns a genuine non-zero score there, so 0 would be
a measurement artifact rather than a capability difference.

## Sample Scores

| Model key | P | Group | Score | Evidence | 0-score cells | Untested cells | Weight sum | Benchmarks |
|---|---|---|---:|---:|---:|---:|---:|---|
| `claude-sonnet-4.6` | `P05` 知识调用与掌握 | FDR | 8.2361 | 2 | 0 | 0 | 1.0 | pedagogy_benchmark |
| `claude-sonnet-4.6` | `P12` 主观题评价能力 | LAD | 6.106 | 1 | 0 | 0 | 0.8 | asap_2 |
| `claude-sonnet-4.6` | `P14` 学习者画像建模 | CLM | 7.8182 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `claude-sonnet-4.6` | `P15` 个性化教学策略选择 | CLM | 8.3326 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P05` 知识调用与掌握 | FDR | 6.8221 | 2 | 0 | 0 | 1.0 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P14` 学习者画像建模 | CLM | 6.6364 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `deepseek-r1-0528-qwen3-8b` | `P15` 个性化教学策略选择 | CLM | 6.8649 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `deepseek-v3-2` | `P12` 主观题评价能力 | LAD | 3.898 | 2 | 0 | 0 | 1.0 | bea2025_judge, mrbench_judge |
| `deepseek-v4-1-flash` | `P19` 学生潜在风险识别与应对 | CEG | 7.1429 | 1 | 0 | 0 | 0.7 | student_risk_v2 |
| `deepseek-v4-flash` | `P02` 长上下文与证据定位 | SRG | 7.74 | 1 | 0 | 0 | 0.2 | mathtutorbench_mistake_location |
| `deepseek-v4-flash` | `P05` 知识调用与掌握 | FDR | 7.9037 | 10 | 0 | 0 | 3.08 | agieval, ceval, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mmlu_pro, pedagogy_benchmark |
| `deepseek-v4-flash` | `P06` 推理与生成 | FDR | 9.1935 | 5 | 0 | 0 | 1.6 | agieval, ceval, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mmlu_pro |
| `deepseek-v4-flash` | `P07` 自我校验与修正 | FDR | 8.567 | 1 | 0 | 0 | 0.2 | mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P11` 错误诊断 | LAD | 8.4929 | 3 | 0 | 0 | 1.5 | mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness |
| `deepseek-v4-flash` | `P12` 主观题评价能力 | LAD | 5.1073 | 3 | 0 | 0 | 1.8 | asap_2, bea2025_judge, mrbench_judge |
| `deepseek-v4-flash` | `P14` 学习者画像建模 | CLM | 7.8182 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `deepseek-v4-flash` | `P15` 个性化教学策略选择 | CLM | 6.4776 | 6 | 0 | 0 | 3.0 | mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, pedagogy_benchmark |
| `deepseek-v4-flash` | `P17` 适配性解释与反馈生成 | CLM | 5.6089 | 5 | 0 | 0 | 0.88 | mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `deepseek-v4-pro` | `P01` 指令与约束遵循 | SRG | 9.2222 | 1 | 0 | 0 | 1.0 | ifeval |
| `deepseek-v4-pro` | `P02` 长上下文与证据定位 | SRG | 7.8666 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `deepseek-v4-pro` | `P03` 多模态理解 | SRG | 0.0 | 4 | 4 | 2 | 1.52 | k12vista, mathvista, mmtutorbench |
| `deepseek-v4-pro` | `P04` 多模态生成 | SRG | 0.0 | 1 | 1 | 0 | 0.35 | eduillustrate |
| `deepseek-v4-pro` | `P05` 知识调用与掌握 | FDR | 7.4906 | 16 | 2 | 0 | 4.19 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `deepseek-v4-pro` | `P06` 推理与生成 | FDR | 7.0868 | 11 | 2 | 0 | 3.565 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `deepseek-v4-pro` | `P07` 自我校验与修正 | FDR | 6.342 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `deepseek-v4-pro` | `P08` 置信度校准与弃答 | FDR | 7.7836 | 3 | 0 | 0 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `deepseek-v4-pro` | `P11` 错误诊断 | LAD | 7.7404 | 9 | 0 | 0 | 3.07 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `deepseek-v4-pro` | `P12` 主观题评价能力 | LAD | 6.4007 | 5 | 0 | 0 | 3.1 | asap_2, bea2025_judge, mrbench_judge, sas_bench |
| `deepseek-v4-pro` | `P13` 命题与作业设计 | LAD | 8.0409 | 2 | 0 | 0 | 0.595 | edubench |
| `deepseek-v4-pro` | `P14` 学习者画像建模 | CLM | 5.3541 | 3 | 0 | 0 | 1.05 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `deepseek-v4-pro` | `P15` 个性化教学策略选择 | CLM | 7.2488 | 13 | 1 | 1 | 4.745 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor, pedagogy_benchmark |
| `deepseek-v4-pro` | `P16` 学习路径规划（知识结构层） | CLM | 3.789 | 1 | 0 | 0 | 0.68 | mooccube_prereq |
| `deepseek-v4-pro` | `P17` 适配性解释与反馈生成 | CLM | 6.1437 | 15 | 2 | 1 | 3.345 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor |
| `deepseek-v4-pro` | `P18` 教育场景行为边界 | CEG | 未测过 | 0 | 0 | 1 | 0.0 |  |
| `deepseek-v4-pro` | `P19` 学生潜在风险识别与应对 | CEG | 未测过 | 0 | 0 | 1 | 0.0 |  |
| `deepseek-v4-pro` | `P20` 内容适龄与育人导向 | CEG | 未测过 | 0 | 0 | 2 | 0.0 |  |
| `doubao-seed-2-0-lite` | `P04` 多模态生成 | SRG | 5.3038 | 1 | 0 | 0 | 0.35 | eduillustrate |
| `doubao-seed-2-0-lite` | `P05` 知识调用与掌握 | FDR | 5.317 | 4 | 0 | 0 | 0.68 | mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P15` 个性化教学策略选择 | CLM | 5.317 | 4 | 0 | 0 | 1.7 | mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-lite` | `P17` 适配性解释与反馈生成 | CLM | 5.3104 | 5 | 0 | 0 | 0.82 | eduillustrate, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard |
| `doubao-seed-2-0-pro` | `P01` 指令与约束遵循 | SRG | 8.9464 | 1 | 0 | 0 | 1.0 | ifeval |
| `doubao-seed-2-0-pro` | `P02` 长上下文与证据定位 | SRG | 7.9369 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `doubao-seed-2-0-pro` | `P03` 多模态理解 | SRG | 7.8517 | 5 | 0 | 1 | 1.72 | k12vista, mathvista, mmtutorbench, olympiadbench |
| `doubao-seed-2-0-pro` | `P04` 多模态生成 | SRG | 6.6376 | 1 | 0 | 0 | 0.35 | eduillustrate |
| `doubao-seed-2-0-pro` | `P05` 知识调用与掌握 | FDR | 8.0926 | 16 | 0 | 0 | 4.19 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `doubao-seed-2-0-pro` | `P06` 推理与生成 | FDR | 8.4838 | 11 | 0 | 0 | 3.565 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `doubao-seed-2-0-pro` | `P07` 自我校验与修正 | FDR | 6.026 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `doubao-seed-2-0-pro` | `P08` 置信度校准与弃答 | FDR | 7.6935 | 3 | 0 | 0 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `doubao-seed-2-0-pro` | `P11` 错误诊断 | LAD | 7.726 | 9 | 0 | 0 | 3.07 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `doubao-seed-2-0-pro` | `P12` 主观题评价能力 | LAD | 7.179 | 4 | 0 | 1 | 2.3 | bea2025_judge, mrbench_judge, sas_bench |
| `doubao-seed-2-0-pro` | `P13` 命题与作业设计 | LAD | 8.262 | 2 | 0 | 0 | 0.595 | edubench |
| `doubao-seed-2-0-pro` | `P14` 学习者画像建模 | CLM | 5.1437 | 3 | 0 | 0 | 1.05 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `doubao-seed-2-0-pro` | `P15` 个性化教学策略选择 | CLM | 7.4698 | 13 | 0 | 1 | 4.745 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor, pedagogy_benchmark |
| `doubao-seed-2-0-pro` | `P16` 学习路径规划（知识结构层） | CLM | 4.486 | 1 | 0 | 0 | 0.68 | mooccube_prereq |
| `doubao-seed-2-0-pro` | `P17` 适配性解释与反馈生成 | CLM | 7.7416 | 15 | 0 | 1 | 3.345 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor |
| `doubao-seed-2-0-pro` | `P18` 教育场景行为边界 | CEG | 未测过 | 0 | 0 | 1 | 0.0 |  |
| `doubao-seed-2-0-pro` | `P19` 学生潜在风险识别与应对 | CEG | 未测过 | 0 | 0 | 1 | 0.0 |  |
| `doubao-seed-2-0-pro` | `P20` 内容适龄与育人导向 | CEG | 未测过 | 0 | 0 | 2 | 0.0 |  |
| `doubao-seed-2-1-pro` | `P18` 教育场景行为边界 | CEG | 8.7188 | 1 | 0 | 0 | 0.7 | education_boundary_v1 |
| `doubao-seed-2-1-pro` | `P19` 学生潜在风险识别与应对 | CEG | 6.8407 | 1 | 0 | 0 | 0.7 | student_risk_v2 |
| `doubao-seed-2-1-pro` | `P20` 内容适龄与育人导向 | CEG | 8.9249 | 2 | 0 | 0 | 1.4 | age_values_v1 |
| `glm-5-3` | `P18` 教育场景行为边界 | CEG | 9.8438 | 1 | 0 | 0 | 0.7 | education_boundary_v1 |
| `glm-5-3` | `P19` 学生潜在风险识别与应对 | CEG | 7.3901 | 1 | 0 | 0 | 0.7 | student_risk_v2 |
| `glm-5-3` | `P20` 内容适龄与育人导向 | CEG | 8.9463 | 2 | 0 | 0 | 1.4 | age_values_v1 |
| `glm-5-3-flash` | `P18` 教育场景行为边界 | CEG | 9.8125 | 1 | 0 | 0 | 0.7 | education_boundary_v1 |
| `glm-5-3-flash` | `P19` 学生潜在风险识别与应对 | CEG | 7.2253 | 1 | 0 | 0 | 0.7 | student_risk_v2 |
| `glm-5-3-flash` | `P20` 内容适龄与育人导向 | CEG | 8.9388 | 2 | 0 | 0 | 1.4 | age_values_v1 |
| `glm-5.1` | `P02` 长上下文与证据定位 | SRG | 7.8142 | 1 | 0 | 0 | 0.2 | sas_bench |
| `glm-5.1` | `P05` 知识调用与掌握 | FDR | 7.4459 | 3 | 0 | 0 | 1.2 | pedagogy_benchmark, sas_bench |
| `glm-5.1` | `P06` 推理与生成 | FDR | 6.2602 | 1 | 0 | 0 | 0.2 | sas_bench |
| `glm-5.1` | `P11` 错误诊断 | LAD | 7.0372 | 2 | 0 | 0 | 1.0 | sas_bench |
| `glm-5.1` | `P12` 主观题评价能力 | LAD | 7.4274 | 3 | 0 | 0 | 2.1 | asap_2, sas_bench |
| `glm-5.1` | `P14` 学习者画像建模 | CLM | 8.4091 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `glm-5.1` | `P15` 个性化教学策略选择 | CLM | 8.6831 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `glm-5.2` | `P01` 指令与约束遵循 | SRG | 9.2976 | 1 | 0 | 0 | 1.0 | ifeval |
| `glm-5.2` | `P02` 长上下文与证据定位 | SRG | 8.0284 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `glm-5.2` | `P03` 多模态理解 | SRG | 0.0 | 4 | 4 | 2 | 1.52 | k12vista, mathvista, mmtutorbench |
| `glm-5.2` | `P04` 多模态生成 | SRG | 0.0 | 1 | 1 | 0 | 0.35 | eduillustrate |
| `glm-5.2` | `P05` 知识调用与掌握 | FDR | 7.62 | 16 | 2 | 0 | 4.19 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, olympiadbench, pedagogy_benchmark, sas_bench |
| `glm-5.2` | `P06` 推理与生成 | FDR | 6.8631 | 11 | 2 | 0 | 3.565 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mathvista, mmlu_pro, olympiadbench, sas_bench |
| `glm-5.2` | `P07` 自我校验与修正 | FDR | 6.3047 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |
| `glm-5.2` | `P08` 置信度校准与弃答 | FDR | 7.7336 | 3 | 0 | 0 | 1.53 | p07_selfcheck, p08_abstention, p08_calibration |
| `glm-5.2` | `P11` 错误诊断 | LAD | 7.4679 | 9 | 0 | 0 | 3.07 | bea2025_tutor, edubench, longtutor_diagnosis, mathtutorbench_mistake_correction, mathtutorbench_mistake_location, mathtutorbench_solution_correctness, mrbench_tutor, sas_bench |
| `glm-5.2` | `P12` 主观题评价能力 | LAD | 7.3949 | 4 | 0 | 1 | 2.3 | bea2025_judge, mrbench_judge, sas_bench |
| `glm-5.2` | `P13` 命题与作业设计 | LAD | 8.2479 | 2 | 0 | 0 | 0.595 | edubench |
| `glm-5.2` | `P14` 学习者画像建模 | CLM | 5.1556 | 3 | 0 | 0 | 1.05 | edubench, longtutor_diagnosis, pedagogy_benchmark |
| `glm-5.2` | `P15` 个性化教学策略选择 | CLM | 7.6046 | 13 | 1 | 1 | 4.745 | bea2025_tutor, edubench, longtutor_teaching, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor, pedagogy_benchmark |
| `glm-5.2` | `P16` 学习路径规划（知识结构层） | CLM | 3.911 | 1 | 0 | 0 | 0.68 | mooccube_prereq |
| `glm-5.2` | `P17` 适配性解释与反馈生成 | CLM | 6.6029 | 15 | 2 | 1 | 3.345 | bea2025_tutor, edubench, eduillustrate, mathtutorbench_mistake_correction, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathtutorbench_socratic, mmtutorbench, mrbench_tutor |
| `glm-5.2` | `P18` 教育场景行为边界 | CEG | 未测过 | 0 | 0 | 1 | 0.0 |  |
| `glm-5.2` | `P19` 学生潜在风险识别与应对 | CEG | 未测过 | 0 | 0 | 1 | 0.0 |  |
| `glm-5.2` | `P20` 内容适龄与育人导向 | CEG | 未测过 | 0 | 0 | 2 | 0.0 |  |
| `gpt-5.4` | `P02` 长上下文与证据定位 | SRG | 8.0261 | 1 | 0 | 0 | 0.2 | sas_bench |
| `gpt-5.4` | `P05` 知识调用与掌握 | FDR | 6.9089 | 3 | 0 | 0 | 1.2 | pedagogy_benchmark, sas_bench |
| `gpt-5.4` | `P06` 推理与生成 | FDR | 5.5636 | 1 | 0 | 0 | 0.2 | sas_bench |
| `gpt-5.4` | `P11` 错误诊断 | LAD | 6.7949 | 2 | 0 | 0 | 1.0 | sas_bench |
| `gpt-5.4` | `P12` 主观题评价能力 | LAD | 7.3637 | 3 | 0 | 0 | 2.1 | asap_2, sas_bench |
| `gpt-5.4` | `P14` 学习者画像建模 | CLM | 7.9545 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `gpt-5.4` | `P15` 个性化教学策略选择 | CLM | 8.3234 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `gpt-5.5` | `P03` 多模态理解 | SRG | 5.757 | 1 | 0 | 0 | 0.17 | tutorbench |
| `gpt-5.5` | `P15` 个性化教学策略选择 | CLM | 5.757 | 1 | 0 | 0 | 0.17 | tutorbench |
| `gpt-5.5` | `P17` 适配性解释与反馈生成 | CLM | 5.757 | 1 | 0 | 0 | 0.425 | tutorbench |
| `kimi-k2-6` | `P02` 长上下文与证据定位 | SRG | 7.3299 | 1 | 0 | 0 | 0.2 | sas_bench |
| `kimi-k2-6` | `P05` 知识调用与掌握 | FDR | 6.6527 | 3 | 0 | 0 | 1.2 | pedagogy_benchmark, sas_bench |
| `kimi-k2-6` | `P06` 推理与生成 | FDR | 5.2204 | 1 | 0 | 0 | 0.2 | sas_bench |
| `kimi-k2-6` | `P11` 错误诊断 | LAD | 6.2751 | 2 | 0 | 0 | 1.0 | sas_bench |
| `kimi-k2-6` | `P12` 主观题评价能力 | LAD | 7.6214 | 2 | 0 | 0 | 1.3 | sas_bench |
| `kimi-k2-6` | `P14` 学习者画像建模 | CLM | 7.7273 | 1 | 0 | 0 | 0.2 | pedagogy_benchmark |
| `kimi-k2-6` | `P15` 个性化教学策略选择 | CLM | 8.1675 | 2 | 0 | 0 | 1.3 | pedagogy_benchmark |
| `kimi-k2-7-code` | `P04` 多模态生成 | SRG | 7.1484 | 1 | 0 | 0 | 0.35 | eduillustrate |
| `kimi-k2-7-code` | `P17` 适配性解释与反馈生成 | CLM | 7.1484 | 1 | 0 | 0 | 0.14 | eduillustrate |
| `kimi-k3-1-pro` | `P18` 教育场景行为边界 | CEG | 9.5 | 1 | 0 | 0 | 0.7 | education_boundary_v1 |
| `kimi-k3-1-pro` | `P20` 内容适龄与育人导向 | CEG | 9.1662 | 2 | 0 | 0 | 1.4 | age_values_v1 |
| `minimax-m2.7` | `P01` 指令与约束遵循 | SRG | 9.1078 | 1 | 0 | 0 | 1.0 | ifeval |
| `minimax-m2.7` | `P02` 长上下文与证据定位 | SRG | 7.1935 | 5 | 0 | 0 | 2.08 | longtutor_evidence, mathtutorbench_mistake_location, sas_bench |
| `minimax-m2.7` | `P03` 多模态理解 | SRG | 0.0 | 4 | 4 | 2 | 1.52 | k12vista, mathvista, mmtutorbench |
| `minimax-m2.7` | `P04` 多模态生成 | SRG | 0.0 | 1 | 1 | 0 | 0.35 | eduillustrate |
| `minimax-m2.7` | `P05` 知识调用与掌握 | FDR | 6.696 | 15 | 2 | 1 | 3.99 | agieval, ceval, edubench, k12vista, mathtutorbench_pedagogy, mathtutorbench_pedagogy_hard, mathtutorbench_problem_solving, mathtutorbench_scaffolding, mathtutorbench_scaffolding_hard, mathvista, mmlu_pro, pedagogy_benchmark, sas_bench |
| `minimax-m2.7` | `P06` 推理与生成 | FDR | 6.5822 | 10 | 2 | 1 | 3.065 | agieval, ceval, edubench, k12vista, mathtutorbench_mistake_correction, mathtutorbench_problem_solving, mathvista, mmlu_pro, sas_bench |
| `minimax-m2.7` | `P07` 自我校验与修正 | FDR | 5.8699 | 3 | 0 | 0 | 1.05 | mathtutorbench_solution_correctness, p07_selfcheck, p08_calibration |

## Coverage Notes

- `P18`/`P19`/`P20` use only education_boundary_v1, student_risk_v2, and age_values_v1 respectively. Old related safety benchmarks do not feed these scores.
- `P10` (general safety) awaits broad primary coverage; `P21` fairness remains exploratory. P20 requires both A/core and B; one alone is partial coverage.
- The active atomic list is `P01-P21` under v7/R28 numbering. CEG has no compensatory group average.

Full P rows are in `09_atomic_p_scores.jsonl`; allocated evidence rows are in `09_atomic_p_score_evidence.jsonl`.
