# Edu Last Exam · challenge_v2

这是沿 2026-11-07 讨论的 21 个方向编写的一批**挑战候选**，每方向一个任务包。材料为 Codex 自行编写的合成案例，文献用于说明失败机制与设计依据，不代表论文原题复现或真实学生记录。实际模型难度尚未测量，不能把这些候选称为已验证的 Edu Last Exam 难题。

题目位于本仓库的 `private/edu_last_exam_pilot_v1/challenge_v2/`。原 12 题和原评测适配器保持独立。本批包含文本、实际图片、原始历史记录和可离线运行的交互材料。

## 文件入口

- [审阅页面](../../../private/edu_last_exam_pilot_v1/challenge_v2/review.html)：按方向浏览题面，展开参考解、出题理由和文献边界。
- [纯题目册](../../../private/edu_last_exam_pilot_v1/challenge_v2/questions.md)：题面和附件链接，不含金标。
- [完整审阅册](../../../private/edu_last_exam_pilot_v1/challenge_v2/review.md)：包含金标与评分依据。
- [作者检查报告](../../../private/edu_last_exam_pilot_v1/challenge_v2/build_report.md)：当前任务包、投递版本及离线检查数量。
- [设计方向与文献](../../../docs/plans/edu_last_exam_direction_proposal_2026-11-07.md)。

`cards.jsonl` 是题卡；`authored/*.jsonl` 是逐题维护源；`items.jsonl`、`prompts.jsonl`、审阅册和 `review_sheet.csv` 由构建脚本导出。刺激材料在 `stimuli/`，参考产物在 `reference/`，可复跑的作者检查在 `checks/`。不要手改导出文件。

## 题目与评分边界

每个任务包有完整输入、可接受答案、实质评分项及证据限制。有些方向包含独立变体；这些变体属于同一任务包，不能扩报成彼此独立的难题。静态教学快照只测该时刻的判断和生成，不能作为真实多轮学习效果证据。给定错误规则的干扰项题验证规则下的诊断可分性，不能证明真实学生都遵循这些规则。群体校准题在明确的可计算假设下检验校准与证据边界，不以猜中未知正确率作为金标。

每包满分 10 分，保留分项得分。一个评分项涉及多个独立变体时，优先按题内列明的变体份额给分；未规定份额时，对适用变体的完成比例等权平均，再按该项权重计分。确需比较版本的项目按任务包评一次，不重复叠分。跨版本一致性只比较相同实质结论；措辞差异和合理教学替代不算失败。`critical_errors` 是实质错误的审核提示，**不继承旧版任意硬门槛触发整题归零的规则**。本批尚未设定通过阈值，也未实现或校准 LLM 裁判。

题目公开必要条件和实质要求，但不以提示直接透露具体诊断。图像题要实际核验附件；产物题要交付能检查的文件。工具可用，具体工具预算和受测模型条件应在未来实测时记录，不能把文本模型看不到图片算作教育能力失败。

## 交付隔离

受测输入只能来自 `prompts.jsonl` 中相应记录的 `system_prompt`、`user_prompt` 和 `assets` 指定文件。`assets` 路径相对于本批目录。投递多个变体时使用互不共享答案的独立上下文。

**不要把整个仓库或本批目录挂载给受测 Agent**：其中包含作者草稿、金标、检查代码和参考产物。工具型执行器须建立仅含指定刺激材料的隔离工作目录。现有 `edu_last_exam_pilot` 适配器只适用于旧 12 题，不应拿它直接跑本批。独立单轮初测脚本见下文，不提供工具循环。

## GLM-5.3 单轮初测（2026-11-07 启动）

经用户授权，使用 `scripts/experiments/run_edu_last_exam_challenge_v2.py` 在后台进行文本/源码初测，并发2。首题核验成功后自动接续其余题，已成功且输入哈希一致的回答会复用。运行范围是30个独立prompt（19个任务包）；07/08的4个PNG版本标为 `unsupported_input_not_scored`，不计答错，不用图片转写代替原题。

官方 Coding OpenAI 兼容接口使用现有 `GLM_API`，请求中省略 `max_tokens`。该路由与原pilot使用的Anthropic路由分开记录。每个请求只有题面和指定刺激材料，附件全文以用户消息投递；不读取参考解。模型得到明确环境说明：无工具，需要文件时以完整代码块交付，由运行器保存。产物未执行、裁判未运行，不生成通过率，不能视为完整Agent评测。

- [实时回答页](../../../reports/eval/edu_last_exam_challenge_v2/_exploratory/GLM-5.3/20261107_01/responses.html)
- [GLM-5.3 内容复核报告](../../../reports/challenge_v2/reviews/2026-11-08/GLM-5.3_initial_review.html)
- [运行进度](../../../reports/eval/edu_last_exam_challenge_v2/_exploratory/GLM-5.3/20261107_01/progress.json)
- 完成依据：同目录 `summary.json` 与 `finished.json`；后台启动不代表完成。
- 请求快照、附件哈希、原始SSE、实际返回模型和逐题结果在同目录 `cases/`；空正文、截断、API错误与模型名不符分别记录。
- 后台日志和退出标记位于 `eval/edu_last_exam_challenge_v2_glm_20261107_01/`。

截至 2026-11-08，30 个可投递版本均已生成回答，4 个图片版本仍为未测。Codex 内容复核标出 4 个 `substantive_issue`、11 个 `minor_issue`、1 个 `ambiguous` 和14个未发现主要问题；这只是定位后续人工审查重点的标签，不是正式通过率。

## 作者核验

```bash
python scripts/build/build_edu_last_exam_challenge_items.py
python scripts/build/build_edu_last_exam_challenge_items.py --validate-only
```

检查默认需要 Python 3 与 Node；不调用模型 API。浏览器材料另用 Python Playwright 和本地 Chromium 核验：

```bash
python private/edu_last_exam_pilot_v1/challenge_v2/checks/browser_review.py --browser /path/to/chromium
```

浏览器检查会从 SVG 生成 PNG，并通过真实控件核验交互参考产物。该证据位于 `reports/challenge_v2/authoring_checks/`。构建清单记录作者源文件和附件的 SHA-256；作者数学、代码与图像核验不替代人工教育质量审查。

作者交付快照的状态：作者自检；人工审核 `pending`；模型实测 `not_run`。后续初测证据独立保存在上述运行目录，不回写作者快照。最终哪些题配得上 Edu Last Exam，仍需以输入与金标可靠、教育价值成立、当前强 Agent 实测困难为依据。
