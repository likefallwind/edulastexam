## Context

当前 V2 把“存在已复核的 V1 失败”写成了新题准入条件，容易把后续工作收缩成少数错例的继续深化。此次修改将生产主线改为：**37 个方向逐方向做机制分析，再由机制生成题族和数据；文献、任务结构、已有成功/失败案例分别提供依据，历史错例不再是入场券。** 本次落实完整的 37 方向生成蓝图和生产队列，不把现有五题原地扩写或篡改既有运行证据。

## 修改方案

### 1. 建立 37 方向机制驱动生产规范

新增 `docs/plans/edu_last_exam_37_direction_mechanism_generation_plan_2026-11-12.md`，明确主流程：

`方向原始构念 → 任务要求与生成失败机制 → 必要输入条件 → 材料/情境变化轴 → 题族与反事实 → gold/rubric/oracle → 离线校验 → 审核与试跑`

规则包括：

- 01–37 每方向都必须有机制蓝图和至少一个题族生成计划，不能因暂时没有模型错例而跳过。
- 机制分析区分文献依据、任务结构推导、历史模型证据和待验证假设，不预设每个方向已经被证明困难。
- 错例用于支持、反驳或修正机制；成功例用于控制和回归；两者都不决定方向是否有资格造数。
- 不用换名字、数字或提示措辞冒充新题族；主方向、关联方向、独立题族和依赖版本分别记录。
- `blueprint / authored / executable / reviewed / tested / frozen` 分开统计；缺真实数据或原生环境的方向保留阻塞，不用弱代理伪造 37/37 可运行覆盖。

### 2. 写入完整的机器可读逐方向蓝图

新增：

- `data/edu_last_exam_mechanism_generation_v1/protocol.json`
- `data/edu_last_exam_mechanism_generation_v1/direction_blueprints.json`

蓝图复用并引用现有 `direction_index.json`、37 份 source card、`direction_mechanism_map.json` 和 route matrix，不另建方向 taxonomy。01–37 每条写清：

- 原始构念、具体教育任务和后果；
- Agent 可能采用的捷径、该捷径失效的任务条件及机制证据等级；
- 必须提供的证据、必须保留的未知/冲突/状态条件；
- 可观察信号和关键错误；
- 独立材料、学科情境及交互形态的变化轴；
- 题族计划、每版改变量/不变量、预期行为差异、正确/no-op/反事实控制；
- gold、评分或真实产物验收方式，以及未测子结论和阻塞条件；
- 可选的 V1/V2 成功或失败案例引用，而非必填失败证明。

### 3. 增加确定性校验与全方向生成队列

新增 `scripts/build/build_edu_last_exam_mechanism_generation.py` 和 `tests/test_edu_last_exam_mechanism_generation.py`，复用现有 JSON + Python validator + SHA-256 + pytest 模式：

- 校验 01–37 无重缺、原始标题和来源卡一致、来源路径与哈希有效。
- 校验每方向都有机制分析、生成条件、变化轴、题族计划、控制、评分及测量边界。
- 校验 family/mechanism ID 唯一，关联方向不虚增主方向覆盖，依赖变体不计为独立题族。
- 明确测试“没有历史 fail 仍可进入生成队列”；有历史证据时仍检查 case identity 和证据角色。
- blocked 蓝图可以进入设计和生成队列，但未解除阻塞前不得标成 executable 或 frozen。
- 由 builder 生成 `reports/edu_last_exam_mechanism_generation_v1/` 下的 37 方向覆盖与生成队列，不手改生成报告。

### 4. 解除 V2 的旧失败硬门槛，保留第一批身份

修改 `scripts/build/build_edu_last_exam_v2_pilot.py`、`data/edu_last_exam_v2_pilot/protocol.json` 和 `private/edu_last_exam_v2_pilot/cards.jsonl`：

- 支持 `--protocol` 和从协议解析批次，便于后续新题族使用新批次，而不是复制 builder。
- 每题必须绑定上述蓝图中的 `mechanism_ref`、来源卡和控制；`v1_evidence` 改为可选验证材料，不再要求所有题目都有 reviewed fail。
- 当前五题仍登记为第一批 5 题族、11 个依赖版本；其已有 V1 证据继续保留并严格校验。
- 协议改记 `v1_failure_required=false`、37 方向机制驱动作者方法和 `difficulty_claim=not_established`。
- 更新 `tests/test_edu_last_exam_v2_pilot.py` 的方向机制绑定和可选错例测试，保留现有数学、分支、工作区、gold 隔离及 stale-export 回归。

**不修改五个 authored JSON、stimuli 或任何历史模型回答/评分/分析报告。** 若协议元数据变化导致派生题册或 manifest 更新，只通过 builder 重建，并确认 `items.jsonl`、`prompts.jsonl`、`runtimes.json` 的内容哈希与 run01 保持一致。

### 5. 更新当前入口，不改写历史证据

- 在 `docs/plans/edu_last_exam_v2_pilot_design_2026-11-12.md` 增加后续路线说明：原文记录第一批样本的历史设计，新生成政策以 37 方向主计划为准。
- 更新 `private/edu_last_exam_v2_pilot/README.md`，说明第一批定位、可选历史错例和已有一次探索性运行。
- 在根 `README.md` 与 `docs/README.md` 加入新主计划和 37 方向生成队列入口。
- 不改完整证据清单、V1/V2 历史报告、item-selection 队列或既有 direction map；它们继续承担证据快照和下游候选排序职责。

## Verification

1. 运行新蓝图的 `--validate-only` 和构建命令，确认 37/37 蓝图覆盖及生成队列可重复构建。
2. 运行 `pytest -q tests/test_edu_last_exam_mechanism_generation.py tests/test_edu_last_exam_v2_pilot.py tests/test_edu_last_exam_difficulty_index.py`，包括缺少方向、缺少生成条件、无历史 fail 可通过、blocked 不可伪装可执行等正反例。
3. 运行 `python scripts/build/build_edu_last_exam_v2_pilot.py --validate-only`，并用 SHA-256 对照 run01 manifest，确认第一批实际题面、runtime 和 item 内容未漂移。
4. 不调用模型 API，不覆盖任何既有运行目录，不提交 Git commit。