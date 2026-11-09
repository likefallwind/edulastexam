# edu_last_exam_pilot_v1

**一句话**：自建 12 题高难教育 pilot，检验批改稳健性、教师意图执行、诊断教学和命题审查。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "覆盖四类当前教育 LLM 易失败的高难能力：批改稳健性、教师意图执行、诊断教学和命题审查。",
    "每题带有硬门槛、10 分制评分合同和禁止行为；任一硬门槛失败记 0 分，总分 ≥8 且硬门槛全过才通过。"
  ],
  "facts": [
    {
      "label": "数据规模",
      "value": "12 题"
    },
    {
      "label": "构成",
      "value": "批改稳健性 5 题、教师意图 2 题、诊断教学 3 题、命题审查 2 题"
    },
    {
      "label": "形式",
      "value": "纯文本单轮；图像与交互任务暂缓"
    }
  ],
  "credits": [
    {
      "text": "Edu Benchmark 维护者，自建题集，2026",
      "url": "https://github.com/likefallwind/edubenchmark/blob/codex/scenario-capability-benchmark/data/edu_last_exam_pilot_v1/README.md"
    }
  ]
}
```
<!-- public-profile:end -->

## 状态

2026-11-06 建立自建 pilot 题集和 adapter。12 道题与逐题判分合同已生成并通过自动校验；尚未接入稳定能力映射，也未完成双人标注校准。已有 MiniMax-M3 与 GLM-5.3 全量试跑，均只作为探索性结果，不作为稳定排行榜或能力结论。

已知题目缺陷：`ELE-GR-001` 金标与题面评分标准矛盾（学生把 2^3、2^2 写反，按标准应得 3 分，金标误为 5 分），金标修复前该题结果无效；修正后两模型真实 pass 应为 10/12。两模型真实共享失败为 `ELE-GR-002`（空白作答后反馈直接泄题）与 `ELE-GR-003`（抗辩下维持分数但不说明无新证据）。

## 动机与证据

本集不测学科解题，测教育岗位判断类工作的失守点。设计讨论见 `reports/edubenchassistant/edu-frontier-last-exam-design-2026-11-04.html`。四个任务族直接映射 2026 最新失败证据，按“仍实际失败 × 教学后果 × 可静态复验”排优先级：

- `grading_robustness`（P0）：14/22 模型因夹带注记提分、17/22 因裸抗辩让步、7 个给空白作答记分 — [AI Grading Benchmark 2026](https://reports.learningdesignalliance.org/ai-grading-benchmark-2026/1.0.0/report/index.html)；
- `teacher_intent`（P1）：53.8% 会话跳过教师流程、目的对齐 59.3%、37.7% 未达设定认知深度 — [EduWild](https://arxiv.org/html/2610.23530v1)、[Will It Teach as Intended?](https://arxiv.org/html/2609.29993)、[TASD](https://arxiv.org/html/2604.16738)；
- `diagnostic_teaching`（P1）：开放案例干预符合率 55.8%、长历史诊断 Macro-F1 39.7%、反馈不定位首错 — [TutorCaseBench](https://arxiv.org/html/2610.30828)、[LongTutor](https://aclanthology.org/2026.acl-long.1371.pdf)、[MathEDU](https://aclanthology.org/2026.eacl-long.132.pdf)；
- `assessment_design`（P2）：难度标签与实测难度 ρ=0.06、教师—AI 命题仍有无效选项 — [难度标注课堂研究](https://arxiv.org/html/2609.27063)、[ENEM 难度估计](https://arxiv.org/html/2602.06631)、[教师—AI 命题缺陷](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2026.1831250/full)。

逐题 `source_evidence` 与上列来源一一对应；完整案例见 `reports/edubenchassistant/education-llm-frontier-failure-cases-2026-11-06.html`。

## 构念

本集用于探测当前 frontier 模型在真实教育任务中的四类残余失败：

1. **批改稳健性**：不被答案内注记、空白作答、学生抗辩、预置分数或强/弱标签改变评分；
2. **教师意图执行**：按教师设定的工作流、边界和认知深度行动；
3. **诊断教学**：基于可见证据定位困难并选择匹配的教学策略；
4. **命题审查**：基于实测数据和 item-writing 原理判断题目难度与质量。

图像与交互任务暂缓，规格见 `data/edu_last_exam_pilot_v1/deferred_visual_tasks.md`。

## 题集

`private/edu_last_exam_pilot_v1/items.jsonl` 共 12 题：

- `grading_robustness`：5 题；
- `teacher_intent`：2 题；
- `diagnostic_teaching`：3 题；
- `assessment_design`：2 题。

每题包含：

- 系统提示；
- 用户输入；
- 期望输出结构；
- 金标或可接受答案范围；
- 硬门槛；
- 10 分制评分标准；
- 禁止行为。

## 判分

固定 LLM judge 依据逐题合同输出：

- `hard_gates`：逐项 true/false；
- `criteria_scores`：每个标准在该权重内的得分；
- `total_score`：0–10；
- `pass`：所有硬门槛通过且总分 ≥8。

任一硬门槛失败时，adapter 强制总分为 0，不采用 judge 自报总分。主指标为 pass rate；另报告 mean score、hard gate pass rate 和四个 family 的分层结果。

## 局限与注意

- 这是 12 题 pilot，样本极小，不能支撑稳定模型排名；
- 尚未做两名教育者逐题审查和双人标注校准；
- judge 仍为 LLM，硬门槛只能降低主观性，不能完全消除；
- 图像与交互任务未纳入；
- 结果目录为探索性 run，不应并入 P01–P21 稳定画像。

## 运行

    python3 scripts/build_edu_last_exam_pilot_items.py validate-only
    python3 scripts/build_edu_last_exam_pilot_items.py export
    LIMIT=3 MODEL=MiniMax-M3 CONCURRENCY=2 EXTRACT_CONCURRENCY=2 ./scripts/run_eval.sh edu_last_exam_pilot_v1
    MODEL=MiniMax-M3 CONCURRENCY=2 EXTRACT_CONCURRENCY=2 ./scripts/run_eval.sh edu_last_exam_pilot_v1
    GLM_API=<key> MINIMAX_API_KEY=<key> MODEL=GLM-5.3 CONCURRENCY=2 EXTRACT_CONCURRENCY=2 ./scripts/run_eval.sh edu_last_exam_pilot_v1
