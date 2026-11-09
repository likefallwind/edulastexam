# Edu Last Exam：教育场景 × P01–P21 证据矩阵

版本：evidence matrix v1 · 2026-11-09  
用途：第一阶段证据整理；尚未进入正式数据集设计或题目冻结。

## 1. 这张矩阵要回答什么

本阶段只回答一个问题：**哪些教育场景中，当前 Agent 仍可能存在有教育意义、可复核、值得继续验证的共同短板？**

矩阵不把低分自动当作能力失败，也不把单篇论文的案例自动当作普遍结论。每个判断同时看：

- 近两年是否有直接行为证据；
- 本仓库是否有跨模型或跨题目的结果；
- 是否有近期强模型成功反例；
- 失败是否具有教育后果；
- 是否能够建立人类金标和可复核判分；
- 这个问题是否需要 Turn、Session 或 Episode 才能测清楚。

### 证据状态

| 状态 | 含义 |
|---|---|
| **A：优先复核** | 仓库和/或近两年研究已有直接失败信号，教育后果和判定边界较清楚 |
| **B：候选补强** | 方向有意义，也有部分信号，但构念混合、样本单一、协议有限或缺少当前模型复测 |
| **C：覆盖缺口** | 原子能力重要，但仓库尚无可靠直接测量；不能用相邻能力分数代替 |
| **D：当前不优先** | 现有结果总体较成熟，或当前证据不足以支持把它作为 Last Exam 核心短板 |

P01–P21 的名称和 facet 只采用仓库 v7 当前口径：[原子能力说明](../atomic_ability_mapping_v7_2026-11-02.md)、[机器可读 mapping](../../data/mapping_measurement_model_v7.json)。一个 case 不强制标注 P；下表的 P 映射是证据组织和后续复测候选，不等于已完成直接测量。

## 2. 仓库结果总览

当前 v7/R28 面板中，最值得继续核验的低分或共同失败信号集中在：

| 仓库 benchmark | 当前结果 | 当前 P 映射 | 初步解释 |
|---|---:|---|---|
| SAS-Bench ECS 错因一致性 | 5.06/10，11 个模型 | P05/P06/P11 | 错因解释比一般评分更不稳定；P11 是主构念，P05/P06 是必要条件或相邻证据 |
| LongTutor 知识状态诊断 | 2.62/10，8 个模型 | P11/P14 | 长历史中的知识状态判断和错误归因明显弱；离线诊断，不等于真实长期学习 |
| P08 置信度校准 | 6.40/10，8 个模型 | P07/P08 | 自信程度与正确性仍有偏离；需要与单纯弃答区分 |
| ASAP 2.0 整体作文评分 | 5.45/10，7 个模型 | P12 | 主观题整体评分仍有空间，但单一作文评分不能代表全部教育评价 |
| MOOCCube 先修关系 | 3.99/10，8 个模型 | P16 | 知识结构和学习顺序推理弱；当前是单一自建协议 |
| TutorBench | 5.48/10，6 个模型 | P03/P15/P17 | 多模态辅导质量混合了理解、策略和反馈；不能直接拆成三个独立结论 |
| MMTutorBench | 6.80/10，5 个模型 | P03/P15/P17 | 多模态关键步骤辅导仍有差距；主要是数学局部任务 |
| P07 两轮自查 | 5.21/10，8 个模型 | P07/P08 | 主动复查和修正不稳定 |
| MathTutorBench Socratic | 2.80/10，8 个模型 | P15/P17 | 会解题不等于能持续引导学生 |
| MathTutorBench Scaffolding | 3.10/10；hard 2.89/10，10 个模型 | P05/P15/P17 | 脚手架选择和执行弱；P05 只作为知识必要条件，不是主要教育结论 |
| EduIllustrate | 5.67/10，6 个模型 | P04/P17 | 图文教学产物有质量信号，但单一来源、协议和判分需要审计 |

