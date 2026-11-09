# challenge_v2 编写约定

逐题 JSON 放在 authored/<batch>.jsonl；修订时更新本批草稿，不触碰原12题。每条遵循 data/edu_last_exam_pilot_v1/challenge_v2/authoring_spec.json。题号 ELE-C2-01 至 ELE-C2-21。每个任务包可以有多个完整、独立可运行的 prompt 变体；不能在学生侧题面泄漏比较目的或预置诊断。附件路径相对于本批根目录，刺激文件只放 stimuli/NN/，参考解/参考产物只放 reference/NN/，离线自检放 checks/NN.py。

每题4–6条实质评分项，权重合计10；跨变体题的评分项按任务包汇总，不把随机措辞视为公平性失败。critical_errors 只列实质严重错误，本批不继承‘任意硬门槛归零’。人审和模型实测都保持 pending/not_run。禁止在 source_evidence 或题面中把合成案例说成真实学生数据。

所有提示必须自包含或引用实际存在的附件。允许工具，能用算式/程序验证的金标必须离线验证。工具/图片任务需要真实素材，不能只写TODO。第一批每方向1个任务包；目的在形成可审阅候选，不能预先宣称模型一定失败。
