# 原题保真轮争议复核：题目与评分依据问题

日期：2026-11-11。对象：GLM-5.3-Flash 原题保真轮中，六阶群题修正后剩余的 10 条 `disputed` 记录。

证据状态：作者关联离线检查，结合一次模型试跑的具体回答；不是独立教师审核，也不是冻结 benchmark 结论。

## 本次讨论确认的结论

用户确认并要求记录：**这批争议项的大部分问题出在题目、参考答案或评分依据上，不能直接当成模型能力失败。** “来源于论文或知名 benchmark”只说明出处，不保证题目、参考答案和评分协议逐项有效。

10 条是测试记录数，实际对应 8 道不同题：语音题、肺癌题分别重复用于自检与置信度测试，不能当成 4 道独立内容题。分类如下：

- **6 条参考答案或标签有误、依据不足**：两条语音记录、两条肺癌记录、两道 Python 标签题。这里不意味着 6 条都属于答案字母误标；其中一条是错误标签依赖未固定的修复路径。
- **2 条把特定参考图谱关系当作唯一教学标准**：图谱不匹配成立，但不足以认定教学顺序错误。
- **2 条输入材料与模型回答同时存在问题**：个体背景缺失但模型无依据归因；原教案诱导错误结论且模型照样讲错。

这只是对上述争议子集的结论，不能外推为本轮全部失败均由题目问题造成，更不是 C-Eval 或其他来源的总体错误率。此前将部分“与原答案不一致”过早解释为“模型答错”，反映了本地复核不足。

## 逐项依据与处理建议

以下为本次复核结论和建议，尚未批量回写机器可读复核标签；原生分数与原始材料保留。选择题答案正确也不自动表示其附带解释全部正确，或整个自检、校准能力已通过验证。

| 任务记录 | 观察到的问题 | 复核建议 |
| --- | --- | --- |
| `ELE-SF-25-001`、`ELE-SF-26-001` | C-Eval 音素题 `[p][p‘][b][m]` 的原答案为 A“清浊”，模型选 B“发音方法”。清浊不能涵盖送气与否、塞音与鼻音的区别；按题目采用的现代汉语教学术语，发音方法涵盖这些方面。 | 按选择题答案判 B 正确；撤销据原 A 标签形成的“自检仍错／高置信错误”解释。 |
| `ELE-SF-25-003`、`ELE-SF-26-003` | 题干问早期肺门、纵隔多发淋巴结转移，原答案 D“腺癌”，模型选 C“小细胞肺癌”。医学文献支持模型所选类型的这些特征。 | 按选择题答案判 C 正确；模型附带医学解释另评，不能由答案正确推出解释全部无误。 |
| `ELE-SF-31-002` | `a,b=int(input().split(""))` 可被 Python 解析，执行先触发 `ValueError`；修正空分隔符后，列表交给 `int` 会触发 `TypeError`。模型识别了二者，原标签额外要求 `SyntaxError`。 | 原参考多出的 `SyntaxError` 无代码依据，不应据此判模型漏检。 |
| `ELE-SF-31-003` | 原无参函数定义与无参调用匹配。模型指出局部变量先读后赋值及缺少输出。原标签额外要求 `TypeError`，但先修作用域、再补打印即可完成，不必经过该异常。 | 额外标签依赖特定修复路径；原协议未固定该路径，不能将其作为唯一必答标签。 |
| `ELE-SF-24-002` | 顺序匹配 4/5 条图谱边，未满足“输入输出→软件”。题目给出的概念和定义不足以证明这是必须遵守的先修关系。 | 保留图谱匹配结果，不算已证实的教学失败。 |
| `ELE-SF-24-003` | 顺序匹配 3/5 条图谱边，未满足“服务器→和校验”“服务器→进程间通信”；部分概念缺定义，关系的教育必要性未获证实。 | 保留图谱匹配结果，不算已证实的教学失败；核查边的语义、方向和课程上下文。 |
| `ELE-SF-11-102` | 原答案 C“等学生玩完”，模型选 D“视觉规则与时间表”。来源评分材料中影响选择的完美主义、未完成活动被打断时情绪失控等背景没有给模型。模型又将“预期不清、时间理解困难”断言为反抗根因。 | 题面不足以唯一确定 C 优于 D；同时将模型的无依据根因归因记录为可观察缺陷。不能强迫在缺信息时认定 C 或 D 唯一正确。 |
| `ELE-SF-27-001` | 输出无条件宣称“More terms → smaller error”；原输入计划也要求建立“项数越多近似越好”的预期。 | 分开记录“计划落实通过、数学准确性失败”，注明来源诱导。整体通过线尚未确定，不冒充原 benchmark 官方失败。 |

两道排序任务是由 MOOCCube 图谱构建的本地历史题，并非论文直接提供的原题。**隐藏先修边本身不是错误**，推断任务本就需要隐藏待预测关系；问题是参考边能否代表必须遵守的教育关系。把边直接给模型会将任务改成拓扑排序，不能作为无说明的修补。

泰勒题的数学事实可以直接核验：取 `f(x)=1+x-3x²`，在 `a=0` 展开、`x=1` 求值，真实值为 −1；一项近似为 1，绝对误差 2；加到两项近似为 2，误差反增至 3。这是多项式，不涉及收敛半径之外的特殊情况。需要确定的是整体评分口径，而非该无条件断言的真假。建议准确性照常扣分、保留输入诱导标签；若要判断普通教案生成表现，应修正原计划后再测。