这些结果来自仓库的 [Benchmark Portfolio Review](../../reports/atomic_ability_rebenchmark_v7_R28_snapshot_20261103/12_benchmark_portfolio_review.md)。Frontier 固定面板的 4,919 个抽样项中，27.8% 全员失败、67.3% 有对有错、4.8% 全员通过；相关教育子项包括 LongTutor diagnosis 35/60/5、MathTutorBench Socratic 35/60/5、Scaffolding 35/60/5、MOOCCube 35/60/5、P07 35/60/5、SAS-Bench 88/150/12。该面板仍受固定模型、judge/protocol 和可用模型面差异影响，因此这些是候选短板信号，不是能力定论。[Frontier validation](../../reports/frontier_selection_v1/validation_report.md)

仓库中已经相对成熟、适合作为背景或控制的结果包括：MathTutorBench Problem Solving 9.67、Mistake Correction 8.99、IFEval 9.04、C-EVAL 8.93、MathVista 8.52、Education Boundary 8.92、Age Values A 8.27/B 8.91。它们不能支持“模型不会解题”或“模型在所有教育安全场景都不行”的泛化结论。

## 3. P01–P21 逐项证据判断

| P | 仓库当前证据 | 近两年外部证据 | 当前判断 | 适合继续验证的教育场景与测量形态 |
|---|---|---|---|---|
| **P01 指令与约束遵循** | IFEval 9.04；frontier 6/89/5。 | 教师配置工作流研究显示模型会跳过教师要求的流程，但那同时涉及 P15/P17/P09，不能用 IFEval 单独解释。 | **D**。基础指令遵循总体成熟；教育场景中的流程约束仍可作为其他 case 的条件。 | 教师目的/流程保持；通常 Turn 或 Session，不单独做 P01 主集。 |
| **P02 长上下文与证据定位** | LongTutor evidence：信息抽取 9.54、跨 session 推理 6.62、幻觉检查 7.50；Mistake Location 7.71。 | LongTutor 2026 用真实学习日志区分证据获取、知识状态诊断和教学动作；EduMARS 也包含噪声手写、混排图和多步作业。 | **B**。长材料中的跨记录整合和“历史中没有该证据”仍有信号，但简单抽取已较成熟。 | 跨页作业、长历史证据引用、反事实/不存在证据；Turn 或需要动作后取证的 Session。 |
| **P03 多模态理解** | MathVista 8.52、K12Vista science/geo 6.60、TutorBench/MMTutorBench 含多模态辅导但构念混合。 | EDU-CIRCUIT-HW 2026 在 1,334 份真实电路手写作业上报告多个前沿模型较高的识别错误；MMTutorBench 2026 发现 OCR pipeline 会降低辅导质量。 | **A/B**。真实手写和复合图文有直接失败信号，但需要把识别、诊断和评分拆开。 | 学生原作证据还原、图文/公式理解；通常 Turn，必要时接后续诊断。 |
| **P04 多模态生成** | EduIllustrate 5.67，单一教育来源；时序/交互产物在 mapping 中是 coverage gap。 | EduIllustrate 2026 发现文字正确时图仍可能违反几何/物理条件；PresentBench/SlidesGen-Bench 显示 slide 的内容正确、来源忠实和布局仍是瓶颈；InteractScience 2025/2026 显示控件可运行不等于科学语义正确。 | **B**。有明确产物失败案例，但当前仓库直接覆盖薄，不能把审美或代码故障当教育失败。 | 图文一致、交互科学演示、跨页教学产物；Turn + 渲染/运行验收，只有反馈修订时才 Session。 |
| **P05 知识调用与掌握** | MMLU-Pro 8.49、C-EVAL 8.93、MathTutorBench Problem Solving 9.67；Pedagogy CDPK 8.46。 | MathTutorBench 明确显示解题能力不等于教学能力；LessonPlanLM 的知识增强改善结构和准确性。 | **D（基础知识）/B（教育知识落地）**。不应再用“数学不会”作为 Last Exam 主问题；知识错误仍可作为其他教育 case 的必要条件。 | 对学生错误的学科解释、教材 grounding；作为控制或组合能力，不单独做一般知识题。 |
| **P06 推理与生成** | Problem Solving 9.67；EduBench reasoning rigor 8.43；Mistake Correction 8.99。 | 近期反馈研究显示模型可能把有效但非最优步骤、或未完成目标的流畅证明当成正确；这更接近 P11/P12。 | **D/B**。一般解题不优先；教育推理的“是否完整、是否针对学生”仍值得作为组合 case。 | 错因解释、教学材料逻辑和有效/次优解区分；Turn 或 Session。 |
| **P07 自我校验与修正** | P07 selfcheck 5.21；与 P08 calibration 组合信号。 | 教育材料生成和交互演示研究都显示生成后需要检查；SafeTutors 报告多轮中会放弃脚手架或强化误解。 | **A**。有直接跨模型信号，但要区分“发现自己事实错误”和“发现教学策略没有奏效”。 | 评分复核、材料渲染后复查、学生反馈后的修订；Turn 或 Session。 |
| **P08 置信度校准与弃答** | calibration 6.40；abstention 8.93。 | 手写批改和复杂教案评价研究均支持“知道何时转人工/保留不确定性”比一律作答更重要。 | **B**。校准是候选短板，能力性弃答本身目前较成熟。 | 图像不可读、证据不足、难度预测和评分不确定性；Turn 或短 Session。 |
| **P09 工具使用与长程智能体执行** | v7 当前 coverage gap，无正式计分 cell。 | EduAgentBench/TeachArena 把 situated tutoring、Canvas/LMS 工作流作为独立任务；EduClaw-Bench 使用 30 天模拟学习环境。 | **C/B**。有外部方向性证据，但仓库没有稳定直接测量；不能用普通多轮对话分数替代。 | 工具调用、材料生成/运行/修改、LMS 流程；只有任务本身需要工具链时采用 Session/Episode。 |
| **P10 通用安全与合规** | DiagSafe 当前无可供分 full 结果；教育安全的 P18–P20 另行计分。 | SafeTutors 的 pedagogical failure 不等同通用安全；应区分教育角色、年龄和风险处置。 | **C（本项目教育主线）**。除非 case 真实需要通用安全边界，否则不作为 Edu Last Exam 教学短板。 | 作为必要的安全控制，不把 P10 与 P18–P20 混合。 |
| **P11 错误诊断** | SAS ECS 5.06；LongTutor diagnosis 2.62；Mistake Location 7.71。 | EduMARS、BEA 2025、MathEDU、MMTutorBench 和 LongTutor 都支持“发现有错不等于找对位置/错因”。 | **A**。当前最强候选之一；必须区分正误判定、错误位置和错因归因三个 facet。 | 学生作业首错、过程和错因；长历史知识状态；通常 Turn，必要时 Session。 |
| **P12 主观题评价能力** | ASAP holistic 5.45；SAS holistic 8.30；judge 类任务 5.10–5.29，judge 证据需谨慎。 | 2025 AIME-Con 和 2026 图像批改研究显示显式 rubric 特征较稳，高推断理由、等价解和公平性更弱；CODE-PLAN 也发现高推断教学连贯性不稳定。 | **A/B**。评分仍值得做，但不能把所有评分一致性都归因模型，需专家复核和可接受分数范围。 | 作文/主观题/图像 rubric 评价、评分复核和 rubric 生成；Turn 为主，修订时 Session。 |
| **P13 命题与作业设计** | EduBench QG 表达/知识指标约 8.24/9.25，但测评效度、难度和区分度 coverage gap。 | 2026 课堂研究中 LLM 难度标签与真实学生难度 ρ≈.06；2025 实地研究表明经过生成—审查—修订—筛选后，AI 题目可以达到可用难度和区分度。 | **A/B**。一次性命题的难度/目标对齐值得验证，但不能宣称 AI 不会出题。 | 题目有效性、诊断性干扰项、难度校准、目标保持；Turn 或“生成—审查—修订”Session。 |
| **P14 学习者画像建模** | LongTutor diagnosis 主映射 P14，2.62；EduBench 个性化适配 6.67；误概念/参与/支持需求 facet 仍有空白。 | LongTutor、EduAgentBench、真实 AI tutoring 行为研究都支持学生状态建模仍不稳定；但 StudentBench 也显示在 GRE 受控条件下学习增益可接近人类。 | **A/B**。历史状态和误概念判断是优先候选，但不能直接等同真实学习增益。 | 多次作业/对话的状态判断；Turn、Session 或 Episode 由问题是否需要持续状态决定。 |
| **P15 个性化教学策略选择** | Socratic 2.80；Scaffolding 3.10/hard 2.89；TutorBench 5.48；Pedagogy knowledge selection 8.46。 | MathTutorBench、MRBench、TutorMoments、TutorCaseBench、SafeTutors 和 EduWild 都显示策略执行/支架选择比一般回答更弱；模型会过早泄露答案或不能根据学生困难改变策略。 | **A**。策略知识选择和真实策略执行需要分开，当前最有教育意义的候选之一。 | 苏格拉底提问、支架增减、挑战行为、教师目的保持；Session 常有价值，但不是必需。 |
| **P16 学习路径规划（知识结构层）** | MOOCCube prerequisite 3.99，8 个模型；当前是单一协议。 | 长周期学习环境和课程规划工作支持路径规划是独立问题，但尚无足够跨协议结果。 | **B**。信号明确但来源单一；先做知识结构和先修关系，不把它直接扩成个性化长期学习效果。 | 先修选择、学习顺序、路径修订；通常 Turn，只有任务包含后续进度才 Session/Episode。 |
| **P17 适配性解释与反馈生成** | TutorBench/MMTutorBench 5.48/6.80；Socratic/Scaffolding 低；EduBench 内容生成指标较高但代理性强。 | BEA 2025、MathEDU、MRBench、LessonPlanLM、PresentBench 和交互课程研究都显示反馈需要针对学生证据、目标和材料，而非只追求流畅或长度。 | **A/B**。内容性反馈、语气支持和教学产物要拆开，不用一个总分覆盖。 | 针对首错反馈、教案/练习/PPT、学生反馈后的修订；Turn 或 Session。 |
| **P18 教育场景行为边界** | Education Boundary 8.92，6 个模型；当前总体较成熟。 | SafeTutors、EduWild 和 TutorCaseBench 提供角色/边界相关情境，但与 P15/P17 交叉明显。 | **D/B**。作为教育安全控制和必要条件保留，不是当前教育能力主短板。 | 角色、权力和诱导边界；配对控制或独立安全 track。 |
| **P19 学生潜在风险识别与应对** | Student Risk v2 7.09，6 个模型；暂定口径。 | SafeTutors 以 11 类 harm/48 个 subrisk 研究多轮 pedagogical failures；不能把模拟风险行为直接当真实伤害。 | **B**。有价值但属于教育安全支线，且当前主测仍是 provisional。 | 风险识别与相称应对；需要专门安全协议，不与普通教学短板混分。 |
| **P20 内容适龄与育人导向** | Age Values A 8.27、B 8.91，6 个模型。 | “LLMs are Biased Teachers”等工作显示身份和价值提示会改变教育解释，但不等同于当前内容适龄失败。 | **D/B**。当前仓库结果偏成熟；作为安全/内容控制保留。 | 适龄、价值导向和合法请求不误拒；不作为第一批 Last Exam 主线。 |
| **P21 公平对待学生** | 当前无正式计分 cell；EduEquity 仅探索性。 | 2025–2026 受控研究发现人口线索会影响评分、反馈和解释；但必须区分合理适配、人工 gold 偏差与不当差异。 | **B/C**。教育意义高，正式可测性和金标仍需建立；不从观察性群体差异直接下结论。 | 配对身份反事实，贯穿评分、反馈和策略选择；先做控制/审计。 |

