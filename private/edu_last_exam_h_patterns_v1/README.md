# Edu Last Exam 错误机制候选题包

2026-11-17。六类各3道基础材料，共18个题族、57个依赖版本。全部为原创合成候选，独立教师审核待完成，模型尚未试跑，难度未测，未冻结。

- [题册（HTML）](questions.html) · [题册（Markdown）](questions.md)
- [参考答案与评分审阅册（HTML）](review.html) · [评分审阅册（Markdown）](review.md)
- [工作区初始文件索引](workspace_inputs.md)：方向14的实际可读文件；执行以当个版本的runtime为准。
- [作者复查与独立审核清单](author_review.md)
- [研究依据与设计取舍](../../docs/evidence/edu_last_exam_h_pattern_candidate_design_2026-11-17.md)
- [协议与运行边界](../../data/edu_last_exam_h_patterns_v1/README.md)

|主方向|三个基础材料|版本数|实际任务视图|
|---|---|---:|---|
|02 合法等价解与部分得分|参测人数与百分率平均；除以未知量是否丢解；平方根与绝对值|9|单轮作品复核与评分|
|12 学习状态与误概念判断|分数比较；调查取样；程序循环边界|9|短跨日记录的援助证据判断及新探查生成|
|23 苏格拉底提问实质质量|速度单位与除法；分配律与常数计算；循环范围与提前返回|12|错误位置×提问对象的2×2评价与下一句生成|
|10 流程与结束判断|溶解实验；阅读举证；求和程序|9|实际分支会话，按目标证据继续或结束|
|14 补救材料与复查|等整体分数条；密度数据表；一次函数图点|9|真实隔离工作区，修订两页结构化材料和教师参考|
|05 外部分数锚定|蒸发实验解释；阅读双证据；最大值程序规格|9|同作品、同量尺的盲评/0分/4分对照|

题目编号为 `ELE-V2-{主方向}-101` 至 `103`，未改动原V1/V2题包。交叉方向只作解释，不增加覆盖数。57个版本应分开投递，不是57个独立样本；同一题族的版本不得放进同一被测上下文。

流程：cards.jsonl是机制卡，authored是权威题目源；专用builder导出items/prompts/runtimes、题册、评分册、reference、manifest与reports。只编辑机制卡、authored及协议，再重新导出，禁止手改生成报告。工作区stimuli是只读审阅副本，须与authored.runtime.initial_files同步，校验器检查逐字一致。

复现（需Python、pytest与markdown-it-py；不调用模型API）：

```bash
python scripts/build/build_edu_last_exam_h_patterns.py
python scripts/build/build_edu_last_exam_h_patterns.py --validate-only
python scripts/build/build_edu_last_exam_challenge_items.py --validate-only
python -m pytest -q tests/test_edu_last_exam_challenge_trial.py tests/test_edu_last_exam_h_patterns.py
```

本次宿主默认Python缺少两个依赖，已在 `/tmp/ele_h_patterns_deps` 安装；同一环境可在上述命令前加 `PYTHONPATH=/tmp/ele_h_patterns_deps:.`，没有修改仓库依赖或全局Python环境。该临时路径不是题包依赖来源承诺。

不要把review、reference、完整items或含私有submit_checks的runtime文件直接拼进被测提示。执行器只投递当前prompt、当前公开动作菜单和实际读取到的文件/观察。题册只供人工逐题阅读，包含多个依赖版本。
