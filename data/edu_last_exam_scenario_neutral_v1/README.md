# 中性题面对照源

`prompt_control.json`固定原批次及原GLM试跑，逐包记录中性任务指令、必须保留的条件、删除的提示片段以及解释边界。附件、金标与rubric不在这里重写。

构建：`python3 scripts/build/build_edu_last_exam_scenario_neutral.py`；离线验证加`--validate-only`。输出位于[`private/edu_last_exam_scenario_neutral_v1/`](../../private/edu_last_exam_scenario_neutral_v1/README.md)。此文件不含API凭据，实验结果独立保留。
