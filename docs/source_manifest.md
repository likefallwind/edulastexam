# Source snapshot manifest

复制日期：2026-11-09  
源仓库：`/home/likefallwind/code/edubenchmark`  
目标仓库：`/home/likefallwind/code/edulastexam`

本仓库复制了与 Edu Last Exam 直接相关的方案、证据矩阵、研究报告、benchmark profile、`edu_last_exam_pilot_v1` 的数据和题目、challenge_v2 作者材料、已完成试跑的持久化结果，以及构建器和评测基础设施。`scripts/eval/` 复制的是可复用框架；其中部分适配器仍依赖源仓库未复制的外部数据集。

challenge_v2 的探索性运行目录已完整复制，包括 manifest、summary、progress、完成标记、逐题请求/响应、产物和原始 SSE。它们仍然只属于 exploratory evidence，不是正式 benchmark score；`reports/challenge_v2/` 中的复核报告也应结合这些原始记录阅读。

复制是增加操作：源仓库没有被删除、移动、重置或改写。今后如果源仓库中的方案发生变化，应在这里追加新的带日期快照或同步记录，不要静默覆盖已经用于实验的版本。

2026-11-09 的后续开发在本仓库内完成：`data/edu_last_exam_v1/selection.json` 固定了从 challenge_v2 选出的八个任务包，`private/edu_last_exam_v1/` 是构建器导出的测试候选集。它包含针对 C2-09、C2-10、C2-12、C2-16、C2-20 的窄范围修订和离线检查；这些修订不回写源仓库，也不把 v1 标记为已验证困难。

