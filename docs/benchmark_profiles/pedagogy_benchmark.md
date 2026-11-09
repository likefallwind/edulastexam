# Pedagogy Benchmark

**一句话**：使用教师职业考试题评估教学法专业知识。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "题目关注如何教学、如何理解学习过程和处理课堂问题，而不局限于学科事实。",
    "按官方提示与答案解析协议进行选择题评分；题目本体遵循发布方访问与展示要求。"
  ],
  "facts": [
    {
      "label": "当前题单",
      "value": "1,119 道计分题；另有 24 道提示示例"
    },
    {
      "label": "形式",
      "value": "教学法选择题"
    },
    {
      "label": "判分",
      "value": "选项匹配；REPAT 解析"
    }
  ],
  "credits": [
    {
      "text": "AI for Education / Fab Inc.，2025",
      "url": "https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark"
    },
    {
      "text": "论文：Benchmarking the Pedagogical Knowledge of Large Language Models（2025）"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- AI for Education（aiforeducation.io），2025（论文 *Benchmarking the Pedagogical Knowledge of Large Language Models*）；https://huggingface.co/datasets/AI-for-Education/pedagogy-benchmark
- 动机：模型的学科能力评得很多，教育学专业知识（学习理论、课堂管理、评估方法、特殊教育）几乎没人评。官方 leaderboard 覆盖 97 个模型。

## 数据

- 两个子集：**CDPK**（跨领域教学法知识，约 900 题选择题）和 **SEND**（特殊教育需求，约 300 题）。题目来自教师资格认证考试。
- **获取状态：HF gated**（要申请），本地没有原始数据——这是它和其他教育核心 benchmark 的关键区别。

## 任务与判分

- 选择题，accuracy，规则判分。
- 原生维度：CDPK 按教学主题分类；SEND 单列。

## 在本仓库怎么用

- **无 adapter**，分数来自同事跑分的外部报告（`otherbenchmark/`，0701 聚合卡片 + `ASAP+Peda.png`）。仓库里它是 `source_scope: otherbenchmark`。
- 映射里有三行：CDPK / SEND / 0701 聚合卡片（后者只在没有细分分数时用，去重逻辑保证不重复计分）。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：CDPK teaching knowledge selection 在当前面板 n=15、均分 8.457、SD=0.536；SEND special education needs selection n=15、均分 7.861、SD=0.543。两个子维度均未触发 ceiling 或 low_variance；旧 n=7 聚合统计和 pilot 的 ρ=−0.90 不再代表当前证据，R28 报告的红旗与观察带均为空。
- 无原始数据在手：没法复算、没法抽题检查污染、没法进 p08 复用。凡是基于它的结论都依赖同事报告的口径。
- "知道怎么教"≠"实际会教"——它是 P17 里唯一的知识侧证据，正因如此才拆了 strategy_knowledge facet。

## 当前映射

- CDPK：P05 0.45 / P17 0.35 / P06 0.20；SEND：P05 0.35 / P16 0.35 / P17 0.30；education_core。
- 构念核对：P06 problem_reasoning 挂载建议移出（R8）；P16/P17 的知识侧 facet 由它独家供分。
