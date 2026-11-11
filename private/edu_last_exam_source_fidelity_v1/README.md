# 原始任务与失败条件复测 v1

本批重新核对原37方向，不沿用上一轮“按大方向自编题即可覆盖”的解释。完整来源记录在 `data/edu_last_exam_source_fidelity_v1/directions/`；[生成审阅报告](../../reports/source_fidelity_v1/source_audit.html)同时展示原方向范围、本轮实际测量视图和未测部分。

## 来源身份

- `original_task`：来自外部原始任务或原作者公开示例，表示来源身份。可执行任务保留原输入、提示/对照/轮次和原生评分；公开示例缺必要输入时只归档、不执行。必要执行适配逐项记入 `fidelity.deviations`，这个标签不表示原论文全实验或所有模型都被复现。
- `mechanism_authored`：按原研究明确失败条件新编，或保留明确标注的本地历史协议；不冒称外部原题。方向卡说明两条路线的区别。
- 原数据、必要系统提示、动态学生或执行环境缺失时，保留审计或候选并明确不执行。只缺原评分者的完整任务可先预测，原分留待补齐，不用其他模型的分数冒充原分。

任务单元可能包含多次独立配对调用、真实追问或代码修复；任务数不等于API请求数，也不等于相互独立的研究样本数。数量与可预测状态以当前 `manifest.json` 和各次运行冻结manifest为准。

## 生成与运行

```bash
/home/likefallwind/miniconda3/bin/python scripts/build/build_edu_last_exam_source_fidelity.py
/home/likefallwind/miniconda3/bin/python scripts/build/build_edu_last_exam_source_fidelity.py --check
/home/likefallwind/miniconda3/bin/python -m pytest -q tests/test_edu_last_exam_source_fidelity.py tests/test_source_fidelity_group_01_13.py tests/test_source_fidelity_group_14_26.py
/home/likefallwind/miniconda3/bin/python scripts/experiments/launch_edu_last_exam_source_fidelity.py
```

预测模型仅GLM-5.3-Flash、最多4个API在途、无token上限。原本明确采用MiniMax-M3裁判的本地历史任务可沿用该原裁判；不会拿它替代论文指定的Claude/GPT/Gemini裁判或学生。凭证只继承已配置环境，不写入题包、快照或日志。

独立后台输出包含源快照、哈希、每次请求/回包、真实交互和产物、原生评分/待评分状态、summary、finished与exit code。Manim/HTML/PDF等生成代码在隔离环境执行；依赖版本和宿主环境限制记录在 `data/edu_last_exam_source_fidelity_v1/runtime_environment.json`。

Manim虚拟环境与固定Playwright/Chromium运行时依赖当前主机的只读目录；它们不等于可迁移的容器镜像。异机恢复须重新验证版本、隔离执行及原测试，不能只复制源快照就声称环境一致。

外部原始输入及嵌入原文的任务导出只留本地，不提交Git。正式benchmark冻结、独立教师审核、多模型难度证据和真实课堂学习收益均未由本次试跑完成。

## 已提交的复核证据与本地导出

Git保留来源清单、协议、构建与运行代码、逐条复核记录、执行核验和[复核汇总](../../reports/source_fidelity_v1/codex_review_20261111/review.html)。[争议项说明](../../docs/evidence/edu_last_exam_source_fidelity_dispute_audit_2026-11-11.md)记录参考答案、图谱标准及输入诱导问题；其中新建议尚未批量回写复核标签。

`authored/`、完整题面导出、`reports/eval/edu_last_exam_source_fidelity_v1/` 原始运行包，以及 `reports/source_fidelity_v1/human_review_book_*/` 完整审核题册均为本地产物。题册包含外部原题、原始素材和完整回答轨迹，遵循仓库原数据与大体积原始预测不入Git的规则。题册生成器已提交；异机生成需先恢复相应来源材料和运行包，不能仅凭Git检出声称已具备完整复现实验条件。
