# K12Vista

**一句话**：通过中文 K12 图文学科题评估模型读图与多步推理。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "覆盖数学、物理、化学、生物和地理，包含选择、填空与问答。",
    "固定抽样按题型和学科学段分层；多空题同时保留整题全对率与逐空部分得分。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "33,660 题"
    },
    {
      "label": "固定题单",
      "value": "600 题：选择 209、填空 198、问答 193"
    },
    {
      "label": "语言与形式",
      "value": "中文；图文输入"
    }
  ],
  "credits": [
    {
      "text": "Li 等，2025",
      "url": "https://github.com/lichongod/K12Vista"
    },
    {
      "text": "论文：K12Vista（2025）",
      "url": "https://arxiv.org/abs/2506.01676"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- Li et al. 2025, *K12Vista*（arXiv:2506.01676），官方仓库 github.com/lichongod/K12Vista，数据 `lipku1999/K12-Vista`（公开，无 gate）。
- 接入动机：P04 在测量模型 v1 里是四个完全空白的 P 之一（`model_type: undeclared`，零格子）。缺口推荐文档（2026-07-11）把 K12Vista 列为首选，理由是中文、公开有标签、静态图文、接入成本与 mathvista 同级。

## 数据

- `fetch_eval_datasets.py --benchmark k12vista` → 克隆官方仓库（要 `K12_Vista/code/prompt.py`）+ 下 `K12_Vista.jsonl`（33,660 行 / 501 MB）。
- **图是 base64 内嵌在 `img` 字段的**，没有单独的图片包——省了配图这一步。
- `build_k12vista_sample.py --size 600` 生成**固定题单** `data/k12vista/item_list_v2.txt`：按 `题型 × 学科-学段` 分层（33 个层，按人口比例分配、每层至少 1 题），解码出图片到 `sources/datasets/k12vista/images/`，并写一份去掉 base64 的瘦身 jsonl。所有模型跑同一份题。
- 抽样构成：选择题 209 / 填空题 198 / 问答题 193；11 个学科-学段各 53-64 题；难度 难 426 / 较难 132 / 中 31 / 较易 11（自然分布，与全量一致）。
- **难度为什么不做分层轴**：`difficulty` 是数据自带的五档标签，但论文对它怎么来的只字未提，官方 `evalaute.py` 的汇总轴也只有 `题型 × 学科-学段`（学段已编码在 subject 里，如 `math-g9`），根本不用它；而且全量分布极偏（难 71.7% / 较难 22% / 易仅 4 题）。v1 拿它当第三轴撑出 121 个层，每层至少 1 题的地板吃掉 300 个名额里的 121 个，把样本拉得比全量偏易约 15pp（难档 54.7% vs 全量 71.7%）。v2 起难度只作报告分桶，并注明标签未经校准。
- **样本量**：600 题时总分 95% CI 约 ±4pp，单个学科-学段桶约 ±13pp（v1 的 300 题分别是 ±5.7pp / ±17-20pp）。要在学科-学段这一档做严肃比较（每桶 ±10pp 以内）可提到 900——改 `--size` 重跑即可，脚本幂等。

## 任务与判分

- **提示词照搬官方** `prompt.py::infer_prompt['directly_infer_prompt'][题型]`（三种题型三套）。官方 runner 会把题干里的 `<image>` 占位符删掉、把图放在文本**前面**（`models/vllminfer.py`），我们一致。
- 官方 `evalaute.py` 的汇总轴是 `题型 × 学科-学段`，外加按学科、按学段的边际——**不含难度**。
- **判分照搬官方** `eval_prompt['directly_eval_prompt'][题型]`：裁判逐空提取参考答案与学生答案，输出 `<evaluation>[[参考],[学生],[0/1 列表]]</evaluation>`，**题分 = 各空得分均值**（多空题部分给分，见 `models/K12_PEM_judgemodel.py`）。
- 表头 `accuracy` = 严格全对率（所有空都对）；官方口径的部分给分均值在 `extra_metrics.official_score`，`score_10` = 10× 它，供能力聚合用。按题型/学科/学段/难度分桶。

## 在本仓库怎么用

```bash
/home/likefallwind/miniconda3/bin/python scripts/eval/data/fetch_eval_datasets.py --benchmark k12vista   # 一次性
/home/likefallwind/miniconda3/bin/python scripts/eval/data/build_k12vista_sample.py --size 600           # 一次性，固定题单
MODEL=MiniMax-M3 ./scripts/run_eval.sh k12vista        # 被测模型必须是视觉模型
MODEL=doubao-seed-2.0-pro K12VISTA_JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh k12vista
```

## 局限与注意

- **裁判不是官方那一个**。官方判分用 GPU 部署的 Qwen2.5-VL-72B 或微调的 K12-PEM，本地起不来；这里换成 API 裁判（`K12VISTA_JUDGE_MODEL`，默认 `MiniMax-M3`）。rubric 原文一字未改，但**裁判模型本身没有拿人工金标校准过**，报告里必须直说，不能声称与官方榜单可比。
- 裁判只看文本（题干、标准答案、解析、学生作答），不看图——官方也是这样，所以裁判不需要视觉能力。
- **模型面天然受限：主测 5 个模型里只有 2 个能看图**。2026-07-13 用真实题图逐个探测的结果——能看图：`MiniMax-M3`、`doubao-seed-2.0-pro`、`doubao-seed-2.0-lite`、`kimi-k2.6`；不能看图：`MiniMax-M2.7`（纯文本）、`glm-5.2`（网关 400）、`deepseek-v4-pro`。
- **`deepseek-v4-pro` 是个陷阱**：收到图片不报错、返回 200，然后回一句"你没有上传图片"照样作答。跑之前不探测的话，会静默产出一堆瞎猜的分数而判分链路毫无警告。**文本模型在 K12Vista 上必须标"不适用"，绝不能记 0 分**——那是测量假象不是能力差距。
- **区分度（13 号，v7/R28，分析日 2026-11-02）**：三个当前格子均已有 n=5，不再是“待凑够 4 个模型”的状态。math problem-figure subset score 均分 7.536、SD=0.464（low_variance）；official partial-credit score 均分 6.675、SD=0.868（未受限）；science/geo subject-chart subset score 均分 6.364、SD=1.020（未受限）。子维度结论不可互换，n=5 配对仍需宽置信区间约束。
- 只跑 600 题抽样，不跑全量 33k：预算约束，且分层已覆盖全部 33 个层。抽样误差要在报告里带上（bootstrap CI）。

## 当前映射

- v7 当前按三个 cell 使用：数学题图子集与科学/地理学科图表子集进入 P03 多模态理解，official partial-credit score 分别向 P05 知识调用和 P06 推理提供弱证据；具体权重以 `data/mapping_measurement_model_v7.json` 为准。
- 旧“P04 提案、权重未定、待 R15 裁决”的文字仅是历史状态，不再描述当前映射。
