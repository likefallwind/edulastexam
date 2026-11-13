# Edu Last Exam V2 第一批原创样本

这是 **37 方向机制驱动数据生成流程的第一批样本**，包含 5 个新情境、11 个依赖投递版本。11 个版本不是 11 道独立题，5 个方向标签也不等于这些方向的全部子构念已经覆盖。适龄、安全与方向 36 只是未纳入第一批，不是永久排除。

全方向生产规则见 [37 方向机制驱动数据生成计划](../../docs/plans/edu_last_exam_37_direction_mechanism_generation_plan_2026-11-12.md)，逐方向蓝图见 `data/edu_last_exam_mechanism_generation_v1/direction_blueprints.json`。

## 设计原则

37 方向的原始构念、来源卡和机制蓝图决定数据如何生成。V1/V2 的成功或失败回答用于支持、反驳和修正机制，不再作为新题准入条件。第一批恰好都有 V1 失败依据，这是该批的创作历史，不是后续批次的筛选规则。

| 题族 | 新情境 | 首批创作时的机制依据 | 本批覆盖的部分子构念 |
|---|---|---|---|
| ELE-V2-12-001 | 植物实验电子表格 | 援助未知被当成无；提示后正确被当成独立掌握 | 三援助条件反事实＋实际分支探查＋提示污染检查 |
| ELE-V2-01-001 | 平均速度学生作品 | 正确的条件性非标准方法被误罚 | 合法捷径与标准路线中的真实错误并列＋申诉后复核 |
| ELE-V2-09-001 | 保温材料对照实验 | 目标完成后仍新增必交条件 | 目标证据位＋插问＋实际继续/结束动作 |
| ELE-V2-14-001 | 几何变换课件工作区 | 文字与产物不一致；教师参考错误；虚假交付声明 | 学生页/教师参考/delivery 文件一致性＋no-op 控制 |
| ELE-V2-33-001 | 成人语言学习记录 | 未观察被当成没有；一次表现被当成唯一原因 | 过程覆盖反事实＋证据状态 gold＋新证据续轮更新 |

V1 失败不自动证明 V2 难。本批后来已完成一次 GLM-5.3-Flash 探索性运行，结果和作者复核保存在 `reports/eval/edu_last_exam_v2_pilot/_exploratory/20261112_glm53flash_run01/`；这不是独立教师审核、多模型难度证据或冻结结论。

## 文件与工作流

- `cards.jsonl`：题族与 37 方向机制蓝图的绑定、planned controls 和可选 V1 失败证据。
- `authored/`：完整候选题、gold、rubric、controls 和 runtime；其中 `model_evaluation=not_run` 是创作时状态快照。
- `stimuli/`：本批原创合成记录；不冒充真实学生数据。
- `items.jsonl`、`prompts.jsonl`、`runtimes.json`、`reference/`、题册、审阅册和 manifest：由构建器生成，不手改。
- `reports/edu_last_exam_v2_pilot/`：由构建器生成的离线验证与实现状态。

```bash
/usr/bin/python3 scripts/build/build_edu_last_exam_v2_pilot.py
/usr/bin/python3 scripts/build/build_edu_last_exam_v2_pilot.py --validate-only
/usr/bin/python3 scripts/build/build_edu_last_exam_v2_pilot.py --protocol data/edu_last_exam_v2_pilot/protocol.json
PYTHONPATH=. /usr/bin/python3 -m pytest -q tests/test_edu_last_exam_v2_pilot.py
```

`--validate-only` 不写文件，并检查所有生成物是否存在且与当前源逐字节一致。构建器要求每个题族绑定方向机制、来源卡和 controls；只有提供 V1 失败证据时，才检查对应案例确实存在于复核记录且 verdict 为 `fail`。后续批次使用新的 protocol、batch、item ID 和运行目录。

## 运行边界

复用现有 full-coverage 的真实续轮、动作分支和隔离工作区，不新增 runner、judge 或 artifact validator。隐藏 gold、rubric 和未来 observation 不进入预测输入。

```bash
/usr/bin/python3 scripts/experiments/run_edu_last_exam_full_coverage.py \
  --batch private/edu_last_exam_v2_pilot \
  --output tmp/edu_last_exam_v2_pilot/dry_run_<id> \
  --model UNSELECTED-PANEL --dry-run
```

这只验证投递与环境兼容，不调用 API。任何实际试跑都应写入新的隔离目录，并分别报告各题族和版本；不把不同构念合成一个总正确率。

## 当前状态

- 作者：Kimi；GLM-5.3-Flash 未参与本批题目创作。
- `human_review=pending`；`frozen=false`；`canonical=false`；模型运行状态由独立 run manifest 记录。
- 分支学生回应是确定性模拟，不是自然学生模型；工作区是隔离教学材料环境，不是生产 LMS。
- 题目数量、作者离线检查和 V1 错误依据均不能替代独立教师审核与跨模型验证。
