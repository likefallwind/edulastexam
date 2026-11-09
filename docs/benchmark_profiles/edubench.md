# EduBench

**一句话**：用讲解、出题、教学材料与学习支持任务评估教育场景中的生成质量。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "官方设计覆盖九类教育场景，关注知识准确性、教学启发、动机支持和个性化等十二个指标。",
    "当前可比题单包含启发式解答、题目生成、教学材料生成、个性化内容生成和个性化学习支持五类任务。"
  ],
  "facts": [
    {
      "label": "官方规模",
      "value": "4,000 多个场景上下文；九类场景"
    },
    {
      "label": "当前题单",
      "value": "3,797 条英文生成任务"
    },
    {
      "label": "判分",
      "value": "固定 LLM 裁判；十二指标分别报告，0–10 分"
    }
  ],
  "credits": [
    {
      "text": "Yu Bai 等，2025",
      "url": "https://github.com/ybai-nlp/EduBench"
    },
    {
      "text": "Copyright (c) 2025 Yu Bai · MIT 许可",
      "url": "https://github.com/ybai-nlp/EduBench/blob/main/LICENSE"
    },
    {
      "text": "论文：EduBench: A Comprehensive Benchmark Dataset for Evaluating Large Language Models in Diverse Educational Scenarios（2025）",
      "url": "https://arxiv.org/abs/2505.16160"
    }
  ],
  "example_note": "此处展示官方中文题目；当前可比成绩采用英文题单。"
}
```
<!-- public-profile:end -->


## 出处与背景

- Bai 等（ybai-nlp/EduBench），2025；https://github.com/ybai-nlp/EduBench
- 动机：把教育大模型评测从选择题拉到真实生成任务，覆盖 9 大教育场景（作业批改、学习规划、心理健康辅导、学情分析、知识点讲解等）、4,000+ 场景上下文。

## 数据

- 官方发布覆盖 4,000+ 教育场景上下文；论文的人类/模型一致性实验使用 198 条中英 sampled data。
- 本仓库可比题单为 **3,797 条英文有效样本 × 11 个既有模型**，prompt、item_id 与 responses 已规范化到 `reports/eval/edubench/judge-deepseek-v3.2/<model>/`。

## 任务与判分

- 本仓库用到 5 个任务：**IP** 启发式解答 / **PCC** 个性化内容生成 / **PLS** 个性化学习支持 / **QG** 题目生成 / **TMG** 教学材料生成。
- LLM 裁判打分，0-10。**原生维度是 12 个评价指标**：基础事实准确性、领域知识准确性、指令遵循、错误识别与纠正、场景元素整合、内容相关性与范围控制、表达清晰启发性、推理严密性、语气风格一致性、高阶思维培养、动机引导正向反馈、个性化适应学习支持。**本地报告（`otherbenchmark/edubench-0625.md`）第三节有 12 指标的逐模型分数。**

## 在本仓库怎么用

- 原始数据已到位（2026-07-12）：`reports/eval/edubench/judge-deepseek-v3.2/<model>/`，11 模型 × 3,797 题（IP 1253 / QG 1266 / TMG 578 / PLS 448 / PCC 252，**只有这 5 个生成/支持类任务，没有 EC/QA/AG/ES**），逐题 12 指标分，裁判 deepseek-v3.2。导入脚本 `scripts/import_edubench_results.py`（源目录只读）。
- 原生 harness adapter：`scripts/eval/benchmarks/edubench.py`；复用同一 3,797 条 prompt/item_id，默认 MiniMax-M3 固定裁判，输出标准 `predictions.jsonl` / `extractions.jsonl` / `scored.jsonl` / `summary.json` / `report.html`。非 MiniMax-M3 裁判统一隔离到 `judge-<judge>/<model>/`。
- 同事的精确 judge prompt 没有随原始产物交付，官方仓库也未提供可直接执行的完整裁判代码；adapter 的 prompt 依据论文 12 维定义和官方动态指标分配重建。题单与裁判身份可比，但不能宣称是旧协议的逐字节复放。
- 逐题级分析：`scripts/analyze_edubench_item_level.py` → `reports/eval/edubench/_analysis/`；换裁判实验：`scripts/run_edubench_judge_swap.py` → `reports/eval/edubench/_judge_swap/`。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：以下均为当前面板的 0–10 归一分；n 是该格的模型数，不是题目数。
  - **指标格（各 n=7）**：basic_factual_accuracy 均分/SD=8.942/0.363（ceiling + low_variance）、domain_knowledge_accuracy 8.332/0.407（low_variance）、reasoning_process_rigor 8.016/0.438（low_variance）、error_identification_correction_accuracy 7.030/0.274（low_variance）、clarity_concision_inspiration 7.831/0.296（low_variance）、scenario_element_integration 7.755/0.272（low_variance）、higher_order_thinking_ability_development 7.253/0.516（未受限）、motivation_guidance_positive_feedback 6.798/0.361（low_variance）、personalized_adaptation_learning_support 7.087/0.374（low_variance）。九个指标格中只有高阶思维未触发方差受限。
  - **任务×指标格（各 n=7）**：QG × domain_knowledge_accuracy + basic_factual_accuracy 均分/SD=8.768/0.197（ceiling + low_variance）；QG × clarity_concision_inspiration + scenario_element_integration 7.908/0.136（low_variance）；TMG/PCC × clarity_concision_inspiration + scenario_element_integration 8.134/0.408（low_variance）。旧 IP/PCC/PLS/QG/TMG 任务均值不能替代这些当前取数格。
- **家族 halo（同次分析）为 0.575**（家族内 66 对 mean ρ=0.786，跨家族 444 对 mean ρ=0.211），仍触发 halo>0.5 的“家族内先聚合”规则；旧 0.76 不再适用。
- **M2 换裁判实验结论（2026-07-12，250 条 × deepseek-v4-pro + doubao-seed-2.0-pro）**：指标分三类——支持簇（个性化适应 ρ 0.77-0.81、高阶思维 0.63-0.73、动机引导 0.61-0.68）跨裁判稳健是真测量；**错误识别指标是裁判噪声**（三裁判两两 ρ≤0.14、均分 4.6/7.4/8.7 各判各的），不入映射；知识/格式簇被新裁判打到天花板（9.8-10.0）只作门槛参考。对原裁判总分 response 级 ρ=0.43-0.45（含 prompt 差异）。
- 题级两簇结构：基础事实与动机/个性化/高阶思维题级 ρ≈0——同一批回答里"答得准"和"教得好"是独立方向（"会答题≠会教"最硬同源证据）。

## 当前映射与升级方向

- 5 任务分别挂 P17/P18 为主（IP/PLS）、P18/P05/P06（PCC/QG/TMG）、P16（PLS 0.30）；education_core。
- **R1（按 R14 收窄）**：按指标挂 P 限定在裁判稳健的三个指标——个性化适应→P17c、动机引导→P18c、高阶思维→P18/P06；~~错误识别→P11c~~（R14 否决：裁判噪声）；指令遵循不作 P01 直接测量（R13，走 IFEval）；知识指标只作门槛。
