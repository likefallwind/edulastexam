# MathTutorBench · 学生解答正误判断

**一句话**：判断学生的数学解答是否正确。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "将学生解答与参考解对照，按正确与错误标签规则评分。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "StepVerify；正确与错误解答视图"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "判分",
      "value": "正误标签匹配"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是判定学生解答正误的那个。
- 与它相邻的两个诊断任务是定位错误步骤和给出修正，三者构成诊断由浅入深的三层：判对错、指出哪一步、说清怎么改。
- 三层分开计分，是因为模型的表现明显不同步——判得出对错，未必定位得准，更未必解释得了。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 学生解答数据来自 eth-nlped/stepverify，英文。

## 任务与判分

- 给定题目、参考解和一份学生解，模型判断学生解是否正确。
- 规则判分，判分逻辑移植自官方实现，不经过裁判。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=9、mean=8.720、SD=0.134、范围 8.567–8.952，同时带 ceiling 与 low_variance 标记，属于 `variance_restricted`。当前面板判“对还是错”的得分普遍较高且拉不开差距；涉及该 cell 的配对不进入构念裁决。
- 这一项同时作为自我校验能力的辅助证据计入——判别别人的解法对错和复查自己的输出共享同一种核验动作，但它不是那项能力的主证据。
- 判对错是诊断里最浅的一层。这一项分数高，不说明模型能指出错在哪，更不说明能解释为什么错。