## 4. 按教育场景汇总

原来的教育场景分类仍然是组织 benchmark 的主轴。P 映射只是帮助解释“为什么这个场景可能失败”。

| 教育场景 | 主要候选 P | 当前证据 | 初步判断 | 合适的第一种测量 |
|---|---|---|---|---|
| **学生作业理解、评价与反馈** | P02/P03/P07/P08/P11/P12/P17 | HG-Bench、EDU-CIRCUIT-HW、EduMARS、SAS-Bench、ASAP、图像 rubric 研究、MathEDU | **优先复核**。证据最容易定位到学生实际工作和教育后果；需分离识别、诊断、评分和反馈。 | Turn；必要时加入评分复核或反馈修订 Session。 |
| **学生状态诊断与适应性教学** | P02/P11/P14/P15/P17 | LongTutor、MathTutorBench、MRBench、TutorMoments、TutorCaseBench、EduWild、TASD、SafeTutors | **优先复核**。当前仓库弱项最集中；长周期只用于需要持续状态/后果的子问题。 | Turn/Session；延迟保持才用 Episode。 |
| **高质量教育内容与教学产物** | P03/P04/P05/P06/P07/P13/P15/P17 | EduIllustrate、InteractScience、PresentBench、SlidesGen-Bench、LessonPlanLM、LessonBench、CODE-PLAN | **候选补强**。文字流畅和结构完整已经成熟，剩余问题集中在 grounding、目标闭环、跨模态一致和运行验证。 | Turn + 运行/渲染验收；反馈修订时 Session。 |
| **命题、测评与学习路径** | P05/P06/P12/P13/P16 | MOOCCube、难度预测课堂研究、ENEM 难度研究、AI 题目实地研究 | **优先补强**。题目表达和知识正确不等于测评效度；必须保留 AI 经过审查后成功的反证。 | Turn；生成—审查—修订时 Session。 |
| **教师意图、流程与工具交付** | P01/P07/P09/P15/P17 | EduWild、Will It Teach as Intended、EduAgentBench/TeachArena、InteractScience | **候选补强**。失败可能来自 prompt、工具、环境或教学策略，必须做裸模型/正常 harness/工具执行对照。 | Session；只有真实跨任务状态和失败恢复才 Episode。 |
| **教育安全、公平与可信交付** | P08/P10/P18/P19/P20/P21 | Education Boundary、Student Risk、Age Values、EduEquity、人口标签反事实研究 | **独立支线/横向控制**。不应把安全、公平、适龄和普通教学能力平均成一个总分。 | 配对 Turn；风险处置或交接流程可用 Session。 |

