# MRBench · 辅导生成

**一句话**：根据学生数学错误对话生成下一句有帮助的辅导回复。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "对话来源包含 MathDial 和 BRIDGE。被测模型生成回复，由固定裁判逐维评价教学质量。",
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
      "value": "固定裁判逐维标签"
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
- 本页是生成侧：模型当 tutor，被别人评。另一个是判卷侧：模型当裁判贴标签。
- 八个维度里，本体系刻意取单维度分而不是复合通过率——一个通过率数字会把识别错误、提供引导、可执行性三种不同能力糅在一起。

## 出处与背景

- Maurya、Kochmar 等（MBZUAI），NAACL 2025；仓库 kaushal0494/UnifyingAITutorEvaluation。
- 动机：把 tutor 回复质量的评价维度统一成一套分类学，后来直接衍生出 BEA 2025 共享任务。
- 数据为 200 段真实学生数学错误对话（源自 MathDial 与 Bridge），英文。

## 任务与判分

- 八个原生维度：识别错误、定位错误、是否泄露答案、提供引导、可执行性、连贯性、语气（鼓励/中性/冒犯）、拟人度。
- 模型生成下一句 tutor 回复，由固定裁判逐维标注。
- v7 按单维度取分：识别错误挂 P11 错因归因、提供引导挂 P15 教学策略执行、可执行性与语气鼓励占比挂 P17 适配性解释；语气非冒犯占比不再向 P18 供分，只保留为 related-only 非羞辱 sentinel。

## 局限与注意

- **区分度（13 号，v7/R28，2026-11-02）**：四个计分 cell 均为 n=8。Mistake_Identification 均分/SD=9.223/0.293、Providing_Guidance 8.974/0.274、Actionability 9.170/0.373，三者均为 ceiling + low_variance；Tutor_Tone (encouraging share) 为 8.497/1.404，未触发方差受限。前三个 cell 的受限配对不进入构念裁决，鼓励语气 cell 未受限也不等于已经完成效度验证。
- 只有 200 段对话，样本量小，维度级估计的噪声较大；跨模型面板的大小不增加原始对话样本量。
- 结果依赖固定裁判的标注质量，不是人工标注。
- 语气维度里的非冒犯占比在当前面板中没有显示模型差异。它在 v7 中只作 P18 的 related-only 非羞辱 sentinel，不参与评分；当前面板恰好都不冒犯，不代表指标永久饱和。
