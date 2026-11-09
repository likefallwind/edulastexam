# MMTutorBench

**一句话**：根据教学视频关键帧与学生问题生成有针对性的数学辅导回复。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "输入包含历史关键帧、当前画面和学生提问，回复需说明理解、操作规划和执行。",
    "固定裁判按六个二元维度检查辅导质量；公开数据缺少逐条人类评分锚点。"
  ],
  "facts": [
    {
      "label": "数据规模",
      "value": "770 条样本；1,414 张关键帧"
    },
    {
      "label": "语言与形式",
      "value": "英文；视频关键帧与文本"
    },
    {
      "label": "判分",
      "value": "六维 rubric；0–6 分及论文等权口径"
    }
  ],
  "credits": [
    {
      "text": "MMTutorBench 作者团队，2025",
      "url": "https://huggingface.co/datasets/Tangchiu/mmtutorbench"
    }
  ],
  "family_id": "mmtutorbench",
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- HF `Tangchiu/mmtutorbench`，2025。
- 动机：真实辅导常发生在"学生看着题/看着讲解卡住了"的多模态语境，考察模型能否基于视觉上下文做辅导（而非只看文字）。

## 数据

- 770 条 JSONL 样本、1,414 张关键帧图片。英文。
- 获取：`fetch_eval_datasets.py --benchmark mmtutorbench`（JSONL + 关键帧 + `data_manifest.json`）。

## 任务与判分

- 输入：历史关键帧 + 当前帧 + 学生提问；要求回复分三段：Insight Discovery / Operation Formulation / Operation Execution。
- 固定 rubric 裁判（`MMTUTORBENCH_JUDGE_MODEL`，默认 MiniMax-M3）按 6 个二元维度判分：insight_identification、operation_prescription、operation_execution、solution_scope_control、brevity、coherence；报告 0-6 总分 + 论文等权分。
- **mmtutorbench_judge_calibration 只是占位**：公开数据没有逐条人类金标，无法做裁判校准（输出状态而非编造校准）。

## 在本仓库怎么用

- 首次冒烟：`LIMIT=5 MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh mmtutorbench`；不要默认跑全量 770。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：multimodal tutor score 格在当前面板 n=5、均分 6.724、SD=0.789，未触发 ceiling 或 low_variance。旧的 n=1、默认排除状态已过时；但相关配对样本仍少、置信区间宽，不能把小面板上的方差直接当作稳定构念证据。
- 无人类金标 → 裁判分数完全没有外部锚点，只能做模型间相对比较。
- 三段式格式要求让分数混入格式遵循成分。

## 当前映射

- P18 0.40 / P03 0.30 / P17 0.30；diagnostic。
- 构念核对：P03 归"教学场景图文理解"（R5）；P17 归"对话辅导"侧（R4）。
