# MathTutorBench · 错误修正

**一句话**：阅读错误解答后给出修正后的数学答案。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "将修正后的最终答案与参考答案对照；该指标不直接评价修正过程的教学质量。"
  ],
  "facts": [
    {
      "label": "数据来源",
      "value": "StepVerify；错误解答与参考解"
    },
    {
      "label": "语言",
      "value": "英文"
    },
    {
      "label": "判分",
      "value": "最终答案规则匹配"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是纠错任务。
- 它是错误诊断三层里最深的一层的一部分：判对错、定位步骤之后，纠错要求模型真的把正确的路径走出来。
- 与前两层分开计分，是因为纠错同时需要诊断和重新解题两种能力，失败原因可以来自任何一侧。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 学生解答数据来自 eth-nlped/stepverify，英文。

## 任务与判分

- 给定含错的学生解答，模型产出修正后的正确答案，从回复中提取答案后按规则判分。
- 不经过裁判，但判的是最终答案而不是修正过程。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=9、mean=8.993、SD=0.395、范围 8.303–9.421，同时带 ceiling 与 low_variance 标记，属于 `variance_restricted`。当前面板高分且离散度小，优先动作是提高难度或更换切分。
- 与 problem_solving 的同次配对使用 9 个共同模型，Spearman ρ=0.610，90% CI [-0.029, 0.964]；早期 pilot 的“相关接近 1”不适用于当前面板。不过该配对两侧均为方差受限，不进入构念裁决，也不能反过来据此断言纠错主要测的是解题能力。
- 判最终答案而不判修正过程，意味着"改对了但没说清为什么原来错"拿的是满分。它作为错因归因的证据只能算弱信号，主证据在别处。
- 这一项同时给推理与生成、适配性解释两项能力提供弱信号，都是尾部权重。
