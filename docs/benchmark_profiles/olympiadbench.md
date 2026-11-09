# OlympiadBench

**一句话**：用奥赛级数学与物理开放题评估复杂推理与精确解题。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "包含中英文数学、物理竞赛题和部分带图题，模型需要自行生成答案。",
    "成绩按学科、语言与题型分别解释；开放题依据答案形式进行规范化与匹配。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "8,476 道数学与物理题"
    },
    {
      "label": "语言与形式",
      "value": "中文、英文；开放题，部分含图"
    },
    {
      "label": "判分",
      "value": "最终答案规范化与等价检查"
    }
  ],
  "credits": [
    {
      "text": "OpenBMB / 清华大学等，2024",
      "url": "https://github.com/OpenBMB/OlympiadBench"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- OpenBMB / 清华，2024（ACL 2024）；https://github.com/OpenBMB/OlympiadBench
- 动机：常规考试题对强模型饱和，用奥赛题（IMO/IPhO 级别）保持区分度，且带完整推理过程标注。

## 数据

- 全集 8,476 题，数学+物理，中英双语，部分带图（多模态）。
- 本仓库只用 **OE（开放式作答）配置**，TP（证明题）配置跳过（无法自动判分）；图片抽取到 `olympiadbench/images/`。
- 获取：`fetch_eval_datasets.py --benchmark olympiadbench`（HF `Hothan/OlympiadBench`）。

## 任务与判分

- 开放式作答，答案是数值/表达式/区间。
- 判分移植官方 repo：`make_prompt` 构造提示，sympy 符号等价的 `AutoScoringJudge` 判对错——**需要 `antlr4-python3-runtime==4.11`**（与 hydra-core 的 4.9 依赖冲突，必要时独立 venv）。

## 在本仓库怎么用

- adapter `scripts/eval/benchmarks/olympiadbench.py`；多模态题需要视觉模型。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：overall/subject/language/modality accuracy 在当前面板 n=7、均分 7.129、SD=0.553；multimodal-subset accuracy n=5、均分 6.859、SD=0.602。两个子维度均未触发 ceiling 或 low_variance，但 n=5–7 的配对置信区间仍宽，旧“共同模型只有 2 个”及“门槛类唯一有潜力”不再作为当前结论。
- 竞赛真题，污染风险存在但比普通考试题低（解题过程难背）。

## 当前映射

- P06 0.55 / P05 0.25 / P03 0.20；foundation_gate。
- 构念核对：P03 挂载属于"解题式图像理解"子方向（R5 拆分后归入该 facet）。
