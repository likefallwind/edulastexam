# 难题候选初审记录（2026-11-11）

本表来自 `reports/difficulty_mining_v1/cross_suite_candidates.jsonl` 中同时出现在 `mini_v2` 和 `frontier_v1`、且两套模型面板都判为全错的 8 个候选。它是作者离线题面/金标初审，不是教师审核，也不是冻结 benchmark 结论。

## 初审结果

|benchmark|item|初步状态|观察|下一步|
|---|---|---|---|---|
|C-Eval|`college_economics-val-45`|待领域复核|序数效用论题，gold 为 D“不饱和性”；从经济学常见假设看有一定合理性，但需核对原题版本和术语范围。|请经济学教师核对选项、教材口径和年份。|
|C-Eval|`computer_network-val-12`|题目缺陷高疑|B、C 两个选项逐字相同，gold 为 B；即使模型知道答案，也无法按选项区分。|从候选池剔除或修复原题后重新评测。|
|C-Eval|`middle_school_biology-val-16`|待领域复核|“植物人”保留心跳呼吸、无意识，gold 为脑干；题面有医学/教材术语边界。|核对中学生物教材的标准表述。|
|C-Eval|`teacher_qualification-val-23`|金标疑似错误|A1:A3 为数值 1、2、3，A4 为文本“3”；`COUNT(A1:A4)+12` 应为 15（A），而源 gold 为 D=18。|用目标 Excel 版本或官方解析复核；修正前剔除。|
|MOOCCube|`mooccube-mcq-de912b1f9b`|金标/构造缺陷高疑|目标为“公开密钥加密”，gold 概念却是“数据传送”；选项也没有与目标定义直接对应的公钥加密概念。|回到概念图谱和生成规则核对 target/gold。|
|MOOCCube|`mooccube-order-09096933f1`|图谱/协议待审|6 个数学概念、5 条约束，chance=0.036111；可能有多个合法拓扑序。|运行规则评分器枚举合法序列，并核对边方向。|
|MOOCCube|`mooccube-order-75290c320c`|图谱质量高疑|“状态—连通性—连通图—孩子—中序遍历”等跨主题边方向缺乏明显先修语义。|逐条回溯专家边/生成快照。|
|MOOCCube|`mooccube-order-91c7baf04e`|图谱质量高疑|“协议数据单元”被连到“密钥长度”“数据通信”“最大传输单元”等概念，且混入数学字段。|核对原始图谱方向、字段和所有合法拓扑序。|

## 这批抽查说明什么

8 个候选确实是两个历史模型面板都难以回答的题，但初审已经发现至少 3 个明显的题目/金标或图谱质量问题，另有 3 个需要领域或协议复核。它们暂时只能标记为 `historical_model_error`，不能标记为 `ai_hard`、`human_hard` 或 `gold_stable`。

这也验证了后续筛选顺序：先做题面、gold、评分协议、合法答案和输入完整性审计；通过后再按 37 个方向的失败机制映射，并用未参与筛选的模型或教师证据复测。MOOCCube 的 `chance`、约束数和反向干扰项只能作为结构挑战变量，不能替代人类难度校准。C-Eval 的学科级 Hard 也不能当逐题难度标签。

## 来源

- 逐题历史面板聚合：`reports/difficulty_mining_v1/summary.json`、`reports/difficulty_mining_v1/cross_suite_candidates.jsonl`。
- C-Eval 原题：`../edubenchmark/sources/datasets/ceval/data/val.jsonl`。
- MOOCCube 本地协议题：`../edubenchmark/sources/datasets/mooccube/items_v1.jsonl`。
- 37 方向机制与候选映射：`data/edu_last_exam_difficulty_mining_v1/direction_mechanism_map.json`。
