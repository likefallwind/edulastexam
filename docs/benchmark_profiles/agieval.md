# AGIEval

**一句话**：使用高考、SAT、LSAT 等人类考试任务评估中英文学科推理。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "题目来自标准化考试与资格考试，包含选择题及开放式数学填空。",
    "不同考试的题型与语言分别报告；选择题匹配选项，数学填空按答案等价性判分。"
  ],
  "facts": [
    {
      "label": "数据范围",
      "value": "21 个本地接入考试子任务"
    },
    {
      "label": "语言与形式",
      "value": "中文、英文；选择与填空"
    },
    {
      "label": "判分",
      "value": "规则评分；按考试分项"
    }
  ],
  "credits": [
    {
      "text": "Microsoft Research，2023",
      "url": "https://github.com/ruixiangcui/AGIEval"
    },
    {
      "text": "论文：AGIEval: A Human-Centric Benchmark for Evaluating Foundation Models（2023）"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- 微软，2023（论文 *AGIEval: A Human-Centric Benchmark for Evaluating Foundation Models*）；https://github.com/ruixiangcui/AGIEval
- 动机：用"给人设计的考试"而非"给模型设计的题"来衡量模型的人类级认知任务表现。

## 数据

- 约 20 个任务子集：高考各科、SAT、LSAT、律师资格、公务员行测、数学竞赛填空等；中英双语混合。
- 获取：数据随官方 repo checkout 直接可用（不需要 HF 下载）。

## 任务与判分

- 两种题型：选择题（字母精确匹配，选项解析移植官方 `post_process.py`）+ 数学填空（等价判断动态加载官方 `math_equivalence.is_equiv`）。
- 规则判分为主，无裁判依赖。按任务/语言/题型出分桶。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/agieval.py`；p08_calibration 复用其中部分题目做置信度测验。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：overall/task/language/question_type accuracy 格在当前面板 n=9、均分 8.718、SD=0.390，标记 ceiling + low_variance；该受限判断仅适用于此面板和取分口径。
- 污染风险高（历年真题全网可查）。
- 混合题型使单一 accuracy 数字掩盖了子集差异。

## 当前映射

- P06 0.45 / P05 0.35 / P01 0.20；foundation_gate。
- 构念核对：P01 搭车（R9）。§2.7 冗余决策：对新模型**降为可选**（与 mmlu_pro/ceval 相互 ρ≥0.9）。