## 对难度结论与后续审核的约束

1. 将模型回答与原答案不一致当作**待核查信号**，先检查题面充分性、参考有效性和评分合同，再归为模型错误。
2. 专门筛选模型错题可能同时集中选入错误参考或不合理评分项；这是筛选风险，不能把这类假失败作为高难度证据。
3. 来源问题与模型问题可以同时存在。既不因题目有问题而豁免可见的事实错误，也不把参考标准缺陷全部归给模型。
4. 保留原生指标、作者复核及修订理由；今后改分须有逐条记录并通过 builder 刷新报告，不手改生成报告。
5. 语音／医学答案核验与 Python 执行事实无需用户凭偏好裁定；学生个体信息不足不能靠主观投票补齐。泰勒题的整体阈值属于仍需明确的评分政策。
6. 有连续指标但无原通过线的项目不在本次 10 条争议分母中，不为给出总正确率而事后任意二分。

## 证据入口与快照

- [当前逐份复核记录](../../reports/source_fidelity_v1/codex_review_20261111/latest_case_reviews.jsonl)、[汇总](../../reports/source_fidelity_v1/codex_review_20261111/summary.json)、[可读报告](../../reports/source_fidelity_v1/codex_review_20261111/review.html)。本次记录所依据的汇总生成时间为 `2026-11-11T02:37:36.300576+00:00`，81 条状态为：36 通过、9 失败、10 争议、17 描述性、4 混合、5 不可评估，无待补跑标签。该状态快照尚未应用本页提出的重新分类建议。
- 上述 `latest_case_reviews.jsonl` 快照 SHA-256：`59dc13b933a357e640211ed50b42f68f07e934bf8bd50f902fbf9d3343311630`。每条复核另含其实际回答的 SHA-256；后续报告再生成时以该日期快照区分本页计数。
- [完整审核题册](../../reports/source_fidelity_v1/human_review_book_20261111/review_book.html)提供原题、原答案和回答。原预测与任务快照位于 [20261110 原 run](../../reports/eval/edu_last_exam_source_fidelity_v1/_exploratory/20261110_source_fidelity_glm53flash/)。
- Python 直接执行依据：[31-002](../../private/edu_last_exam_source_fidelity_v1/review_20261111/evidence_27_37/ELE-SF-31-002_execution.json)、[31-003](../../private/edu_last_exam_source_fidelity_v1/review_20261111/evidence_27_37/ELE-SF-31-003_execution.json)；[原标注规则](../../sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/pymeta/annotation/ANNOTATION_GUIDELINES.md)说明逐次修错，但未固定唯一修复路径。
- 学生过渡任务：[模型可见原 MCQ](../../sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13/tutorcase/mcq_prompt/mcq_0002_immediate_c001_s002.txt)、[另存的个体背景与评分材料](../../sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13/tutorcase/rubric_evaluation_prompt/rubric_evaluation_prompt_0002_immediate_c001_s002.txt)。
- 泰勒任务：[原计划](../../sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/lessonbench/lesson_160_0/lesson_plan.md)、[模型回答](../../reports/eval/edu_last_exam_source_fidelity_v1/_exploratory/20261110_source_fidelity_glm53flash/GLM-5.3-Flash/cases/ELE-SF-27-001/response.md)。
- 六阶群的两条记录 `ELE-SF-25-002`、`ELE-SF-26-002` 已先行由争议改为内容通过，[修订历史](../../private/edu_last_exam_source_fidelity_v1/review_20261111/revision_history/20261111_six_order_group.json)另存；它们不在本页剩余 10 条中。

来源数据、完整审核题册和原始运行包不随 Git 提交，上述 `sources/datasets/`、`human_review_book_20261111/` 与 `reports/eval/` 链接以本地快照为准。Git 中保留逐条复核记录、汇总、来源身份和构建代码。

## 本次使用的外部核验资料

- [青岛理工大学：语音的性质和基本概念](https://jw.qut.edu.cn/info/1087/1705.htm)：发音方法包含阻碍方式、声带振动及除阻气流强弱。用来核对概念，不以网页声母拼音字母替代题目的国际音标。
- [Lee 等：CT findings of small cell lung carcinoma](https://pmc.ncbi.nlm.nih.gov/articles/PMC5134877/)：对 142 例病理确诊病例的研究，讨论肺门／纵隔表现及早期血管、淋巴侵犯；结合题干，支持小细胞肺癌选项。这不是临床个案诊断。
- [日本肺癌学会 2022 指南：小细胞肺癌总论](https://www.haigan.gr.jp/publication/guideline/examination/2022/1/3/220103000000.html)：说明其增殖快及早期淋巴结、远处转移特征。
- [C-Eval 论文 §2.2](https://arxiv.org/html/2305.08322v2#S2.SS2)：题目主要收集自既有试题材料，经过处理与多轮人工核验；GPT-4 参与 dev 解析草稿生成，不能因此说题目由 AI 生成。
- [C-Eval 官方 issue #84](https://github.com/hkust-nlp/ceval/issues/84)：维护者确认过其他题目的答案错误并回复修复。这只能证明知名题库亦可能残留错误，不能证明本页几题的具体致错环节。

上述网页在 2026-11-11 对话复核时访问；本地保留的原 C-Eval 记录见 [selected_ceval_original.json](../../sources/datasets/edu_last_exam_source_fidelity_v1/group_14_26/selfcheck_calibration/selected_ceval_original.json)。
