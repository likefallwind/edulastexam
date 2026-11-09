# IFEval

**一句话**：通过可自动检查的字数、格式和关键词约束，评估模型是否完整遵循指令。

## 公开介绍

<!-- public-profile:start -->
```json
{
  "overview": [
    "每条请求包含一个或多个可验证要求，例如不用逗号、满足字数下限或保留指定格式。",
    "主要指标是 prompt 级严格通过率：同一条请求中的全部要求都满足才算通过。判分直接检查原始回复。"
  ],
  "facts": [
    {
      "label": "数据规模",
      "value": "541 条请求"
    },
    {
      "label": "语言与形式",
      "value": "英文；文本生成"
    },
    {
      "label": "判分",
      "value": "官方规则检查；同时报告严格与宽松口径"
    }
  ],
  "credits": [
    {
      "text": "Zhou 等 / Google Research，2023",
      "url": "https://github.com/google-research/google-research/tree/master/instruction_following_eval"
    },
    {
      "text": "题例数据：CC BY 4.0（Google Research 数据许可）",
      "url": "https://creativecommons.org/licenses/by/4.0/"
    },
    {
      "text": "论文：Instruction-Following Evaluation for Large Language Models（2023）",
      "url": "https://arxiv.org/abs/2311.07911"
    }
  ]
}
```
<!-- public-profile:end -->


## 出处与背景

- Zhou et al. 2023, *Instruction-Following Evaluation for Large Language Models*（arXiv:2311.07911），google-research 官方实现，Apache-2.0。
- 接入动机（R13/R14）：edubench 裁判打的"指令遵循"分与知识指标在模型排名上信息重合（同源模型级 ρ≈0.96），且换裁判后不稳健——P01 的直接测量必须走规则判分。

## 数据

- `fetch_eval_datasets.py --benchmark ifeval` → `sources/datasets/ifeval/data/input_data.jsonl`（541 条）+ 官方 checker 四个模块 vendored 到 `sources/datasets/ifeval/instruction_following_eval/`。
- 判分依赖 nltk / langdetect / immutabledict / absl-py（miniconda python 已装；fetch 时自动下 nltk punkt）。

## 任务与判分

- 每条 prompt 带 `instruction_id_list` + `kwargs`（约 25 种指令类型）；无裁判、无抽取 LLM，直接对原始回复跑官方检查。
- headline = 官方 **prompt 级 strict accuracy**（一条 prompt 的全部指令在原始回复上全部满足）；`extra_metrics` 含 prompt-loose / instruction-strict / instruction-loose（loose 按官方 8 变体重试：去首行/尾行/去 `*`）。

## 在本仓库怎么用

```bash
/home/likefallwind/miniconda3/bin/python scripts/eval/data/fetch_eval_datasets.py --benchmark ifeval   # 一次性
MODEL=MiniMax-M3 ./scripts/run_eval.sh ifeval        # 全量 541 题，无 API 判分成本（只有答题成本）
```

## 局限与注意

- 通用指令、英文为主，不是教育语境——按 foundation_gate 挂 P01，作操作基座门槛证据，不宣称教育指令遵循。
- 部分指令（如"重复请求原文"）会让回复看起来像回显题面，是正常现象。

## 当前映射

- ifeval：P01 1.00，foundation_gate，weight 0.80；测量模型 P01/core 格子 weight 1.0（此前 P01 全是搭车格子）。
- 2026-07-12 全量（MiniMax-M3, 541 题）：prompt-strict **0.874** / prompt-loose 0.911 / instruction-strict 0.915 / instruction-loose 0.940。该单模型点位不能判断跨模型区分度。**13 号实测（v7/R28，分析日 2026-11-02）**：prompt-level strict accuracy 在当前面板 n=8、均分 9.045、SD=0.312，标记 ceiling + low_variance，取代旧“无天花板迹象”的推断。
- 踩坑记录：run_eval.sh 启动时 `PATH=/home/likefallwind/miniconda3/bin:$PATH` 前缀必须放在 nohup/bash -c **里面**，否则 python 解析到默认 venv、缺 absl/nltk 直接崩（7-12 首跑即此故障）。
