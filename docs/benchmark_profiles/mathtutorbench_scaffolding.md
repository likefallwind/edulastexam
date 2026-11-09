# MathTutorBench · 教学脚手架

**一句话**：在学生卡住时给出帮助其继续思考的下一句辅导。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "根据数学题与师生对话生成简短回复，与参考回复进行教学质量成对比较。"
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
      "value": "固定 LLM 裁判；位置平均胜率为主，双序全胜率为辅"
    }
  ],
  "credits": [
    {
      "text": "Jakub Macina、Nico Daheim、Ido Hakimi、Manu Kapur、Iryna Gurevych、Mrinmaya Sachan，EMNLP 2025",
      "url": "https://github.com/eth-lre/mathtutorbench"
    },
    {
      "text": "题例原始数据：Macina 等 / MathDial，2023",
      "url": "https://github.com/eth-nlped/mathdial"
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

- 家族 MathTutorBench 把辅导拆成九个可分别计分的任务，本页是脚手架生成，另有一个更难的 hard 变体单独计分。
- 它属于家族里四个开放式生成任务之一（脚手架、脚手架 hard、教学法指令、教学法指令 hard），判分方式是与参考回复比较的胜率，而不是规则匹配。
- 这是整个体系里最接近"真的在辅导"的任务：不给答案、不讲一整套，只给下一步。

## 出处与背景

- ETH Zurich LRE 组（Macina 等），2025；https://github.com/eth-lre/mathtutorbench
- 对话数据来自 MathDial，真实学生数学错误场景，英文。

## 任务与判分

- 给定辅导对话上下文，模型生成下一句回复，与参考回复做两次位置交换的成对比较。主指标 `extra_metrics.win_rate` 先将每题两次投票取均值（0、0.5 或 1），再跨题平均；`strict_win_rate` 与 `accuracy` 保留为双序均胜的辅助比例。
- 主指标仅统计两次投票均完整有效的题，并单独报告有效判分覆盖率（有效题数 / 总题数）。缺票、调用失败或无法解析的裁判回复属于缺失判分，不计作模型失败；覆盖率不足时不把条件均值当作完整结果。
- 官方用一个 GPU 上的专家级奖励模型判分（该模型能区分专家教师与新手教师的回复）；本仓库改用 LLM 裁判做成对判决，绝对分因此不可与论文对照，横向比较仍然可用。

## 局限与注意

- **v7/R28（2026-11-02）**：该 subdimension cell 为 n=10、mean=2.858、SD=1.565、范围 1.100–5.948，没有 ceiling 或 low_variance 标记。它是家族内离散度最高的 cell，适合观察当前面板的教学生成差异；这一结论仅限当前家族和面板，不外推为全体系排名。
- 纯解题 cell 当前接近满分，而这里整体低得多，仍直观呈现“会答题≠会教”。不过 problem_solving 为 n=9、本 cell 为 n=10，两个描述统计不是同一固定面板上的严格分差。
- 胜率类分数依赖裁判，也与参考回复的风格相关——风格差异大的好回复可能被判负。
- 与 hard 变体的同次配对使用 10 个共同模型，Spearman ρ=0.939，90% CI [0.698, 1.000]。两者排序高度重叠但并非完全冗余，不应视为互相独立的两份复证。
