# Edu Last Exam v1（测试候选集）

这是从 `challenge_v2` 逐题审查后选出的第一批小规模测试题，不是已经完成效度验证的公开排行榜版本。选择清单见 [`selection.json`](selection.json)，逐题审查见 [`../../docs/reviews/edu_last_exam_challenge_v2_audit_2026-11-09.md`](../../docs/reviews/edu_last_exam_challenge_v2_audit_2026-11-09.md)。

## 题集边界

首版包含 8 个任务包：C2-01、C2-03、C2-09、C2-10、C2-12、C2-13、C2-16、C2-20。任务包内的多个 prompt 或执行阶段仍属于同一个教育任务，报告时按任务包聚合，不能把变体数量当成独立题数。

首版同时保留三个测量边界：

- C2-01、09、10、12、13、16 是核心文字、决策或评估设计轨道；
- C2-03 是评分稳健性控制，不能因为它通过率高就宣称题集失败；
- C2-20 是独立 artifact 轨道，必须分别保存交付物、脚本/浏览器验收和人工审阅状态。

C2-16 当前是一次性交付的静态测评设计题。它要求模型设计一个“两阶段学生题”，但本仓库的首版 runner 不会真的在第一阶段和第二阶段之间向模型发放读数，因此不能把结果表述为真实多轮实验能力。

## 运行和状态

使用构建器从 challenge_v2 复制题面、参考材料和离线检查，并写入 `private/edu_last_exam_v1/`：

```bash
python scripts/build/build_edu_last_exam_v1.py
python scripts/build/build_edu_last_exam_v1.py --validate-only
```

当前状态字段明确写作 `test_release_candidate`、`human_review: owner_review_pending`、`model_evaluation: not_run`、`difficulty_status: not_measured`。在专家审核、对照题和跨模型试跑完成前，不发布整体通过率、排行榜或“绝大多数 Agent 不通过”的结论。

题目设计遵循三个独立判断：题目是否有真实教育构念和可观察失败机制；受测模型是否在该任务上失败；评分器是否能够稳定识别失败。一次模型回包只能支持探索性错误分析，不能替代后两项验证。
