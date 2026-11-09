# edu_last_exam_pilot_v1

> 2026-11-07 新增：[challenge_v2 挑战候选](challenge_v2/README.md)，覆盖重新讨论的 21 个方向并包含图像/交互材料；与下面的原 12 题版本分开维护。新批次尚未模型实测。

自建的小规模高难教育能力题集，用来测试当前 frontier 模型在真实教育场景里最容易失守的四类能力：

1. **评分稳健性**：不因附注、空白、标签、学生抗辩或外部预置分而改变判断；
2. **教师意图执行**：守住教师设定的步骤、边界和认知深度；
3. **诊断与教学决策**：基于学生证据选择合适教学动作，而不是给通用解释；
4. **命题与难度校准**：识别题目缺陷、难度标签失真，并给出可执行修正。

本集不做图像题；图像与交互类任务暂缓，见 `deferred_visual_tasks.md`。

## 为什么做 Edu Last Exam

Edu Last Exam 不测“模型会不会做学科题”，而测“模型能不能胜任真实教育岗位里最易失守的判断类工作”：读学生的真实作答证据、抵抗操纵、执行教师意图、诊断学生状态、审查命题质量。完整设计讨论（构念优先、三类题目用途、对照与消融、发布纪律）见 `../../reports/research/edu-frontier-last-exam-design-2026-11-04.html`。

任务族不来自想象，直接取自 2026 年最新失败证据（见下表）；旧模型已修复的失败（如 GPT-4 基础算术）只保留任务形式，不作为当前能力证据复测。

## 证据基础与出题优先级

按“当前 frontier 模型仍实际失败 × 对真实教学后果影响大 × 可静态复验”排序：

| 任务族（优先级） | 依据（2026 证据） | 来源 |
|---|---|---|
| `grading_robustness`（P0，5 题） | 22 个模型中 14 个因夹带注记提分、17 个因裸抗辩让步多于复核请求、7 个给空白/无意义作答记分 | [AI Grading Benchmark 2026](https://reports.learningdesignalliance.org/ai-grading-benchmark-2026/1.0.0/report/index.html) |
| `teacher_intent`（P1，2 题） | 真实课堂会话 53.8% 跳过教师设定流程；目的对齐率仅 59.3%；37.7% 会话未达到教师设定的认知深度 | [EduWild](https://arxiv.org/html/2610.23530v1)、[Will It Teach as Intended?](https://arxiv.org/html/2609.29993)、[TASD](https://arxiv.org/html/2604.16738) |
| `diagnostic_teaching`（P1，3 题） | 最强模型开放案例干预符合率仅 55.8%；长历史诊断最佳 Macro-F1 39.7%；反馈常不定位学生首错 | [TutorCaseBench](https://arxiv.org/html/2610.30828)、[LongTutor, ACL 2026](https://aclanthology.org/2026.acl-long.1371.pdf)、[MathEDU, EACL 2026](https://aclanthology.org/2026.eacl-long.132.pdf) |
| `assessment_design`（P2，2 题） | 模型难度标签与实测学生难度相关仅 ρ=0.06；教师—AI 命题仍产出无效或线索化选项 | [AI 难度标签课堂研究](https://arxiv.org/html/2609.27063)、[ENEM 难度估计](https://arxiv.org/html/2602.06631)、[教师—AI 命题缺陷](https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2026.1831250/full) |

逐题 `source_evidence` 字段引用的短名与上表一一对应。完整案例、输入/错误输出/预期输出对照和旧案例处置见 `../../reports/research/education-llm-frontier-failure-cases-2026-11-06.html`。

## 组成

- 12 题；
- 4 个任务族：
  - `grading_robustness`：5 题
  - `teacher_intent`：2 题
  - `diagnostic_teaching`：3 题
  - `assessment_design`：2 题
- 每题均为文本任务；
- 每题带：
  - 明确输入；
  - 期望输出结构；
  - 硬门槛（hard gates）；
  - 主要评分标准；
  - 次要评分标准；
  - 禁止行为；
  - 预期金标或可接受答案范围。

## 判分

通用规则见 `judge_contract.md`。每题的 `scoring` 字段是该题主分合同，优先级高于通用规则。

- 主分：0–10 分；
- 任一硬门槛失败，主分为 0；
- 主分 ≥ 8 且硬门槛全过，记 `pass=true`；
- 其余记 `pass=false`；
- 不把回答长度、礼貌程度或格式美观单独加分。

## 状态

- 题目与判分合同已完成初稿，并已接入评测框架（`scripts/eval/benchmarks/edu_last_exam_pilot.py`）；
- MiniMax-M3 与 GLM-5.3 并发 2 的全量 run 已完成，均为探索性结果（各 12/12 scored、各 pass 9/12），不作为稳定榜单或能力结论；
- 已知题目缺陷：ELE-GR-001 金标与题面评分标准矛盾——学生把 2^3、2^2 的值写反，按题面五项标准应得 3 分，金标误写为 5 分；两个模型给出的 3 分判分与忽略夹带注记的行为均正确，修正金标后真实 pass 应为 10/12。金标修复前该题结果无效；
- 两个模型的真实共享失败为 ELE-GR-002（空白作答后反馈直接给出完整答案）与 ELE-GR-003（抗辩下维持分数但不说明“未提供新证据”）；
- 尚未做人工双人校准；
- 图像题暂缓。

## 文件

| 文件 | 作用 |
|---|---|
| `taxonomy.json` | 任务族、题量、判分策略和暂缓项的机器可读规格 |
| `judge_contract.md` | 通用裁判规则与各任务族补充标准 |
| `deferred_visual_tasks.md` | 图像/交互类任务的 TODO，不进入本版题库 |

题目本体在 `private/edu_last_exam_pilot_v1/`，由 `scripts/build/build_edu_last_exam_pilot_items.py` 校验并导出。
