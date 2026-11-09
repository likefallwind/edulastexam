# MathTutorBench · 教学法指令遵循

**一句话**：根据指定教学法生成数学辅导回复。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "将教学法要求与师生对话一起提供给模型，再与参考回复成对比较。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "MathDial 与 BRIDGE；1,150 条上下文"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是教学法指令遵循，另有一个更难的 hard 变体单独计分。
- 它属于家族里四个开放式生成任务之一，判分方式是与参考回复比较的胜率。
- 与脚手架任务的区别在于：脚手架考的是自己选对下一步，这一项是策略已经给定，只考执行——把"不会选"和"选了也做不出"两种失败分开。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 对话数据来自 MathDial，英文。

## 任务与判分

- 给定辅导上下文和一条教学法指令，模型按该教学法生成回复，与参考回复成对比较取胜率。
- 官方用专家级奖励模型判分，本仓库改用 LLM 裁判做成对判决。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=10、mean=8.045、SD=0.619、范围 6.935–8.670，没有 ceiling 或 low_variance 标记。当前面板中它仍明显高于同家族脚手架任务；这与“给定策略比自选策略更容易执行”的解释一致，但两类 cell 不能混作同一指标。
- 这一项同时挂在教学专业知识上——按教学法指令生成，是教学法知识的生成式测法，与选择题式的测法互补。
- 与 hard 变体的同次配对使用 10 个共同模型，Spearman ρ=0.903，90% CI [0.615, 1.000]。两者信息高度重叠，不应视为两份独立复证；样本仍小，也不把点估计当作精确效应量。
