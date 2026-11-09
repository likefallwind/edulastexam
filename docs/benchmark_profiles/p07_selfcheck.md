# 两轮自查

**一句话**：在没有外部反馈的情况下，让模型检查并修正自己的上一轮解答。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "模型先答题，再接收固定复查请求；两轮答案均使用同一规则判分。",
    "分别观察原本答错后改对的比例，以及原本答对却改错的比例。"
  ],
  "facts": [
    {
      "label": "固定题单",
      "value": "550 题；与置信度校准共用题单"
    },
    {
      "label": "题源",
      "value": "C-Eval、MMLU-Pro、AGIEval、GSM8K"
    },
    {
      "label": "协议",
      "value": "两轮；无外部正确性反馈"
    }
  ],
  "credits": [
    {
      "text": "Edu Benchmark 维护者，2026",
      "url": "https://github.com/likefallwind/edubenchmark/blob/codex/scenario-capability-benchmark/doc/benchmark_profiles/p07_selfcheck.md"
    }
  ],
  "family_id": "selfcheck_calibration",
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- 本仓库自建（2026-07-12，缺口推荐文档优先级第 2 项）；协议是学术界 intrinsic self-correction 评测的标准做法（无外部反馈、不暗示对错）。
- 动机：构念核对（R9）发现 P07 此前全是搭车格子——分数看着有，实际没有任何测验直接考"自查"这个行为。

## 数据

- 零新增标注：复用 P08 的 delegate（ceval 0-shot / mmlu_pro / agieval / mtb_problem_solving）和**同一份**难度分层 item_list（`data/p08_calibration/item_list_v1.txt`，550 题），P07/P08 同题可比。

## 任务与判分

- 第一轮：delegate 原生出题（prediction 阶段）；第二轮：extract 阶段把原对话 + 模型自己的第一轮回答 + 固定复查指令再发给**被测模型本身**（harness 会把被测模型名写进 `adapter.model_under_test`；传给 extract 的 client 是抽取模型，不是被测模型）。
- 两轮答案都用 delegate 自己的抽取和判分。headline `score_10 = 10×[0.5×改对率 + 0.5×(1−改错率)]`，两项都以第一轮状态为条件，构造上与第一轮正确率解耦。`extra_metrics` 含 r1/r2 accuracy、net_gain、change_rate、逐来源分解。
- **解析修复（2026-11-07）**：AGIEval／C-EVAL 单选答案按明确答案标记或独立答案行读取，避免把 `answer is correct` 的 c、`CO₂` 的 C 当成选项。P07 缓存版本为 `p07-choice-boundaries-v2-20261107`；已有结果用 `scripts/rescore_cached_run.py --reextract-cached` 直接读取保存的两轮回复重算，不重新生成第二轮。缺失第二轮继续标记缺失，评分公式不变。

## 在本仓库怎么用

```bash
MODEL=MiniMax-M3 ./scripts/run_eval.sh p07_selfcheck    # 默认走 item_list（550 题 × 2 轮）
```

## 为什么不能复用以前跑过的预测

以前各 benchmark 的全量预测只有"第一轮答案"，而 P07 测的是**第二轮行为**——模型看到自己的第一轮回答后改不改、改对还是改错。第二轮必须以第一轮的原始回复作为对话历史现场再调一次被测模型，这个交互在旧预测里不存在，也没法离线补造（换措辞、换上下文都算换协议）。所以旧全量分数只能省下"第一轮"这一半成本吗？也不能：为了保证两轮在同一套 prompt/参数/对话格式下发生，第一轮也要在本协议内重跑，否则改答率会混入格式差异。

## 局限与注意

- 每题两次被测模型调用（round 1 + round 2），成本约是普通跑分的 2 倍。
- "复查"指令措辞固定（中/英各一版）；换措辞就是换协议，对比时注意。
- 已知现象（文献一致）：多数模型 intrinsic self-correction 改对率低、部分模型改错率不低——低分是真实测量结果，不是 bug。

## 当前映射

- v7 将 two-round self-check cell 接入 P07 自我校验与 P08 置信度校准；具体相关度和置信权重分别以 v7 JSON 与聚合元数据为准，旧 0.85/0.15 相关度拆分不再适用。
- **区分度（13 号，v7/R28，分析日 2026-11-02）**：two-round self-check (fix/break rate) 在当前面板 n=8、均分 5.213、SD=0.230，标记 low_variance。2026-07-12 的三题冒烟和“全量跑分随批量启动”仅是历史状态；当前低方差结论属于该面板，不能解释为所有模型都没有自查能力。
