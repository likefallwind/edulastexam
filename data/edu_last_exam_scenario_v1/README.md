# 场景候选集机器可读协议

- `protocol.json`：5包/12版本、独立单次调用、作者/被测面板隔离与待审核状态。
- `source_manifest.json`：原库commit、记录索引、原图哈希、下载位置、许可状态及筛选排除项。
- 题目源与导出物：[private/edu_last_exam_scenario_v1](../../private/edu_last_exam_scenario_v1/README.md)。

本目录不保存原始下载数据或API凭据。源数据在忽略目录`sources/datasets/edu_last_exam_scenario_v1/`；图像投递副本也不入Git。模型可见输入仅来自导出的`prompts.jsonl`及其声明的`stimuli`，不包含这里的审查标签或金标。
