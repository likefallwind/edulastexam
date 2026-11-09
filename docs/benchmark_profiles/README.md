# Benchmark 档案

主计分体系里**每个 benchmark_id 一份档案**：它是什么、谁做的、数据从哪来、怎么判分、我们怎么用它、有什么局限。目的是让映射裁决和对外解释时不用翻论文——所有"这个分数到底在测什么"的问题在这里有答案。

事实来源：官方论文/仓库、本仓库的调研库存（`doc/edubench.md`、`data/exhaustive_2026-05-13/`）、adapter 实现（`scripts/eval/benchmarks/`）、otherbenchmark 报告，以及 13 号映射效度检查的实测统计。**当前区分度统计以 2026-11-02 的 v7/R28 13 号检查为准**：主报告见 `reports/atomic_ability_rebenchmark/13_mapping_validation.md`，逐 cell 数据见 `reports/atomic_ability_rebenchmark/13_mapping_validation_cells.jsonl`。其中 n 是该 cell 的共同模型数，不是全局面板大小；均分/标准差按 0–10 归一分，并须结合具体 subdimension 和 variance-restriction 标记解读。

另有 2026-11-02 的 `reports/benchmark_health_index_pilot/` 隔离试验：固定 8 模型 × 28 benchmark，只计算 Tech-BHI-static 两轴，数据截至 2026-11-01。它是非 canonical 的方法试验，只支持宽层级解读，不替代 13 号结果，也不并入正式能力画像。

## 一个 id 一份档案

档案文件名必须等于 benchmark_id（唯一例外 `mooccube_prereq` → `mooccube.md`，走 `PROFILE_MAP`）。

这条规则是改出来的。此前 17 个子评测 id 折叠到 5 份家族档案上，结果是：点进 `mathtutorbench_socratic` 看到的是整个家族的九行任务表，其中八行与这个格子无关；而家族档案「当前映射」一节说的 P 列表，与该 id 实际挂载的 P 对不上。现在每个 id 自带档案，开头点明它是家族里的哪一个、与兄弟子评测什么关系。

下面五份是**家族背景文档**，保留供阅读，构建脚本不再读取：`mathtutorbench.md`、`eduguard_bench.md`、`mrbench.md`、`bea2025.md`、`p08_selfbuilt.md`。

## 档案索引

### 门槛与通识

| 文件 | 一句话 |
|---|---|
| [mmlu_pro.md](mmlu_pro.md) | 高难版 MMLU，10 选 1 学科知识 |
| [ceval.md](ceval.md) | 中文 52 学科考试选择题 |
| [agieval.md](agieval.md) | 高考/SAT/法考等标准化考试原题 |
| [olympiadbench.md](olympiadbench.md) | 奥赛级数学物理开放题 |
| [ifeval.md](ifeval.md) | 可验证指令遵循，规则判分 |
| [diagsafe.md](diagsafe.md) | 中英双语通用安全，逐题 rubric、原生多轮；P10 已选定，待全量挂分 |

### 多模态

| 文件 | 一句话 |
|---|---|
| [mathvista.md](mathvista.md) | 图文数学推理 |
| [k12vista.md](k12vista.md) | 中文 K12 图文学科题 |
| [mmtutorbench.md](mmtutorbench.md) | 视频关键帧数学辅导 |
| [eduillustrate.md](eduillustrate.md) | 生成 Manim 可视化讲解 |

### 教育核心（单 id）

| 文件 | 一句话 |
|---|---|
| [edubench.md](edubench.md) | 中文教育场景生成，9 场景 12 指标 |
| [pedagogy_benchmark.md](pedagogy_benchmark.md) | 教师资格考试教学法选择题 |
| [tutorbench.md](tutorbench.md) | 真实多模态辅导，rubric 判分 |
| [edu_last_exam_pilot_v1.md](edu_last_exam_pilot_v1.md) | 自建 12 题高难教育 pilot，逐题硬门槛与权重判分 |
| [asap_2.md](asap_2.md) | 英文作文自动评分 |
| [sas_bench.md](sas_bench.md) | 高考主观题分步评分 + 错因诊断 |
| [mooccube.md](mooccube.md) | 先修关系推理（id `mooccube_prereq`） |
| [p07_selfcheck.md](p07_selfcheck.md) | 无提示两轮自查，改对率 vs 改错率 |

### MathTutorBench 九个子任务

家族背景见 [mathtutorbench.md](mathtutorbench.md)。四个规则判分的硬任务 + 一个 BLEU 判分 + 四个胜率判分的开放任务。

| 文件 | 一句话 |
|---|---|
| [mathtutorbench_problem_solving.md](mathtutorbench_problem_solving.md) | 纯解题，门槛用 |
| [mathtutorbench_solution_correctness.md](mathtutorbench_solution_correctness.md) | 判学生解对错 |
| [mathtutorbench_mistake_location.md](mathtutorbench_mistake_location.md) | 定位首处错误步骤 |
| [mathtutorbench_mistake_correction.md](mathtutorbench_mistake_correction.md) | 给出改对的解答 |
| [mathtutorbench_socratic.md](mathtutorbench_socratic.md) | 引导性提问，BLEU 判分 |
| [mathtutorbench_scaffolding.md](mathtutorbench_scaffolding.md) | 搭脚手架；当前 13 号面板中为家族内高离散度 cell |
| [mathtutorbench_scaffolding_hard.md](mathtutorbench_scaffolding_hard.md) | 脚手架 hard，与常规版 r=0.98 |
| [mathtutorbench_pedagogy.md](mathtutorbench_pedagogy.md) | 按给定教学法生成回复 |
| [mathtutorbench_pedagogy_hard.md](mathtutorbench_pedagogy_hard.md) | 教学法 hard，与常规版 r=0.92 |

