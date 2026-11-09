# C-Eval

**一句话**：以中文多学科考试题评估从中学到职业资格层面的知识与推理。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "覆盖 52 个学科和四个难度层级，题目采用四选一形式。",
    "当前使用公开答案的验证集；它与需提交官方平台评分的隐藏测试集是不同划分。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "13,948 题；52 学科"
    },
    {
      "label": "当前题单",
      "value": "val 集 1,346 题"
    },
    {
      "label": "判分",
      "value": "5-shot answer-only；选项精确匹配"
    }
  ],
  "credits": [
    {
      "text": "上海交通大学、清华大学、香港科技大学等，2023",
      "url": "https://github.com/hkust-nlp/ceval"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- 上海交大 / 清华 / 港科大等，2023（NeurIPS 2023 Datasets & Benchmarks）；https://github.com/hkust-nlp/ceval
- 动机：给中文大模型一个覆盖国内考试体系的知识基准，弥补 MMLU 英文中心的问题。

## 数据

- 13,948 题选择题（4 选 1），52 学科 × 4 难度（初中/高中/大学/职业资格）。
- **官方 test 集答案不公开**（要提交官网评分）；本仓库评的是带标签的 **val 集 1,346 题**。
- 获取：`fetch_eval_datasets.py --benchmark ceval` 遍历 52 个 subject config，学科→大类映射读官方 repo 的 `subject_mapping.json`。

## 任务与判分

- 官方协议是 **5-shot answer-only**：每学科 5 道 dev 题作为多轮示例、回复裸字母；本仓库 adapter 照搬（无 LLM 提取，读首字母精确匹配，同官方 `response[0] == answer`）。
- 按大类和学科出分桶。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/ceval.py`；注意 p08_calibration 里复用 ceval 时改走 0-shot（要给置信度后缀留空间）。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：overall/category/subject accuracy 格在当前面板 n=10、均分 8.929、SD=0.451，标记 ceiling + low_variance。这是当前面板的受限结论，不外推为所有模型面板上永久不变的“最严重天花板”。
- 污染风险极高：题目来自公开考试题库，且发布已两年多。
- val 只有 1,346 题，学科级分数样本很小。

## 当前映射

- P05 0.60 / P06 0.25 / P01 0.15；foundation_gate。
- 构念核对：P01 搭车（R9）。§2.7 冗余决策：**转为按需跑**——只在评测中文优先模型时启用（与 mmlu_pro ρ≈1 只在现有模型上成立，中文特化模型未必）。
