# MathTutorBench · 教学法指令遵循 · Hard

**一句话**：在更困难的上下文中按指定教学法完成辅导。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "沿用教学法指令遵循任务，在固定 hard 子集上观察回复质量。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "MathDial / BRIDGE 的 hard 子集"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "判分",
      "value": "固定 LLM 裁判；严格胜率"
    }
  ],
  "credits": [
    {
      "text": "Jakub Macina、Nico Daheim、Ido Hakimi、Manu Kapur、Iryna Gurevych、Mrinmaya Sachan，EMNLP 2025",
      "url": "https://github.com/eth-lre/mathtutorbench"
    },
    {
      "text": "论文：MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors（EMNLP 2025）",
      "url": "https://aclanthology.org/2025.emnlp-main.11/"
    }
  ],
  "family_id": "mathtutorbench",
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 这是哪个子任务

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是教学法指令遵循的 hard 子集，与常规版分开计分。
- 它属于家族里四个开放式生成任务之一，判分方式是与参考回复比较的胜率。
- 当前 hard 版比常规版拉得更开一些，但两者高度相关，应作为难度变体而不是独立复证。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 对话数据来自 MathDial，英文。

## 任务与判分

- 给定较难的辅导上下文和一条教学法指令，模型按该教学法生成回复，成对比较取胜率。
- 官方用专家级奖励模型判分，本仓库改用 LLM 裁判做成对判决。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=10、mean=7.642、SD=0.866、范围 6.284–8.639，没有 ceiling 或 low_variance 标记。SD 高于常规版的 0.619、低于 scaffolding_hard 的 1.394，因此当前它不是两个 hard 变体中离散度更高的一个。
- 与常规版的同次配对使用 10 个共同模型，Spearman ρ=0.903，90% CI [0.615, 1.000]。信息重叠度高，不应视为两份独立证据；小样本下也不把点估计当作精确效应量。
- 当前分数仍明显高于同家族的 scaffolding_hard（mean=2.631）——策略给定和策略自选之间的落差在 hard 条件下依然存在；两者都是 win-rate cell，但仍受各自参考回复与裁判影响。