### 成对子评测

| 文件 | 一句话 |
|---|---|
| [eduguard_sata.md](eduguard_sata.md) | 教学伤害知识全选题（家族见 [eduguard_bench.md](eduguard_bench.md)） |
| [eduguard_adversarial.md](eduguard_adversarial.md) | 801 条越狱提示；v7 中仅作通用安全与学业边界的关联证据 |
| [bea2025_tutor.md](bea2025_tutor.md) | 生成 tutor 回复，4 维标注（家族见 [bea2025.md](bea2025.md)） |
| [bea2025_judge.md](bea2025_judge.md) | 当裁判贴标签，与人类金标比 |
| [mrbench_tutor.md](mrbench_tutor.md) | 生成 tutor 回复，8 维标注（家族见 [mrbench.md](mrbench.md)） |
| [mrbench_judge.md](mrbench_judge.md) | 当裁判贴 8 维标签 |
| [p08_calibration.md](p08_calibration.md) | 自报置信度 vs 实际正确率（家族见 [p08_selfbuilt.md](p08_selfbuilt.md)） |
| [p08_abstention.md](p08_abstention.md) | 不可答题的弃答表现 |

### LongTutor 三个子评测

| 文件 | 一句话 |
|---|---|
| [longtutor_evidence.md](longtutor_evidence.md) | 长材料证据定位，按记忆类型三分 |
| [longtutor_diagnosis.md](longtutor_diagnosis.md) | 从长历史诊断学生知识状态 |
| [longtutor_teaching.md](longtutor_teaching.md) | 长历史下的教学动作选择 |

### 教育安全与公平

| 文件 | 一句话 |
|---|---|
| [education_boundary_v1.md](education_boundary_v1.md) | P18 唯一暂定主测，检验诱导、压力与正常对照中的教育角色边界 |
| [student_risk_v2.md](student_risk_v2.md) | P19 唯一暂定主测，联合考察学生风险识别与相称应对 |
| [age_values_v1.md](age_values_v1.md) | P20 唯一暂定主测，分别报告适龄内容与育人导向两个必要 facet |
| [eduequity.md](eduequity.md) | P21 的身份反事实探索性证据，暂无正式计分 cell |

## 档案模板

**单 id 的 benchmark**：出处与背景 / 数据 / 任务与判分 / 在本仓库怎么用 / 局限与注意。

**子评测**：这是哪个子评测（家族、兄弟子评测、为什么分开计分）/ 出处与背景 / 任务与判分 / 局限与注意。

## 写作约定

- **不写权重数字、不写映射清单。** `当前映射` 小节会被解析器丢弃，网站上的权重表由 `data/mapping_measurement_model_v7.json` 生成。老档案里残留的 `当前映射` 一节可能使用旧 P 编号，不要照抄。
- H1 标题就是网站上的页面标题，子评测请写成 `家族 · 子任务名`。
- `**一句话**：…` 紧跟 H1，是卡片和页面导语。
- 每行一条 bullet，自成一句；表格和代码块会被解析器丢弃。

配套文档：缺口推荐 `doc/benchmark_gap_recommendations_2026-07-11.md`、历史构念核对 `doc/old/p_construct_review_2026-07-11.md`。

## 网站公开内容契约（2026-11-03）

公开目录由 `data/benchmark_public_catalog.json` 独立维护，不以能力计分 cell 枚举。目录包含当前任务档案及已接入的评测任务；家族背景文档不单独计为 Benchmark。尚无成绩、探索性任务与校准占位保留自己的状态，不因出现在目录中而获得能力分。

每份档案的 H1、`一句话` 和 `公开介绍` JSON 块是网站公开文案的唯一来源。`scripts/benchmark_public_profiles.py::load_public_profiles(root)` 仅导出这些字段、出处与经核验例题；下面的内部协议、历史映射、运行命令和长篇方法讨论不进入产品页面。已有历史章节保留供研究复核，不能作为当前运行状态的替代。

真实题例由目录声明固定本地文件 SHA-256、原始 item ID 或固定行位置、允许公开的字段、来源与许可依据。加载时重新核对哈希和题目身份；来源漂移、字段缺失或授权声明不满足要求时停止导出，不自动换题。MathTutorBench Scaffolding 例题另与 MathDial 原始题目和参考解交叉核验，避免误用 BRIDGE 内容。只导出选定原文，不复制整个数据集，不导出作者画像、隐藏 gold 或内部控制字段。三个自建题集的正常对照例题由维护者明确授权展示；该许可不改写整库对外授权。LongTutor 只保留来源入口，不再分发题目。

离线检查：`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/test_benchmark_public_profiles.py`。实际源核验：`PYTHONDONTWRITEBYTECODE=1 python3 scripts/benchmark_public_profiles.py`。两者不运行模型、不重建评测报告。