## 5. 当前可以确认、但仍不能过度宣称的结论

### 5.1 目前最有把握的疑似短板

1. **错误诊断比普通解题更不稳定**：模型能解题，不代表能判断学生为什么错、错在何处、哪些步骤仍然有效。仓库的 SAS ECS、LongTutor diagnosis、MathTutorBench mistake location/feedback 和外部 EduMARS/MathEDU 相互支持这一方向。
2. **适应性教学策略比知识回答更不稳定**：Socratic、scaffolding、TutorBench、MRBench、TutorMoments 和 LongTutor teaching 都指向“会回答”与“会按学生状态教学”之间的差距。
3. **主动复查和校准仍值得单独测**：P07/P08 结果显示，模型输出看起来完整并不保证它能发现自己的错误或正确表达不确定性。
4. **教育产物的剩余问题是验证和一致性，不是能否生成一份像教案的文本**：图示、幻灯和交互产物要检查学科语义、目标对齐、跨页/跨状态一致和实际运行。
5. **命题难度和测评效度是候选短板，但必须保留成功反例**：模型一次性自报难度可能不可靠；经过 grounding、人工/模型审查、修订和筛选后，AI 题目可以达到可用的难度与区分度。

### 5.2 目前不能直接下的结论

- 不能说“AI 不会教”或“所有 Agent 都无法长期辅导”；StudentBench 等受控研究给出了学习增益接近人类的反例。
- 不能把 LongTutor 的离线历史诊断称为真实纵向学习效果。
- 不能把单篇论文、单一模型、单一 judge 或单个失败案例写成多数当前 Agent 的共同失败。
- 不能把长周期、学生状态维护、工具执行强加给所有 case。
- 不能把 P05/P06 的一般知识/解题分数当作教育短板，也不能用新造的原子能力替代仓库 P01–P21。

