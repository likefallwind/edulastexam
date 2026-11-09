# MathVista

**一句话**：结合图表、几何图和文字问题，评估视觉数学推理。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "将多个视觉数学数据来源整合为统一题目，要求模型同时理解图像和题干。",
    "题型包含选择、数值和文本答案；当前常用公开带标签的 testmini 划分。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "6,141 题"
    },
    {
      "label": "当前题单",
      "value": "testmini：1,000 题"
    },
    {
      "label": "形式与判分",
      "value": "图文输入；答案提取、规范化与匹配"
    }
  ],
  "credits": [
    {
      "text": "Pan Lu 等，2023 / ICLR 2024",
      "url": "https://github.com/lupantech/MathVista"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- Lu Pan 等（UCLA / 微软），2023，ICLR 2024；https://github.com/lupantech/MathVista
- 动机：数学推理评测此前几乎全是纯文本，MathVista 把 28 个既有多模态数据集 + 3 个新建子集统一成一个视觉数学基准。

## 数据

- 6,141 题；常用 testmini 1,000 题（带答案）；英文。
- 图片需单独下载：`cd sources/datasets/mathvista/data && wget .../images.zip && unzip`。

## 任务与判分

- 混合题型（选择/数值/文本），按 task / question_type / answer_type 分桶。
- 判分移植官方 `evaluation/`：few-shot 提取提示（`ext_ans.demo_prompt`）+ `normalize_extracted_answer` + 最近选项编辑距离，重实现在 `scripts/eval/scoring.py`，无额外依赖。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/mathvista.py`；必须用视觉模型（MiniMax-M3 可以，M2.7 纯文本不行）；`--dry-run` 会省略 base64 图片打印消息。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：整体 task/question_type/answer_type accuracy 格在当前面板 n=5、均分 8.518、SD=0.224，标记 ceiling + low_variance。已不再是单模型待配对状态，但该格仍受方差限制，不能据此作稳定排名或构念配对结论。
- 题源来自公开数据集拼装，部分子集污染风险高。
- 感知与推理混在一个 accuracy 里，拆不开（构念核对里归"解题式图像理解"）。

## 当前映射

- P06 0.45 / P03 0.35 / P05 0.20；diagnostic。
- 构念核对：P03 的最接近直接测量，R5 拆分后归"解题图像理解"facet。
