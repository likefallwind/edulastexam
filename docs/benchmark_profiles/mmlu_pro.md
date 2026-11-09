# MMLU-Pro

**一句话**：用更具推理要求、最多十个选项的学科题评估通识知识与复杂答题能力。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "MMLU-Pro 在原有学科知识评测基础上增加选项并提高推理题比例，覆盖法律、工程、心理学和自然科学等领域。",
    "模型作答后提取最终选项，与标准答案比较；该任务测量学科答题表现。"
  ],
  "facts": [
    {
      "label": "数据规模",
      "value": "12,032 道 test 题；14 个学科大类"
    },
    {
      "label": "语言与形式",
      "value": "英文；最多 10 选 1"
    },
    {
      "label": "判分",
      "value": "选项精确匹配"
    }
  ],
  "credits": [
    {
      "text": "TIGER-Lab，2024",
      "url": "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro"
    },
    {
      "text": "MMLU-Pro 数据 MIT 许可",
      "url": "https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro/blob/main/README.md"
    },
    {
      "text": "论文：MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark（2024）"
    }
  ]
}
```
<!-- public-profile:end -->


## 出处与背景

- TIGER-Lab，2024（论文 *MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark*）；https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro
- 动机：原版 MMLU 被强模型刷到 88%+ 接近饱和，且对 prompt 敏感；MMLU-Pro 通过 10 选 1 + 提高推理占比来恢复区分度。

## 数据

- 约 12,000 题，14 个学科大类（数学、物理、化学、法律、工程、心理学等），英文。
- 获取：`TIGER-Lab/MMLU-Pro` 公开可下（注意 `TIGER-AI-Lab/` 路径是 gated 的，别用错）；`fetch_eval_datasets.py --benchmark mmlu_pro` 落到 `sources/datasets/`。

## 任务与判分

- 10 选 1 选择题，模型输出选项字母。
- 规则判分：官方 `answer is (X)` 正则提取，失败时走 LLM 提取兜底；精确匹配字母。无裁判依赖。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/mmlu_pro.py`，`--benchmark mmlu_pro`。
- 按 category 出分桶。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：overall/category accuracy 格在当前面板 n=9、均分 8.489、SD=0.288，触发 low_variance、但未触发 ceiling。该面板上的排名信息有限，不能外推为对新模型也无区分度。
- 训练数据污染风险高（公开考试题库类）。
- 纯英文，对中文教育场景是间接证据。

## 当前映射

- P05 知识调用 0.60 / P06 推理 0.30 / P01 指令遵循 0.10；evidence_tier = foundation_gate。
- 构念核对：P01 挂载属于搭车（R9）；§2.7 冗余规则下它是三个基础答题类里**保留的那一个**（agieval/ceval 转按需）。