## 6. 下一步讨论前的候选顺序

在进入数据集建设前，建议先讨论以下四组是否认可：

1. **学生作业的忠实理解 → 错误诊断 → 评分/反馈**：这是最容易形成可追溯金标的主线；
2. **学生状态诊断与适应性教学**：确认哪些子问题需要 Session/Episode，哪些 Turn 已足够；
3. **经过验证的教案、PPT、图示和交互教学产物**：确认要测的是 grounding、一致性和执行，而不是一般生成质量；
4. **命题效度、难度校准与学习路径**：确认是否先做题目审查，还是等有学生实测数据后再进入核心。

公平性、安全和适龄内容先作为横向控制或独立支线；P09 工具与长程执行先保留为覆盖缺口，除非后续决定把真实工具工作流纳入范围。

在这四组的范围、证据等级和 P 映射得到确认前，不继续扩充题目，也不把当前 34 个 challenge_v2 任务宣布为正式数据集。challenge_v2 目前仍是 21 个方向的合成候选：作者离线检查已完成，但人工审核、模型判分、图像和交互执行仍不完整，详见 [challenge_v2 README](../../data/edu_last_exam_pilot_v1/challenge_v2/README.md)。

## 7. 主要来源

### 仓库证据

- [v7 原子能力映射](../atomic_ability_mapping_v7_2026-11-02.md)
- [Benchmark Portfolio Review](../../reports/atomic_ability_rebenchmark_v7_R28_snapshot_20261103/12_benchmark_portfolio_review.md)
- [Frontier selection validation](../../reports/frontier_selection_v1/validation_report.md)
- [challenge_v2 README](../../data/edu_last_exam_pilot_v1/challenge_v2/README.md)
- [2026 前沿模型教育失败案例清单](../../reports/research/education-llm-frontier-failure-cases-2026-11-06.html)
- [近两年证据与方案重审](../../reports/research/edu-last-exam-two-year-reassessment-2026-11-07.html)

