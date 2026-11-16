# 方向31：学生程序多错误诊断与真实验证

本批按37方向机制蓝图M31/MG-31-A制作两类原创合成作业：传感器读数的截尾均值、含缺测的连续降雨记录。各含多错误、单错误、正确等价实现三个依赖条件，共两个材料、六个条件。GLM-5.3-Flash未参与题目生成。独立教师审核pending，canonical=false，frozen=false。

历史简单案例GLM曾通过，用作成功参考。新材料在调用API前固定，不根据本次输出改题。历史错例可参考，不要求每道题都有历史失败。

工作区提供list/read/write/run/submit。run复用方向31的受限AST解释器，实际读取当前student.py并执行公开测试，返回代码哈希和结果；不执行任意Python。提交时检查实际运行过提交版本；私有合同探针仅用于运行后评分，不返回模型。正确控制要求代码原样保留。诊断、最终功能、实际验证和反馈分别记录。

本轮run只接受预先固定的公开示例，不提供任意自定义测试输入；模型对其他反例的说明属于静态推演，不能称为实际执行。静态审查已足以识别本批两个根因，因此本批不单独证明模型在首修后遇到新代码状态时的持续诊断能力。

公开测试是示例，完整合同已明示重复观测与缺测语义。私有探针覆盖长度0–5的短序列与预先固定的边界/长序列：统计题3910例，连续记录题368例。它们验证本批有限域，不穷尽所有长度20输入。受限解释器已对可信作者程序与CPython逐例对照；模型输出始终只进入受限解释器。

离线命令：

```bash
PYTHONPATH=/tmp/edu_last_exam_testdeps:. python scripts/build/build_edu_last_exam_v2_pilot.py --protocol data/edu_last_exam_v2_31_debug/protocol.json
PYTHONPATH=/tmp/edu_last_exam_testdeps:. python scripts/build/build_edu_last_exam_v2_pilot.py --protocol data/edu_last_exam_v2_31_debug/protocol.json --validate-only
PYTHONPATH=/tmp/edu_last_exam_testdeps:. python -m pytest -q tests/test_edu_last_exam_v2_31_debug.py
```

运行选择与完整重复策略见`data/edu_last_exam_v2_31_debug/selection.json`。实际运行使用coding plan原有endpoint，不设token上限；新隔离目录保留source snapshot、请求身份、SSE完成状态、返回模型、退出码、summary和完成标记。不调用同模型judge；确定性执行与作者关联语义复核分开，不称独立教师验证。

## 实际结果

2026-11-13完成两轮全量GLM-5.3-Flash探索运行。首轮并发3遇到429，归档失败状态后降到2，按原请求身份恢复接口失败调用；第二轮完整重复全部六条件。两轮请求身份和题包哈希一致，所有返回调用均有stop/DONE及返回模型核验，两个进程退出码均为0。

- 12条最终代码轨迹全部通过各自预设功能探针；4条多错误目标轨迹均正确识别、解释并修复两个根因。两轮正确控制均原样保留。
- 首轮`ELE-V2-31-001__v1`附加反馈误称final/total与Python内建名称冲突；反馈事实项未通过，完整量尺为5通过、1反馈问题。重复轮6条件均通过作者复核，该附加问题未复现。
- 首轮一个反例字段有可辨的嵌套格式瑕疵；两轮均有可恢复的非JSON动作。分别记录，不将这些问题称为多错误遮蔽机制复现。
- 本批未建立AI难题证据。作者复核不是独立教师审核；状态仍为候选、未冻结。

可读[总复盘](../../reports/edu_last_exam_v2_31_debug/overview.html)、[第一轮报告](../../reports/edu_last_exam_v2_31_debug/20261113_glm53flash_run01/result_analysis.html)和[重复轮报告](../../reports/edu_last_exam_v2_31_debug/20261113_glm53flash_run02/result_analysis.html)。作者判断及引文身份保存在`reviews/`，原始流与冻结代码在被Git忽略的`reports/eval/edu_last_exam_v2_31_debug/`中。

报告可由`python scripts/experiments/analyze_edu_last_exam_v2_31_debug.py --run <原始运行目录> --output <报告目录> --reviews <作者复核JSON>`重新生成；使用`--compare <第一轮报告目录> <重复轮报告目录> --output reports/edu_last_exam_v2_31_debug`生成总复盘。
