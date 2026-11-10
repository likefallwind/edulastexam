# Edu Last Exam

Edu Last Exam 是一个独立维护的教育场景 benchmark 仓库。它要测的不是模型能否回答一道普通学科题，而是模型能否在真实教育工作中稳定完成高风险、证据依赖、带约束的判断与行动：理解学生作品，诊断学习状态，执行教师意图，设计和审查教学内容，进行可靠评价，并在需要时跨轮维护状态。

本仓库由 `/home/likefallwind/code/edubenchmark` 中已经完成的 Edu Last Exam 调研、方案、候选题、试跑结果和必要的评测基础设施复制而来。复制发生在 2026-11-09；源仓库仍然保留原内容，且仍是跨 benchmark 结果的主要来源。本仓库以后承载 Edu Last Exam 的题目开发、审核和专用实验。

## 当前状态

- [全方向探索候选 v1](private/edu_last_exam_full_coverage_v1/README.md)已落实清单37个方向的38个基础案例、82个投递版本及评分协议。包括真实续轮、分支动作、隔离工作区、跨会话记忆、可渲染教学产物和真实媒体素材。阅读[题册](private/edu_last_exam_full_coverage_v1/questions.html)、[评分审阅册](private/edu_last_exam_full_coverage_v1/review.html)及[逐项测量边界](reports/full_coverage_v1/implementation_status.html)。这是全量探索候选；人审、当前模型难度和未覆盖子结论分别记录，不是冻结benchmark。
- [中性题面对照](private/edu_last_exam_scenario_neutral_v1/README.md)保留原5包/12版本的附件、答案和rubric，仅移除系统及任务中的定向提示。可看[逐包题面对照](private/edu_last_exam_scenario_neutral_v1/prompt_comparison.html)。基线GLM试跑得到22份有效回答、2次图片接口拒绝；中性版结果独立记录，不将接口错误计作答题错误。
- [场景研究首批候选题](private/edu_last_exam_scenario_v1/README.md)已完成作者离线核验：5个任务包、12个独立投递版本（含2个原图版本），覆盖首错/参考稿复核、真实手写作品审查、学习历史诊断。可直接读[题册](private/edu_last_exam_scenario_v1/questions.html)和[审阅册](private/edu_last_exam_scenario_v1/review.html)。当前模型难度未测、专家审核pending、未冻结。
- 完整研究依据见 [AI 在教育应用中的薄弱点：文献与本仓库实验完整对照（2026-11-10）](docs/evidence/edu_last_exam_complete_evidence_inventory_2026-11-10.md)，另有 [HTML 阅读版](reports/research/edu-last-exam-complete-evidence-inventory-2026-11-10.html)。清单逐项区分文献、本地实验、当前判断和未验证部分；它是研究证据快照，不是冻结 benchmark 结论。[首批易错场景与证据核验](docs/evidence/edu_last_exam_scenario_shortlist_2026-11-10.md)保留为前期记录。先核实具体失败场景与成功反例，再设计少量题目；原题复用、改编、自建按场景适配性选择，不设置复用优先级。
- [11 月 9 日证据矩阵](docs/evidence/edu_last_exam_evidence_matrix_2026-11-09.md) 和 [11 月 8 日总体方案](docs/plans/edu_last_exam_integrated_plan_2026-11-08.md) 保留为前期研究记录，不要求按原子能力或 21 个方向凑齐题目。
- `edu_last_exam_pilot_v1` 保留了原来的 12 题版本、题目规范和已跑过的 smoke 结果。
- `challenge_v2` 是 21 个方向的研究启发式候选集，作者离线检查已通过，但人工审核和跨模型难度测量仍未完成；它不能被当作已经冻结的 Last Exam。
- [`data/edu_last_exam_v1/`](data/edu_last_exam_v1/) 和 [`private/edu_last_exam_v1/`](private/edu_last_exam_v1/) 是从 challenge_v2 逐题审查后选出的 8 个任务包测试候选集；构建报告和状态字段明确标记为 `test_release_candidate`，不是正式排行榜版本。
- 目前不宣称“绝大多数 Agent 不通过”。只有在题目完成专家审核、对照/消融设计、跨模型测试和评分协议校准后，才会形成正式 benchmark 结论。

## 设计原则

教育场景分类是第一层：评分与反馈、学生诊断与教学决策、教师意图执行、内容和教学产物、命题与评估设计等。P01–P21 原子能力是第二层解释轴；一个 case 不必强行标记原子能力，若标记只能使用 [`docs/atomic_ability_mapping_v7_2026-11-02.md`](docs/atomic_ability_mapping_v7_2026-11-02.md) 中的既有编号和名称。是否需要长周期、多轮对话或显式维护学生状态，由具体构念决定，不作为所有题目的统一门槛。

每道题都要有可观察的失败机制、充分但不泄漏答案的输入、可复核的参考解和评分标准，并区分：题目本身有挑战、模型确实失败、评分器能可靠识别这三件事。现有候选题的状态和限制必须在导出物中保留，不能用一次模型试跑替代题目效度证据。

## 目录

| 路径 | 用途 |
|---|---|
| `docs/plans/` | 方案、研究计划和方向提案 |
| `docs/evidence/` | 文献与仓库实验证据矩阵 |
| `docs/benchmark_profiles/` | 相关 benchmark 和本项目 profile |
| `data/` | 机器可读规范、taxonomy、原子能力映射 |
| `private/edu_last_exam_pilot_v1/` | 自建题目、刺激材料、参考解、审核表和导出稿 |
| `private/edu_last_exam_v1/` | 首版 8 个任务包测试候选题、刺激材料、参考解、检查和 manifest |
| `reports/research/` | 调研报告和讨论产物 |
| `reports/challenge_v2/` | challenge_v2 的作者检查与模型审阅证据 |
| `reports/eval/` | 已复制的试跑结果和耐久运行元数据 |
| `scripts/` | 题目构建器、评测入口和可复用评测代码 |
| `tests/` | 离线回归测试 |

## 常用离线命令

```bash
python scripts/build/build_edu_last_exam_pilot_items.py --help
python scripts/build/build_edu_last_exam_challenge_items.py --validate-only
python scripts/build/build_edu_last_exam_v1.py --validate-only
python scripts/build/build_edu_last_exam_v1.py
pytest -q tests
```

v1 仍使用隔离的探索性投递器；通过 `--batch` 指向 v1，模型回包只保存不自动判分或执行产物：

```bash
python scripts/experiments/run_edu_last_exam_challenge_v2.py \
  --batch private/edu_last_exam_v1 \
  --output reports/eval/edu_last_exam_v1/_exploratory/<model>/<run-id> \
  --model <model> --dry-run
```

完整的 API 评测需要相应数据集、凭据和明确的模型实验计划。不要把 `scripts/eval/` 中复制的通用适配器误认为所有依赖已经随本仓库提供；下载数据放在 `sources/datasets/`，不提交到 Git。

## 下一步

1. 按[全方向计划](docs/plans/edu_last_exam_next_stage_plan_2026-11-10.md)用GLM-5.3-Flash并发4运行全部候选；逐方向保留错误、成功、接口未测与争议，完成后再决定深测范围。
2. 对实际回答进行评分初审与独立教师复核；同模型语义评分仅作探索证据，17的连续指标单列，禁止混成一个总正确率。
3. 按[研究待办](docs/plans/benchmark-todo.md)补未覆盖子结论、材料许可及评分校准；真实学习效果和自然课堂长期效度不由模拟互动替代。
4. 完成专家审核、对照/消融和跨模型验证后，才讨论正式版本和公开报告；通过的题可以转为回归或控制题。

