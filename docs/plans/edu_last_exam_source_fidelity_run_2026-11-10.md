# 37方向原始任务保真核验与GLM复测

用户决定：重新核对全部37方向的原论文和仓库；有原题则使用原题并保留原任务与评分条件；没有原题，先弄清研究中具体容易失败的条件，再据此出题。完成后用GLM-5.3-Flash试跑。沿用每模型并发4及后台运行方式，不覆盖上一轮82版本的原题、回答、初评或Codex复核。

本轮工作目录为 `data/edu_last_exam_source_fidelity_v1/`、`private/edu_last_exam_source_fidelity_v1/`、`scripts/source_fidelity/`，完整[协议](../../data/edu_last_exam_source_fidelity_v1/protocol.md)约束逐项交付。当前计划文件不是完成证明；实际状态由37份方向核验、导出manifest和独立run的持久标记确定。

## 实现与核验顺序

1. 直接查看原作者论文、公开数据及评分程序，固定版本/commit和文件哈希。不能再把本地旧自编题的“来源复用”叫作外部论文原题。
2. 原题保留完整输入、原prompt、原轮次/追问、原允许工具、原输出和评分逻辑。按来源顺序及研究失败条件选少量实例，不能看当前GLM回答再选题；原生指标保留，不能一律二分化。
3. 无公开完整原题的方向记录检索过程；有明确研究失败条件时才自建，并逐条对应条件、材料和评分。原论文数据/学生角色/环境确实缺失则明示缺口，不将更简单任务冒充复现。
4. 原金标可疑时保留原分与作者复核疑点，不静默修正。原judge身份或学生模拟模型不可用时保留待测/待评，不悄悄替换成GLM并报告原指标。
5. 所有付费调用前完成来源、模板、素材和适配代码的离线验收。任意生成代码仅在无凭证、无外网、隔离主机个人文件的环境执行，保留真实产物与原测试输出。
6. 独立冻结源快照，GLM-5.3-Flash并发4、后台预测后原生评分。保留请求、原回包、真实轨迹、source/request/scoring身份、汇总、完成标记及退出码。缺原评分条件不算模型答错。

## 交付入口

- 来源核验：`data/edu_last_exam_source_fidelity_v1/directions/01.json`至`37.json`。
- 题包、模型可见导出与manifest：`private/edu_last_exam_source_fidelity_v1/`。
- 可阅读来源与任务报告：[source_audit.html](../../reports/source_fidelity_v1/source_audit.html)（由builder生成）。
- 离线构建：`/home/likefallwind/miniconda3/bin/python scripts/build/build_edu_last_exam_source_fidelity.py`及`--check`；该环境含原指标需要的`sacrebleu`等依赖。
- 运行入口：`scripts/experiments/launch_edu_last_exam_source_fidelity.py`，输出到独立`reports/eval/edu_last_exam_source_fidelity_v1/_exploratory/`；凭证仅继承环境变量。

解释结果时区分：原任务子集、按条件自建、原评分待补、原环境不可运行。37项核验完成不等于37项实测完成；完成试跑也不等于原论文复现成功、真实课堂效果成立或benchmark已冻结。

## 本轮启动记录

2026-11-10 20:17（Asia/Shanghai）已启动 `20261110_source_fidelity_glm53flash`。37份来源审查、81个任务单元已通过离线导出校验；63项为外部原任务/公开示例，18项为按机制自建或明确标注的本地历史题。77个单元具备预测条件，覆盖29方向；4个归档单元缺原输入/学生角色而禁止发起调用，另5个方向保留来源/环境缺口、暂无可执行任务。原视频及5个对照探针已纳入本次快照。

后台GLM-5.3-Flash并发4，监督进程PID378307、工作进程PID378309。启动检查已见首批6个有效回包，评分尚未开始；这只是启动时的观测，不是最终结果。当前状态以[运行summary](../../reports/eval/edu_last_exam_source_fidelity_v1/_exploratory/20261110_source_fidelity_glm53flash/GLM-5.3-Flash/summary.json)和[运行报告](../../reports/eval/edu_last_exam_source_fidelity_v1/_exploratory/20261110_source_fidelity_glm53flash/GLM-5.3-Flash/report.html)为准，完成还须检查对应control的finished和退出码。

本次输入与代码快照含14,324个文件；请求传输模块也纳入恢复身份校验。离线回归32项及3个子测试通过，Manim真实PNG、原PFT/VQT浏览器链路与真实PDF链路均有固定fixture产物。fixture验证不属于模型成绩；Manim/Playwright外部只读环境在异机恢复时仍须重验。缺原评分者的项目保留待评，不合并为总正确率。

## 2026-11-11直接复核与补跑

原run于2026-11-10 21:14（Asia/Shanghai）退出0，72有效、4原输入/角色缺失、5执行或接口未完成。用户随后授权未完成补跑、已完成直接由Codex判断。新增[复核协议](../../data/edu_last_exam_source_fidelity_v1/codex_review_protocol_2026-11-11.md)、分组记录和[生成报告](../../reports/source_fidelity_v1/codex_review_20261111/review.html)，原run与原判分不覆盖。原81条状态/72份有效回答已全量复核；报告以SHA绑定每次具体回答。

补跑`20261111_source_fidelity_retry01`处理19-001、23三题、28-001（工作PID387105、初始并发4）。23适配后暴露换行stop作用于推理流的接口兼容问题；保留失败尝试`retry01`与`retry23b`，以`retry23c`进行无损消息角色拆分并在可见正文执行原stop，三题全部完成且Codex判通过。后续23运行并发2，与19/28合计不超过4；不再调用付费judge。19保留成功阶段缓存，原参数重试截断阶段；28保留40轮及完整原材料，以显式本地工具协议执行。

截至2026-11-11 09:11，最新已审75份有效结果：34通过、9未通过、12争议、16描述性、4配对混合；4未测，2产物任务还在后台。此为当时进度，不能替代后续summary/完成标记。2项后续完成后追加独立复核并刷新报告，不删除旧尝试。作者直接判定不冒充原指定judge或独立教师审核。

## 2026-11-11争议项讨论记录

已记录[剩余10条争议的复核依据与处理建议](../evidence/edu_last_exam_source_fidelity_dispute_audit_2026-11-11.md)。用户确认：这批争议大部分来自题目、参考答案或评分依据问题，不能直接视为模型能力失败。10条对应8道不同题，其中6条参考答案／标签有误或依据不足，2条图谱匹配不能等同唯一教学标准，另2条输入与模型回答同时有问题。六阶群两条已先行改判，不在这10条之内。

本次将讨论结论和建议存档，尚未将上述建议批量回写复核标签。原生分、作者复核与后续修订须分别保留；不将争议子集推论为整轮失败均由出题错误导致。泰勒题须区分计划落实与数学准确性，不能因来源计划也错而豁免回答中的事实错误。
