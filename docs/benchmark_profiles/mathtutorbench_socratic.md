# MathTutorBench · 苏格拉底式提问

**一句话**：围绕数学题生成帮助学生逐步思考的引导性问题。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "使用 GSM8K socratic 版本的问句作为参考，衡量生成问句与参考的文本匹配。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "GSM8K socratic test；1,319 题"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "判分",
      "value": "最佳匹配 SacreBLEU"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是苏格拉底式提问。
- 它在判分方式上自成一类：既不是规则判分的硬任务，也不是胜率判分的开放任务，而是拿模型生成的问句和金标问句比措辞相似度。
- 引导式提问是辅导里最能体现"不代替学生思考"的动作，构念上很重要，但正因为好问题有很多种问法，它也是最难判分的。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 对话数据来自 MathDial，真实学生数学错误场景，英文。

## 任务与判分

- 给定学生犯错的对话上下文，模型生成下一句引导性提问。
- 用 SacreBLEU 与金标问句取最佳匹配打分。

## 局限与注意

- **BLEU 对短问句是弱指标。** 一个合理但换了说法的好问题会被误罚，而措辞贴近金标的平庸问题反而得分高——分数方差里"引导质量"和"措辞相似"分不开。
- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=8、mean=2.801、SD=0.339、范围 2.131–3.226，带 low_variance 标记并属于 `variance_restricted`，没有 ceiling 标记。低分至少有一部分来自判分方式而非模型表现，不宜直接读作“模型不会引导”；涉及该 cell 的配对也不进入构念裁决。
- v7 已把它计入 P15 教学策略执行与 P17 适配性解释，不再是待补挂状态；具体权重以 v7 JSON 为准。权重使用仍需考虑上述 BLEU 局限，也不能把它与胜率类分数当作同一指标。
