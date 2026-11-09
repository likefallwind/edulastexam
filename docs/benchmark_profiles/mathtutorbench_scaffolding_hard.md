# MathTutorBench · 教学脚手架 · Hard

**一句话**：在更困难的辅导上下文中提供下一步学习支架。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "保留脚手架任务的生成目标，在固定 hard 子集上独立报告表现。"
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
      "value": "固定 LLM 裁判；位置平均胜率为主，双序全胜率为辅"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是脚手架的 hard 子集，与常规版分开计分。
- 它属于家族里四个开放式生成任务之一，判分方式是与参考回复比较的胜率。
- 分开计分的初衷是看难度上升后模型是否掉队；当前结果显示 hard 版均分略低、模型排序高度稳定，但两个变体并非完全冗余。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 对话数据来自 MathDial，英文。

## 任务与判分

- 给定较难的辅导对话上下文，模型生成下一句回复，与参考回复做两次位置交换的成对比较。主指标 `extra_metrics.win_rate` 为逐题双序投票均值再跨题平均；`strict_win_rate` 与 `accuracy` 保留为双序均胜的辅助比例。
- 主指标仅统计两次投票均完整有效的题，并单独报告有效判分覆盖率（有效题数 / 总题数）。缺票、调用失败或无法解析属于缺失判分，不计作模型失败；覆盖率不足时不把条件均值当作完整结果。
- 官方用专家级奖励模型判分，本仓库改用 LLM 裁判做成对判决，绝对分不与论文对照。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=10、mean=2.631、SD=1.394、范围 1.101–5.612，没有 ceiling 或 low_variance 标记。它与常规版同属家族内离散度较高的 cell；这一描述仅限当前家族和面板，不外推为全体系排名。
- 与常规版的同次配对使用 10 个共同模型，Spearman ρ=0.939，90% CI [0.698, 1.000]。模型排序高度重叠但并非完全冗余；做效度检验时不得把两个变体互为独立证据。
- 当前 cell 均分比常规版的 2.858 低 0.227。两者该次配对有相同的 10 个共同模型，但这只是当前面板的描述性难度差，不外推为固定效应。
