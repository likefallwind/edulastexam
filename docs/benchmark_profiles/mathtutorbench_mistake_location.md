# MathTutorBench · 首处错误定位

**一句话**：指出学生数学解答中第一次发生错误的位置。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "数据包含逐步解答与首错位置标注，模型需定位出错步骤。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "StepVerify；逐步解答标注"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "判分",
      "value": "首错步骤识别；micro-F1"
    }
  ],
  "credits": [
    {
      "text": "Jakub Macina、Nico Daheim、Ido Hakimi、Manu Kapur、Iryna Gurevych、Mrinmaya Sachan，EMNLP 2025",
      "url": "https://github.com/eth-lre/mathtutorbench"
    },
    {
      "text": "题例数据：ETH NLP for Education / StepVerify（MathDial 衍生）",
      "url": "https://huggingface.co/datasets/eth-nlped/stepverify"
    },
    {
      "text": "题例按 CC BY-SA 4.0 展示；仅选取和排版原始字段",
      "url": "https://creativecommons.org/licenses/by-sa/4.0/"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是定位错误步骤的那个。
- 它夹在判定正误和给出修正之间，是错误诊断三层里的中间层：知道错了还不够，要说得出错从哪里开始。
- 这一层对教学的价值很直接——能定位到步骤，反馈才可能具体，否则只能说一句"你再检查检查"。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 学生解答数据来自 eth-nlped/stepverify，逐步骤标注了首个出错位置，英文。

## 任务与判分

- 给定题目与一份含错的学生解答，模型指出第一处错误发生在哪一步。
- 规则判分，与标注的首错步骤比对，不经过裁判。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=9、mean=7.707、SD=0.138、范围 7.450–7.919，带 low_variance 标记并属于 `variance_restricted`，但没有 ceiling 标记。当前结论是模型排序受低方差限制，而不是分数已经到顶；涉及该 cell 的配对不进入构念裁决。
- 这一项同时作为长上下文与证据定位能力的弱信号计入——定位行为是真实的，但材料很短，测不出长材料下的定位压力，所以权重压得很低。
- 只测首处错误。学生解答里往往有连锁错误，"后面几步是被第一步带歪的还是独立错的"这个区分没有覆盖。
