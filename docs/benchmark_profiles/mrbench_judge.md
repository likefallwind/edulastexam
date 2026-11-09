# MRBench · 回复评价

**一句话**：评价已有辅导回复，并检查模型标签与人类标注的一致性。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "对话来源包含 MathDial 和 BRIDGE。被测模型逐维评价已有回复，与人类金标比较。",
    "生成与评价是不同任务，结果分别报告。"
  ],
  "facts": [
    {
      "label": "数据范围",
      "value": "200 段对话；每段至多九种模型回复"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "维度",
      "value": "八个教学质量维度"
    },
    {
      "label": "判分",
      "value": "逐维 macro-F1"
    }
  ],
  "credits": [
    {
      "text": "Maurya、Kochmar 等 / MBZUAI，2025",
      "url": "https://github.com/kaushal0494/UnifyingAITutorEvaluation"
    }
  ],
  "family_id": "mrbench",
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 这是哪个子评测

- 家族 MRBench（NAACL 2025，MBZUAI）是 AI tutor 回复质量的八维人工标注基准，本仓库据此实现了两个方向相反的子评测。
- 本页是判卷侧：模型当裁判。另一个是生成侧：模型当 tutor 写回复。
- 两者共用同一批人类标注，但被测能力完全不同，所以分开计分；本页只挂到主观题评价能力上。

## 出处与背景

- Maurya、Kochmar 等（MBZUAI），NAACL 2025；仓库 kaushal0494/UnifyingAITutorEvaluation。
- 数据为 200 段真实学生数学错误对话，每段配至多 9 个 tutor 模型的回复，八维人工标注。英文。

## 任务与判分

- 模型逐维贴标签，与人类金标算一致性，取 macro-F1 而非裸准确率——标签类别高度不平衡。
- 这是本体系里唯二直接测"判卷能力"的证据之一，另一个来自 BEA 2025。

## 局限与注意

- **区分度（13 号，v7/R28，2026-11-02）**：8-dimension tutor response judging 格在当前面板 n=10、均分 5.287、SD=0.539、范围 4.109–5.938，未触发 ceiling 或 low_variance。这表示当前面板保留了一定模型间差异，但不等于判卷构念已经完成效度验证。
- 这一类证据曾被整体排除在计分之外，后来因为构念对口而重新纳入：判卷能力这项能力，被测的就是判卷本身。
- 只在主观题评价能力上计分，不进任何其他能力。
- **量尺问题**：macro-F1（当前归一分约 4.1–5.9）与同一层里的评分一致性指标不在同一度量尺度上，两者进同一个加权平均隐含了可比性假设，待单独处理。
- 200 段对话的样本量偏小，因裁判协议噪声，置信度做了一档折价。
