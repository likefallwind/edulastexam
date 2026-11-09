# LongTutor · 长历史教学动作

**一句话**：利用学生长学习历史选择并生成合适的下一步教学动作。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "基于离线历史材料观察模型是否利用已发生的学习信息；三项任务共享数据背景但分别评分。",
    "该评测不直接测量真实学生的长期学习增益。调用与判分协议已对齐上游官方评测脚本，裁判模型仍为本地面板，成绩不等同于论文榜单。"
  ],
  "facts": [
    {
      "label": "数据范围",
      "value": "1,000 个带人类金标的历史样本"
    },
    {
      "label": "判分",
      "value": "官方盲评 rubric 五维（含总分）分别报告"
    }
  ],
  "credits": [
    {
      "text": "LongTutor 作者团队，ACL 2026",
      "url": "https://github.com/liano3/LongTutor"
    }
  ],
  "family_id": "longtutor",
  "example_note": "本页仅提供原始来源入口，不再分发 LongTutor 题目。"
}
```
<!-- public-profile:end -->


## 这是哪个子评测

- 家族 LongTutor 面向长程辅导场景，本仓库实现了三个子评测：证据定位、学生状态诊断、以及本页的教学动作选择。
- 三者是一条链的三个环节，本页是终点：前两步做对了，这一步才谈得上做对。
- 与其他辅导类评测的区别是上下文长度——同样是选下一步教学动作，这里的模型必须先消化一段很长的历史。

## 出处与背景

- 官方仓库只提供 pipeline 脚本，本仓库自行移植为可复现的 adapter，绝对分不与原论文对照。
- **协议对齐（2026-11-06）**：预测端复刻官方 `eval_ai_tutor.py` 发布版默认配置（合并 JSON 调用，本子评测取 `content` 字段，采样温度 0）；判分端换用官方 `_grade_content_with_gpt` 盲评裁判——只给裁判 GOLD 参考教学文与 MODEL 回复，五维 1-5 分（History Utilization / Strategy Alignment / Coherence / **Comprehension & Difficulty** / **Overall**），空回复按官方记全 1。旧协议的自制裁判会把 gold 诊断/策略/上下文一并给裁判并只打四维，分数与官方不同尺度。

## 任务与判分

- 五维 rubric 分别报告，含 overall 总分。
- History Utilization 是这个子评测的特色维度——很多模型在长历史条件下会退化成忽略历史、按通用套路回复。

## 局限与注意

- **区分度（13 号，v7/R28，分析日 2026-11-02）**：judge dims: strategy_alignment + history_utilization (1-5) 在当前面板 n=8、均分 6.186、SD=1.282，范围 3.599–7.681，未触发 ceiling 或 low_variance。该面板上有模型间差异，但不据此消除下面的构念可比性问题。**注：该面板数字产生于协议对齐之前的旧自制裁判。**
- 调用与判分协议已对齐官方发布版脚本；剩余差异是裁判模型替换（本地面板 vs 官方 GPT-5），在教学策略执行上仍只作弱信号计入。
- 长历史条件下的教学动作与短对话条件下的教学动作是否同一构念，目前没有实证检验。把它和其他辅导类证据放进同一层，是一个尚未验证的假设。
