# Edu Last Exam

Edu Last Exam 是一个独立维护的教育场景 benchmark 仓库。它要测的不是模型能否回答一道普通学科题，而是模型能否在真实教育工作中稳定完成高风险、证据依赖、带约束的判断与行动：理解学生作品，诊断学习状态，执行教师意图，设计和审查教学内容，进行可靠评价，并在需要时跨轮维护状态。

本仓库由 `/home/likefallwind/code/edubenchmark` 中已经完成的 Edu Last Exam 调研、方案、候选题、试跑结果和必要的评测基础设施复制而来。复制发生在 2026-11-09；源仓库仍然保留原内容，且仍是跨 benchmark 结果的主要来源。本仓库以后承载 Edu Last Exam 的题目开发、审核和专用实验。

## 当前状态

- 证据矩阵和总体方案已经形成，见 [`docs/evidence/edu_last_exam_evidence_matrix_2026-11-09.md`](docs/evidence/edu_last_exam_evidence_matrix_2026-11-09.md) 和 [`docs/plans/edu_last_exam_integrated_plan_2026-11-08.md`](docs/plans/edu_last_exam_integrated_plan_2026-11-08.md)。
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

1. 对 [`private/edu_last_exam_v1/review.md`](private/edu_last_exam_v1/review.md) 做 owner 级逐题确认，特别是静态测评和 artifact 轨道的验收边界。
2. 先用小模型面板和独立评分器试跑 v1，按任务包记录通过、错误类型和评分一致性，不先汇总总分。
3. 根据试跑补做多模态、成对一致性、HTML/SVG 渲染和公平控制轨道。
4. 只有完成专家审核、对照/消融和跨模型验证后，才讨论正式版本和公开报告。

