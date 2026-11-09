# ASAP 2.0

**一句话**：让模型按作文评分标准打分，并比较其与人工评分的一致性。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "数据来自英语议论文自动评分任务，作文整体分为 1–6 分。",
    "当前评测使用官方测试划分，主要指标为二次加权 Kappa：分歧越大受到的惩罚越大。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "约 24,000 篇 6–12 年级议论文"
    },
    {
      "label": "当前题单",
      "value": "7,421 篇测试作文"
    },
    {
      "label": "主要指标",
      "value": "QWK；整体分一致性"
    }
  ],
  "credits": [
    {
      "text": "The Learning Agency Lab / ASAP 2.0，2024",
      "url": "https://github.com/scrosseye/ASAP_2.0"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- Kaggle "Learning Agency Lab – Automated Essay Scoring 2.0" 竞赛（2024），是 2012 年 Hewlett 基金会 ASAP-AES 的续作；https://www.kaggle.com/competitions/learning-agency-lab-automated-essay-scoring-2
- 动机：ASAP 2012 老化且泄露严重，2.0 换了新的学生作文集（约 24,000 篇，6-12 年级议论文），整体分 1-6。

## 数据

- 约 24k 篇真实学生作文，英文，holistic 1-6 分。
- **获取状态：Kaggle manual required（gated）**——本地无原始数据，仓库口径里记为证据缺口。

## 任务与判分

- 模型读作文 + rubric，输出整体分；指标 **QWK**（二次加权 Kappa，对"差得远的错"惩罚更重）。
- 无官方"模型 leaderboard"——它本来是训练竞赛，拿来测 LLM zero-shot 评分是社区用法。

## 在本仓库怎么用

- **无 adapter**，分数来自同事跑分（`otherbenchmark/`，`ASAP+Peda.png`），QWK 归一到 0-10。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：essay holistic QWK 在当前面板 n=7、均分 5.450、SD=0.509，未触发 ceiling 或 low_variance。它在该面板上保留了一定模型间差异，但 13 号 P12 评级仍为 insufficient_evidence，不能仅凭未受限就称为教育核心类中区分度最好的格子之一。
- LLM zero-shot QWK 天然偏低（人类评分员间 QWK 约 0.7-0.8），分数解释要对照人类基线。
- 只有整体分没有 trait 分，测不了细粒度评分能力（ELLIPSE/EssayJudge 才有多维，见缺口推荐）。

## 当前映射

- P14 rubric 评分 0.65 / P02 证据定位 0.20 / P05 0.15；education_core。
- 构念核对：P02 挂载属于搭车（R9）；P14 拆分后归"学业作答评分"facet（R3）。
