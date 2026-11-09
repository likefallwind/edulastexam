# EduIllustrate

**一句话**：让模型把解题过程生成可运行、可理解的教学动画。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "模型生成 Manim 代码，经渲染得到可视化讲解，再从文本与视觉两个侧面评价教学表达。",
    "八项 rubric 各按 0–5 分评分；渲染失败单独影响结果。当前使用替代裁判，成绩不等同于论文榜单。"
  ],
  "facts": [
    {
      "label": "输出形式",
      "value": "Manim 动画代码与渲染结果"
    },
    {
      "label": "评价维度",
      "value": "四个文本维度、四个视觉维度"
    },
    {
      "label": "汇总方式",
      "value": "八维几何平均；同时保留分项"
    }
  ],
  "credits": [
    {
      "text": "EduIllustrate 作者团队，2026",
      "url": "https://github.com/ECNU-innoSpark/EduIllustrate"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- arXiv 2604.05005，2026。
- 动机：多模态教学评测几乎全在输入侧（看图答题），输出侧（画图讲题）没有基准；EduIllustrate 测"能不能把讲解变成正确、可读的可视化"。

## 数据与运行

- **不在本仓库 harness 里跑**：依赖 manim + texlive 太重，评测在上游克隆（`~/code/EduIllustrate`）执行；`scripts/eval/build_eduillustrate_report.py` 只负责把 8 维裁判分回灌到标准 `reports/eval/eduillustrate/<model>/` 布局。

## 任务与判分

- 模型输出 Manim 代码 → 渲染 → 裁判按 8 维 0-5 打分（正确完整性、逻辑连贯、易懂性/教学效果等 4 个文本维 + 4 个视觉维）；单题总分是 8 维**几何平均**；渲染失败按失败计。
- **本地裁判是替代品**：论文用 Gemini 3.0 Pro，本地用 MiniMax-M3 —— **分数只能内部比较，不可对外与论文对照**（此 caveat 已写入 summary.json 和 HTML）。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：8-dim 0-5 visual explanation score 格在当前面板 n=6、均分 5.673、SD=2.397，未触发 ceiling 或 low_variance。当前分差较大，但模型数仍少且使用替代裁判，不能把大 SD 直接等同于构念效度。
- 渲染成败混入分数：一部分方差来自"会不会写能跑的 Manim 代码"（工程能力）而非教学可视化能力。
- 当前仍是单源、替代裁判证据；相关能力结论都依赖这一个 benchmark 和本地判分链路，不能仅凭大 SD 宣称构念已经验证。

## 当前映射

- v7 将 8-dim visual explanation score 同时接入 P04 多模态生成与 P17 适配性解释和反馈生成；具体权重以 `data/mapping_measurement_model_v7.json` 为准。
- 生成任务不测 P03 输入感知，也与当前 P10 通用安全无关；旧 P10/P18/P03 编号和“P10 孤证”表述仅属 v6 历史。
