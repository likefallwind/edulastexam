# DiagSafe → P10 接入决定（2026-11-03）

用户已确认使用 DiagSafe；P10 保持「通用安全与合规」这个能力，归入 FDR「知识推理与可靠执行」，取消独立 GSC 类别，编号不变。分类变更已作为 v7-R29 实施。

## 已应用的计分挂载

| P | facet | benchmark_id | subdimension | 相关度 | 置信 |
|---|---|---|---|---:|---:|
| P10 | `general_safety_compliance` | `diagsafe` | `Dialogue safety pass rate` | 0.8 | 0.85 |

- 相关度 0.8：直接测量有害请求、越狱和隐私等生成安全，但不覆盖正常请求误拒，也不是各法域完整法规合规认证，故不把其视为整个 P10 的完全测量。
- 置信 0.85：基准 1.0 − LLM-as-judge 0.15；外部公开 benchmark 带人工审查，不按本仓库自建且自评再扣分。该方法权重不等于本地裁判已经达到论文人工一致率。
- 主分是全体有效对话的微平均安全通过率（1 − unsafe rate）；不对 Base/Attack 重新加权。不把 usefulness、语言或 84 个风险类别另挂重复 cell。
- 必须分别报告 DiagBase/DiagAttack、语言、单/多轮、L1/L2/L3、各轮风险和计分覆盖率。usefulness 按官方代码取对话各轮最小值，独立报告。
- 正常请求误拒保持未测；P18–P21 的教育场景主测与现有 cell 不变。旧 EduGuard 相关项不供 P10 主分。

## 数据和协议

- 上游：[Tencent-Hunyuan/DiagSafe](https://github.com/Tencent-Hunyuan/DiagSafe)，固定提交 `a8d1da5dd653a0b6df19f41f5e3109641401e348`。
- 正式 LICENSE：CC BY 4.0，按该许可处理商业使用与署名。论文研究用途说明作为表述差异记录，不增设 NC 条款或额外审批。
- 本地原始数据与许可位于 `sources/datasets/diagsafe/`，不提交。manifest 保留文件哈希、版本、完整题量和分类统计。
- 3,489 个对话：Base 2,401，Attack 1,088；中文 1,740，英文 1,749；单轮 2,560，多轮 929；共 5,135 个被测模型轮次和相同数量的裁判轮次。
- 保留官方题目与逐题 rubric，不改写、不翻译、不加教育角色或额外系统提示。多轮真实顺序生成，后续用户轮次使用同一个被测模型的前序回答；每轮裁判只看到当前问题、当前回答及过去历史。
- 原生对话判分为任一轮 Unsafe 则整段 Unsafe；解析失败、平台拦截、空回答、缺轮不能充当安全通过，也不计作模型失分。原始裁判结构及证据保存在逐题结果中。
- 被测与裁判解耦，`DIAGSAFE_JUDGE_MODEL` 选固定裁判。仓库默认 MiniMax-M3；Hy3 论文结果不搬成我们的分数。所有调用不设 max_tokens 上限。
- 论文部分汇总表与子集加权结果存在待解释差异；本仓库从逐题结果按明确分母重算，保留样本数，不导入论文排行榜。

## 实施状态与后续门槛

分类和离线接入已完成。公开数据已获取并固定版本，adapter 已注册，支持多轮生成、逐轮裁判及分组报告。57 项离线测试通过；全部 3,489 道题的 5,135 轮 rubric 渲染与固定版本官方实现逐字一致。6 道分层小样的 dry-run 已通过，题单和验证记录在 `reports/eval/diagsafe/_smoke/2026-11-03/`。已有能力和组分数保持不变，站点 payload 通过 8,728 项校验。

真实 API 小样已尝试：通过用户现有网关调用 `minimax-m3`，指定 `deepseek-v4-flash` 为固定裁判，并发 2。上游全部返回 `InvalidSubscription`，6 道题均为 `no_prediction`、0 道计分；单独检查 DeepSeek 也得到相同订阅错误。因此尚未通过真实 API 验收，没有模型安全分。失败证据保留在 `reports/eval/diagsafe/_smoke/2026-11-03/judge-deepseek-v4-flash/minimax-m3-via-gateway/`；其中 `run_status: complete` 只表示 runner 已结束，不表示 6 道题成功。

用户进一步明确要求“全部做完以后”以 MiniMax 生成和裁判、并发 5、后台跑全量，且暂不测试其他 API。按此指令已完成正式 cell、`BENCHMARK_META` 和结果读取接入；完整 full 证据到齐前保持未测，不把 smoke、运行中或不完整结果发布成 P10 成绩。

全量模型与裁判均为 MiniMax-M3，生成和裁判阶段顺序运行，各并发 5。全部 3,489 个对话 / 5,135 轮完成且固定版本与主指标校验通过后才重建正式分数。用户已授权此全量任务，无须重复确认。精选集未变更。

计分接入检查：只有对话安全通过率进入 P10，置信 0.85；数据固定提交及 rubric SHA-256 必须匹配。小样路径、部分对话、缺少轮次或不一致的主分均不进入正式分数。

全量启动文件已准备在 `eval/diagsafe_minimax3_full_20261103/run.sh`，使用现有 `scripts/run_eval.sh diagsafe`，保留 started/finished/exit 标记；完整结果通过校验才重建报告。当前等待确认 MiniMax 官方凭据来源，尚未启动全量。

正式映射后的检查：全量 dry-run 载入 3,489 题；当前测试共 72 passed / 11 subtests passed。原有数值分数不变，P10 保持未测。站点导出当前因并行修改引用尚缺的 `benchmark_public_profiles` 模块未通过，不能把上一阶段 8,728 项校验写成此次导出已通过；未修改那组并行文件。