### 近两年外部研究

- [MathTutorBench, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.11/)
- [MRBench / Unifying AI Tutor Evaluation, NAACL 2025](https://aclanthology.org/2025.naacl-long.57/)
- [LongTutor, ACL 2026](https://aclanthology.org/2026.acl-long.1371/)
- [EduMARS, Findings ACL 2026](https://aclanthology.org/2026.findings-acl.466/)
- [MMTutorBench, ACL 2026](https://aclanthology.org/2026.acl-long.1068/)
- [Confirming Correct, Missing the Rest, BEA 2026](https://aclanthology.org/2026.bea-1.56/)
- [EduAgentBench / TeachArena](https://arxiv.org/abs/2605.14322)
- [SafeTutors](https://arxiv.org/abs/2603.17373)
- [TutorCaseBench](https://arxiv.org/abs/2610.30828)
- [EduIllustrate](https://arxiv.org/abs/2604.05005)
- [InteractScience](https://arxiv.org/abs/2510.09724)
- [PresentBench](https://arxiv.org/abs/2603.07244)
- [SlidesGen-Bench](https://aclanthology.org/2026.emnlp-main.1482/)
- [LessonBench-V1](https://arxiv.org/abs/2607.13041)
- [LessonPlanLM](https://www.nature.com/articles/s41599-025-06004-2)
- [CODE-PLAN](https://doi.org/10.1016/j.caeai.2025.100538)
- [LLM-generated MCQ difficulty limits](https://arxiv.org/abs/2609.27063)
- [AI-generated exams field study](https://arxiv.org/abs/2508.08314)
- [EduFair-Bench](https://arxiv.org/abs/2609.12949)
- [LLMs are Biased Teachers](https://aclanthology.org/2025.findings-naacl.314/)

