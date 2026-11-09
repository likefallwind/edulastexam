# MathTutorBench · 解题

**一句话**：直接解答数学应用题，检验基础数学答题表现。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "模型生成完整解答，并以最终数值答案匹配金标。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "GSM8K test；1,319 题"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "判分",
      "value": "数值答案匹配"
    }
  ],
  "credits": [
    {
      "text": "Jakub Macina、Nico Daheim、Ido Hakimi、Manu Kapur、Iryna Gurevych、Mrinmaya Sachan，EMNLP 2025",
      "url": "https://github.com/eth-lre/mathtutorbench"
    },
    {
      "text": "题例原始数据：OpenAI / GSM8K，2021 · MIT",
      "url": "https://github.com/openai/grade-school-math/blob/master/LICENSE"
    },
    {
      "text": "论文：MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors（EMNLP 2025）",
      "url": "https://aclanthology.org/2025.emnlp-main.11/"
    }
  ],
  "family_id": "mathtutorbench"
}
```
<!-- public-profile:end -->


## 这是哪个子任务

- 家族 MathTutorBench（ETH Zurich LRE 组，2025）按学习科学理论把"辅导"拆成九个可分别计分的任务，本页是其中的解题任务。
- 九个任务分三类判分：四个规则判分的硬任务（解题、判解法对错、定位错误步骤、给出修正）、一个用 BLEU 对金标问句比对的苏格拉底式提问、四个用胜率判分的开放辅导任务（脚手架与教学法指令，各含一个 hard 变体）。
- 每个子任务单独计分而不合成家族总分，是因为它们的难度与判分方式差得太远——合成会让门槛类任务的高分掩盖辅导类任务的低分，而那个落差恰恰是本体系最想呈现的结论。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 题源为 GSM8K 的小学数学应用题，英文。

## 任务与判分

- 给一道数学题，模型直接作答，按数值匹配规则判分，不经过任何裁判。
- 这是家族里判分最硬的一类，分数没有裁判噪声。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=9、mean=9.670、SD=0.112、范围 9.477–9.803，同时带 ceiling 与 low_variance 标记，属于 `variance_restricted`。当前模型面板几乎贴在天花板上；涉及该 cell 的配对不进入构念裁决。
- 它证明的是"会做题"，完全不能证明"会教"。整个体系里它的权重被刻意压得很低，就是为了不让解题能力冒充教学能力。
- 看这一项时应对照同一家族的脚手架任务。当前 scaffolding 是另一个 n=10 的 cell，mean=2.858、SD=1.565、范围 1.100–5.948；两者可用面板不同，因此这是分 cell 对照，不冒充同一固定面板上的严格分差。
