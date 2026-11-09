# TutorBench

**一句话**：以学生真实作业问题与逐题评价标准检验辅导回复质量。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "覆盖文本和图像输入，包括手写作业、图表与截图，并关注解释、反馈和引导等辅导行为。",
    "固定裁判逐条检查人工 rubric；不同子集及缺失样本处理方式需随成绩一起展示。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "约 1,470 条 STEM 辅导样本"
    },
    {
      "label": "覆盖",
      "value": "六类 STEM 学科；文本与图文"
    },
    {
      "label": "判分",
      "value": "逐题 rubric；保留加权通过率与子集口径"
    }
  ],
  "credits": [
    {
      "text": "Scale AI，2025",
      "url": "https://huggingface.co/datasets/ScaleAI/TutorBench"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- Scale AI，2025；https://huggingface.co/datasets/ScaleAI/TutorBench
- 动机：辅导能力评测要贴近真实使用（多模态输入 + 自适应讲解 + 作业反馈 + 主动引导三类任务），rubric 由人工逐题编写。

## 数据

- 约 1,470 条样本，文本+图片（手写作业、图表、截图），6 大 STEM 学科（生物/物理/化学/统计/微积分/计算机）。英文。
- **获取状态：HF gated**（外部依赖与 gated 数据规则见 `AGENTS.md`），本地无原始数据。

## 任务与判分

- 模型生成辅导回复，LLM 裁判逐条判 rubric 通过与否。三个指标：Simple Pass（不加权）、Weighted Positive（critical 条目权重更高）、**Weighted Shifted**（考虑负面 rubric 下界，主排序指标）。
- 本地口径：**Fair815**——815 个公平样本子集，所有模型同分母；缺失/跳过按未通过算（保守）。

## 在本仓库怎么用

- **无 adapter**，分数来自同事报告 `otherbenchmark/tutorbench_0630.MD`（vlm_eval 链路）。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：Fair815 multimodal tutor quality 在当前面板 n=6、均分 5.478、SD=0.250，标记 low_variance。均分不高但该面板上的模型间差异受限；这不外推为未来模型也必然拉不开分。
- 报告自己的 case study 发现：**它强烈奖励"完整、显式、分步骤"的回答风格**——回答简短的模型（如 Qwen3-VL-235B）失分主要因为不够显式，而非看不懂图。也就是说分数里混着可观的"回答风格"方差。
- rubric 判分依赖裁判 LLM；缺失样本处理口径影响绝对分。

## 当前映射

- P18 0.40 / P17 0.35 / P03 0.25；education_core。
- 构念核对：P03 挂载归"教学场景图文理解"子方向（R5）；P17 归 strategy_enactment 的"对话辅导"侧（R4）。
