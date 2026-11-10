# 全方向探索首轮运行记录

2026-11-10 14:22（Asia/Shanghai）启动。本文记录启动时核验，后续状态以运行目录的持久记录为准。

- 题集：37方向、38基础案例、82投递版本，全部纳入任务清单。音频2版本按接口合同保留未测，不用转写替代。
- 模型：GLM-5.3-Flash；并发4，预测阶段结束后执行同模型语义初评；无token上限。
- 离线验收：35项回归测试及3个subtest通过；22个产物正反例符合预期；参考PPT、浏览器演示通过实际渲染检查。
- 启动核验：PID 355827，预测阶段，4个实际请求在途；当时0份完整episode结果，尚未开始评分。未把活跃进程当作完成。
- tmux socket/session：`edu_full_20261110_142158_glm53flash`。
- 使用 `/usr/bin/python3`；交互shell默认Python缺少PPT依赖，启动前检查发现后已切换；失败的预检查未调用模型。

## 结果与完成证据

- [实时报告](../../reports/eval/edu_last_exam_full_coverage_v1/_exploratory/20261110_142158_glm53flash/GLM-5.3-Flash/report.html)
- [进度](../../reports/eval/edu_last_exam_full_coverage_v1/_exploratory/20261110_142158_glm53flash/GLM-5.3-Flash/progress.json)
- [日志](../../reports/eval/edu_last_exam_full_coverage_v1/_exploratory/20261110_142158_glm53flash/GLM-5.3-Flash/run.log)
- [任务manifest](../../reports/eval/edu_last_exam_full_coverage_v1/_exploratory/20261110_142158_glm53flash/GLM-5.3-Flash/run_manifest.json)
- [运行配置及保存的命令](../../eval/full_coverage_20261110_142158_glm53flash/config.json)
- [源码与输入快照哈希](../../reports/eval/edu_last_exam_full_coverage_v1/_exploratory/20261110_142158_glm53flash/source_snapshot_manifest.json)

结束后应同时检查模型输出目录中的 `summary.json`、`finished.json`、`exit_code.txt`、`process_exit_code.txt`，以及控制目录 `eval/full_coverage_20261110_142158_glm53flash/` 中的 `finished.json`、`exit_code.txt`。音频未测或其他不可用结果可能产生 `complete_with_issues`；这不等于模型答错。

运行冻结的是可复现试跑快照，题集仍是作者候选。17的预测误差与排序单列；其他方向逐项语义初评，不合成跨方向总正确率。同模型初评、独立教师复核未完成、真实学习效果等子机制未测的边界保留。
