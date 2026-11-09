# EduEquity

**一句话**：保持教育任务不变，仅改变学生身份描述，比较模型是否公平提供支持。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "从 EduBench 五类任务选择身份中立 seed，构造性别、民族、城乡和家庭经济背景四个身份轴的成对请求。",
    "分别比较教学标准、发展机会、支持质量与尊重程度；当前是探索性证据，尚无正式能力计分。"
  ],
  "facts": [
    {
      "label": "数据规模",
      "value": "100 个 seed；400 个反事实 pair；800 条提示"
    },
    {
      "label": "来源任务",
      "value": "IP、QG、TMG、PLS、PCC"
    },
    {
      "label": "判分",
      "value": "成对 LLM 裁判；四维 0–10 分"
    }
  ],
  "credits": [
    {
      "text": "Edu Benchmark 维护者，2026；基础数据 Yu Bai 等 / EduBench，2025",
      "url": "https://github.com/likefallwind/edubenchmark/tree/codex/scenario-capability-benchmark/data/eduequity/"
    }
  ],
  "example_note": "题目示例请参阅下方原始来源。"
}
```
<!-- public-profile:end -->


## 出处与背景

- EduEquity 从 DirectionAI/EduBench 的五类任务 IP、QG、TMG、PLS、PCC 各取 20 个身份中立 seed，共 100 个 seed。
- 每个 seed 注入性别、民族、城乡和家庭经济背景四个身份轴，形成 400 个 A/B 反事实 pair、800 条 prompt；任务、学段、学科、目标、困难和任务相关资源保持不变。
- 它是 P21 的直接相关探索性证据，不是三套新自建安全题集的一部分，不能外推那些题集的人工审核状态。

## 任务与判分

- 每个评分单元由同一 pair 的两次生成组成；A/B 确定性地映射为 X/Y 后交给固定 LLM judge，避免直接暴露方向。
- 裁判按教学标准、发展机会、支持质量、尊重与非刻板印象四个 0–10 维度评分，pair 分为四维均值，越高表示越公平。
- 合理的任务相关个性化不算不公平，A/B 也不要求字面相同；严重身份歧视或机会剥夺可触发 Hard Fail，双方均无效的 pair 不进入均值。
- v7 不给 EduEquity 配置正式计分 cell，P21 当前保持覆盖缺口。

## 在本仓库怎么用

    LIMIT=3 MODEL=glm-5.2 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh eduequity
    MODEL=glm-5.2 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh eduequity

`LIMIT` 的单位是 pair 而非单条 prompt；抽样运行会隔离到 smoke 路径。详细协议见 `doc/eduequity_run_and_evaluation_guide_2026-08-26.md`。

## 局限与注意

- 当前仅用于探索和方法诊断，不发布稳定公平排名，不作为上线门槛、合规证明或真实教育公平效果证据。
- 100 个 seed 的原始筛选脚本、随机种子和完整人工筛选记录未随仓库保存，现有 JSONL 可复核但不能完整重建抽样过程。
- 400 个 pair 都来自“不应有实质差异”的负向预期，没有预注入不公平行为的阳性控制；同一 seed 还跨四个身份轴复用，统计分析不能把 pair 当作完全独立任务。
- 开放生成任务缺少统一 gold 和严格内容质量 rubric；同身份重复生成对照、充分人工校准和裁判重复性证据仍待补。
- 现有裁判选择和生成覆盖会改变结果；部分历史运行未生成完整 800 条回答，解读时必须同时检查覆盖率和 judge 身份。
- 民族、性别等轴的覆盖不能泛化为对整个群体的公平结论。完整问题清单见 `doc/eduequity_problem_status_2026-10-24.md`。
