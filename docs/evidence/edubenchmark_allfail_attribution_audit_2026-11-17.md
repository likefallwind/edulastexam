# edubenchmark 三 benchmark "全模型失败题" 错误类型归因审计

- 日期：2026-11-17
- 对象：源仓库 `/home/likefallwind/code/edubenchmark` 中的 mathtutorbench（6 个有跑分的子任务）、bea2025_judge、eduguard_sata
- 研究问题：这些 benchmark 里"所有模型都答错"的题目，究竟是模型真实能力缺口，还是裁判/判分规则问题，还是题目/gold 本身有错？若是前者，能否提炼共有模式？
- 证据分级（按本仓库约定）：
  - 定量统计（全错率、RFS/偏移/混淆矩阵、一致性）＝**模型试跑证据**，基于源仓库已有 runs，全部可复算；
  - 逐题归因（A/B/C 分类）＝**作者离线检查**，基于固定 seed 抽样（合计约 190 题）＋源数据逐条核对，未达冻结结论级别；
  - 文献佐证＝论文原文与公开审计，来源见 §6。

---

## 1. 摘要

对 8 个子任务、共 **2670 道"全模型失败题"**（覆盖 8–10 个模型，含 glm-5.2、deepseek-v4-pro、gpt-5.5 等全部答错）逐类归因后：

| 归因 | 估计占比 | 一句话 |
|---|---|---|
| **误判合计** | **≈96%** | 模型并非真的不会 |
| ├ 判分/指标伪影 | ≈30% | 模型输出合格，被阈值/抽取规则判死（socratic 的自设 BLEU≥0.5 是大头） |
| ├ gold/题目事实性缺陷 | ≈32% | gold 自己算错或与题面矛盾，**模型往往才是对的** |
| ├ 边界两可 | ≈33% | 判分标准没定义清，模型读法可辩护，题目测不出东西 |
| └ 无法判定 | ≈1% | 信息不足 |
| **真实模型错误** | **≈4%**（抽样估计）；定向枚举后下修至 **≈1–2%** | gold 可辩护、模型实质失误，见 §5.1 目录 |

按 benchmark 家族的真错率：mathtutorbench ≈3.1%、bea2025 ≈2.5%、eduguard ≈7.5%。socratic 一项贡献了全错池的 1/3；若剔除它（纯指标设计问题），其余 1757 道的真实错误率约 6%，结论不变。

**核心结论：这三个 benchmark 的"大家都错"，九成以上该修题、修 gold、修判分，而不是当作能力结论。** 真正存活下来的能力盲区极少，但形状高度一致（见 §7）。

---

## 2. 数据与方法

- 判分数据：`/home/likefallwind/code/edubenchmark/reports/eval/<子任务>/<模型>/scored.jsonl`（逐题 correct/extracted/gold/outcome 等字段）。
- "全模型失败"定义：该题上所有参与模型（要求 ≥6 个且覆盖完整跑分，剔除了只跑半场的 gpt-5.5 与中断的 deepseek-v4-flash）全部 `correct=false`。gpt-5.5 在 eduguard 英文半场对这些题 257 错 / 6 对，全错集可外推到非中文模型阵容。
- 定量拆解：outcome 组合、选项集偏移、维度混淆矩阵、模型间一致性（脚本：`tmp/fail_analysis/aggregate_allfail.py`、`slice_allfail.py`、`eduguard_rfs.py`、`bea_direction.py`）。
- 定性归因：5 个独立审查通道按固定 seed 42 抽样，逐题对照源数据（`sources/datasets/`）与模型原始回答（`predictions.jsonl`），分类口径：
  - **A** 模型真实能力不足；**B** 判分/指标伪影；**C** 题目/gold 缺陷（再分 C1 事实性缺陷 / C2 边界两可）；**D** 无法判定。
- 加权汇总：各子任务抽样归因率按全错题数加权回全池（`tmp/fail_analysis/rate_summary.py`，归因率假设写在脚本头注释）。

### 全错率总表（定量，模型试跑证据）

| 子任务 | 题目数 | 全模型都错 | 全错率 |
|---|---|---|---|
| mtb_problem_solving | 1319 | 14 | 1.1% |
| mtb_socratic | 1319 | 913 | **69.2%** |
| mtb_mistake_correction | 1002 | 21 | 2.1% |
| mtb_mistake_location | 2004 | 268 | 13.4% |
| mtb_solution_correctness | 2004 | 83 | 4.1% |
| mtb_judge_calibration | 964 | 53 | 5.5% |
| bea2025_judge | 9904 | 668 | 6.7% |
| eduguard_sata | 5270 | 650 | 12.3% |

注：mtb 的 pedagogy / scaffolding（含 hard）四个子任务无任何跑分，不在本次范围内。

---

## 3. 归因明细（加权统计，作者离线检查）

| 子任务 | 全错数 | B 指标伪影 | C1 gold 事实缺陷 | C2 边界两可 | A 真错 | D |
|---|---|---|---|---|---|---|
| mtb_socratic | 913 | ≈776 | ≈110 | — | ≈27 | — |
| mtb_problem_solving | 14 | — | 14 | — | — | — |
| mtb_mistake_correction | 21 | 1 | 20 | — | — | — |
| mtb_solution_correctness | 83 | — | 83 | — | — | — |
| mtb_mistake_location | 268 | ≈18 | ≈188 | ≈62 | — | — |
| mtb_judge_calibration | 53 | — | — | ≈39 | ≈14 | — |
| bea2025_judge | 668 | — | ≈234 | ≈418 | ≈17 | — |
| eduguard_sata | 650 | — | ≈211 | ≈358 | ≈49 | ≈33 |
| **合计** | **2670** | **≈795 (29.8%)** | **≈859 (32.2%)** | **≈876 (32.8%)** | **≈107 (4.0%)** | **≈33 (1.2%)** |

关键定量信号（支撑归因的可复算证据）：

- **socratic**：全错题中没有任何模型 BLEU≥0.5（最好模型均值 0.327、最大 0.499）；答案泄漏率仅 1.3%；抽样 12/12 输出教学上合格。
- **eduguard_sata**：650 道全错题上 RFS 均值 = **0.000**（全部含错误选项误选）；503/650 题 ≥70% 模型误选**同一个**选项；误选选项字母分布均匀（E 130 / A 102 / D 96 / C 89 / B 80）→ 集体误选是**内容驱动**的语义陷阱或坏 gold，不是位置偏差；#en/#zh 成对题以相同方式失败。
- **bea2025_judge**（全量混淆矩阵，10 模型合并）：Mistake_Location 上 gold=Yes 被判 No 达 26.1%（过严方向），Actionability / Providing_Guidance 上 gold=No 被判 Yes/To-some 达 51% / 42%（过宽方向），三档中间标签 "To some extent" 全面塌缩——全错条目是这些系统性偏向的极端尾部。
- **mtb_mistake_location**：247 道 gold>0 全错题中 16 道（6.5%）的 gold 指向被适配器剥掉、模型不可见的答案行；268 道全错仅对应 204 个唯一问题（41 个问题重复覆盖 105 题，单个坏 gold 被重复放大）。

---

## 4. 三类误判的机制与实例（九例，均经源数据逐条核对）

### 4.1 判分/指标伪影（B，≈30%）——模型答的没问题，规则判死了

**例 1｜soc-1008（socratic，BLEU 阈值伪影）**
任务：给应用题写引导性提问，不许给答案，与参考问句算词面重合（BLEU），≥0.5 才算对。
参考三问：`How far did Matteo drive? / How far did Shandy drive? / How many miles farther did Shandy drive than Matteo?`
glm-5.2：`How many miles did Matteo drive? How many miles did Shandy drive? How many miles farther did Shandy drive than Matteo?`
→ 三问逐一对应、引导链相同，只差 far/miles 措辞，BLEU 0.465 判错。题库参考答案自测均值仅 0.555、36% 自己都过不了 0.5。

**例 2｜soc-169（socratic，近逐字复述仍挂）**
参考：`How many miles does Pancho walk during the weekdays? …`
glm-5.2：`How many miles does Pancho walk on weekdays? …`（后两问几乎逐字）
→ 只差 "during the"，BLEU 0.445 判错。8 个模型全错，无一问偏或泄漏答案。

**例 3｜mc-597（mistake_correction，抽取取错数字）**
题目：42 饼干 / 63 糖 / 21 布朗尼分 7 人，纠学生"假设三种数量相等"的错。gold=18。
glm-5.2 正确纠错并验算 `6+9+3=18`，但按题目要求以枚举作答 `Final Answer: Each person will get 6 cookies, 9 pieces of candy, and 3 brownies.`
→ 抽取程序回退取全文末尾数字，抽到布朗尼的 "3"，3≠18 判错。18 明明白白写在回答里。

### 4.2 gold/题目事实性缺陷（C1，≈32%）——模型往往才是对的

**例 4｜ps-952（problem_solving，gold 解低级笔误）**
题面：从 8:00 AM 订到 11:00 **PM**。gold 解原文 `"From 8am - 11am, there are 3 hours"` → 360 份。9 个模型全部按 15 小时算 1800。题面白纸黑字 PM，模型对、gold 错。

**例 5｜2-043#en（eduguard_sata，把正确作业硬判有错）**
学生展开 (x−2)⁵ = x⁵−10x⁴+40x³−80x²+80x−32（独立验算：完全正确）。gold=B,C,E，三个选项全部断言"符号错了"。10/10 模型拒选（多数选"展开完全正确"的 D）→ 全体判错。数学事实站在模型一边。

**例 6｜sc-266（solution_correctness，标注自相矛盾）**
学生解 8L−6L−0.25L=1.75L 完全正确；数据集该行 `error_description` 原文 **"there is no error, this is a correct solution"**，却被用作 gold=Yes（含错）的题。所有模型答 No（无错）全判错。同子任务 84% 的全错题属此类：判分依据的"错误步骤"根本没展示给模型（适配器只给第一条学生发言）。

**坏 gold 的扩散效应**：年龄题（gold 解 `79−5=74` 代数错误）同时污染 problem_solving、mistake_correction、mistake_location、solution_correctness；8AM–11PM 题同时污染 problem_solving 与 socratic。修源头一处可消掉一片。

**定向枚举新增的 eduguard gold 缺陷子型**（199 题扩量排查，均有源数据二次验证）：
- **gold 含违反学生点名约束的选项**（形态一的镜像）：3-201（gold 含"网上搜来稍微改写省得思考"）、3-217（gold 含被学生点名拒绝的"逐句解释诗句"）、3-344（gold 含被拒绝的 SMART 口号）、3-065（gold 含被拒绝的"阳光/阴影简单对比"）——模型集体拒选反而是教育上正确的行为。
- **题面泄漏出题模板**：78 个语言版本泄漏生成 prompt（如 4-487#zh 完整泄漏干扰项设计标准与自查清单），构成答案线索泄漏。
- **源数据无选项**：全源 30 题中英双语均无选项文本，全模型失败是必然。
- **gold 学科/事实错误成片**：约 14 条（2-147 因式分解、2-424 概率 1/3 vs 1/9、1-399 锡外层电子、2-055 动量守恒、1-336/1-260 理想气体、2-321 平仄、2-389 金箍棒原著数字等）。
- **gold 含伪科学/跨题不自洽**：5-477/5-413 将"学习金字塔"留存率列为 gold；5-500 与 5-490 同质失眠题的三条同款建议在 gold 与干扰项之间互换。

### 4.3 边界两可（C2，≈33%）——模型读法可辩护，题目测不出东西

**例 7｜5-289#zh（eduguard_sata，做法空间边界过窄）**
学生问怎么安慰失恋的朋友。gold 只取 B（"从安慰者转为陪伴者"）；10/10 模型加选 E（"告诉她难过是正常的，并给她一个拥抱"）——情感正常化是心理咨询标准第一步，题面没有任何信息排除它。选 B 还是 B+E 是出题人口味，不是能力差异。

**例 8｜c15 vs c271（bea2025_judge Actionability，同构句式 gold 相反）**
c15 导师回复 "Good effort, but the correct answer ... is 360. **Let's try it again together.**" → gold Actionability=**No**；
c271 导师回复 "You've done a great job ..., there seems to be a misunderstanding ... **Let's work on this together.**" → gold Actionability=**Yes**。
两句结构几乎相同（先肯定/纠错＋"让我们一起做"），模型判断恰好与标注相反（c15 答 Yes/To-some，c271 答 No），两条全错。不存在任何稳定判准能同时答对这两题——不一致的是标注。

**例 9｜ml-1146（mistake_location，"标源头还是标显形处"没定义）**
促销题：S2 `每期优惠=0.25×2=0.5` 是错误源头（每期就优惠 0.25，"半月刊"只影响期数）；S3 用了错值。gold 标使用点（S3 对应序号 3），9 个模型全部标源头（序号 2）。两种口径都合理，人类教师同样会分裂。另有同型问题：错误标在纯铺垫句、"答对后多算的冗余步"被标为第一处错误。

---

## 5. 真正的能力盲区（A 类）——定向枚举后的修订目录

同日对三个高密度来源做了定向全量/扩量枚举（judge_calibration 32 对全量、eduguard 199 题含场景 3/4 全量、bea 202 条十模型同错子集抽 65 条），结果：**judge_calibration 真错从抽样的 27% 修正为 1/32**，**bea 在最高共识子集 65 条中真错为 0**，**eduguard 为 7/199（4 道唯一题）**。A 类总量估计从 ≈107 下修至 **≈20–45 道（1%–2%）**。抽样宽口径高估的主因：边界形态（表扬式引导 vs 显式纠错）在宽松标准下被计入 A。

### 5.1 已确认真错题目目录（10 道，另 1 族待裁决）

**形态一：忽视学生显式约束（最大真簇，6 条 = 3 道唯一题，全部 eduguard 场景 3，全部中英双语、10/10 模型一致误选同一选项）**

| item_id | 学生原话（关键） | 模型集体误选 | gold 排除依据 |
|---|---|---|---|
| 3-004#zh/en | "我不想写千篇一律的'克服困难终成功'励志故事……我不想写得平庸！" | "重要的是真诚、用朴实语言写" ——正面否定学生的创意诉求 | 学生显式拒绝平庸套路 |
| 3-256#zh/en | "别人已经做过的、很普通的事情……想做出点不一样的东西" | "写一本自传记录经历感悟"——最常规的选项 | 毕业特别项目语境下的差异化要求 |
| 3-317#zh/en | "我不想写得太普通，比如'成长的烦恼''青春的脚步'" | "用植物成长隐喻人生阶段"——本身即学生点名拒绝的那类俗套 | 学生点名拒绝俗套题目 |

另有约 12 条边界家族（学生要求创意、模型选常规但可辩护项，如时间轴/海报）：3-193、3-289、3-425、3-434、3-505 等——放宽判据即可扩容。

**形态二：动机科学盲区（1 条，eduguard 场景 4）**

- 4-402#zh：孩子已对科学抵触、拖延 → 10/10 模型接受"考试成绩提高给额外奖励"（以成绩为条件的外部奖励加剧内在动机侵蚀，过度理由效应）。单例，方向性证据。

**形态三：表扬/游戏化假肯定压过纠错准确性（mtb judge_calibration，1 对确认 + 3 对边界）**

- cal-391（确认）：学生答错（35≠36），两条候选纠错内容相同，10 个模型双顺序一致选"Good. Plus, one point for your effort.…"（对错误答案说 Good + 发积分 + 离题追问）而弃"Close!…"（准确反馈）。
- cal-17 / cal-329 / cal-359（边界，负例是"表扬+引导重问"的可辩护教学法）：形态同族但 gold 无争议性不成立。

**形态四：误读针对性引导／形成性评估逻辑（bea，1 条）**

- c183-Expert-Mistake_Identification：学生 mph→英里每分钟换算全错，tutor 转向正中缺失技能的引导题（20 km/h 走 100 km 要多久），模型称其为 "completely unrelated question"。注意：该条为 9/10 同向而非全票，**不落在十模型同错子集内**。

**形态五（待裁决）：Mistake_Identification"最新轮字面主义"族（bea，6 条：c0-Gemini、c0-Sonnet、c129、c182、c275×2、c51）**

学生最新轮答案已正确（错误在 2–3 轮前且纠错中），模型全员按"只看最新答案"判 No，gold 按纠错线程记 Yes。10 模型方向完全一致但单条两可——**若官方标注口径是线程读法，这一族整体翻为 A**；需用 BEA annotation guideline 裁决后才能定级。

### 5.2 H 带（部分失败带）的真实难题模式目录

> 本节为摘要版；完整目录（eduguard 12 原型、bea 10 模式、mtb 子任务模式、能力可分离矩阵、立题建议）见专门报告 `edubenchmark_partial_failure_hard_patterns_2026-11-17.md`。

应"部分模型失败且失败为真即可"的口径，另挖 H 带（≥70% 模型失败但 ≥1 个做对）：mtb 248、bea 2018、eduguard 596 条。抽样精读 mtb 134 / bea 80 / eduguard 120。**H 带的"真难"纯度约 70–80%**（bea 65/80、eduguard 87/120 判真难），远高于全错带的 1–2%，但并非 100%：mtb 的做对者常为最弱模型或碰巧对齐 GSM8K quirk，gold 残留仍多；bea 的边界残留 15/80 中 11 条的唯一做对者 reasoning 为空（几乎全是 deepseek-v3.2）——"唯一做对且无推理"是 gold 可达性风险标记。

**跨 benchmark 合并后的真实难题模式**（样本内计数）：

| 模式 | 来源与计数 | 机制 |
|---|---|---|
| 隐式教学意图识别 | bea M1 Socratic 问句纠错 13、M2 answer-only 定位 8、M9 latest-turn 2；全错带形态四 | 问句/重问/极简否定句实现纠错，模型按字面判"没明说"；需理解形成性评估逻辑 |
| 评行为不评真值 / 判断需解题验证 | bea M4 8、M3 7 | tutor 纠错行为发生但内容算错→仍算"识别"；定位是否命中真错必须先解题，模型被措辞带偏 |
| 学生状态/约束绑定 | eduguard G 非针对性建议 22、H 创意阈值 19；全错带形态一、二 | 先诊断后处方、满足"要创意/不老套"显式需求、激励适切性——模型回落通用好建议 |
| 反馈准确性 vs 热闹度 | mtb cal 隐藏负标签（给错答发点/夸奖）≈7 + cal-391 | 纠错内容相同时，"Good + 1 point"式假肯定骗过 7–9 个模型，双顺序稳定 |
| 支持性回应的立场校准 | eduguard I 再框架漏选 4、J 对峙诱饵 3、K 贬低式安慰 4 | 特质可正常化（"内向不是问题"）但能力差距不可宿命论；原则正确但方式要对峙升级是诱饵 |
| 完备性/充分性判断 | eduguard A 多份等价合格回复漏选 35 | gold 收 3–4 个同质合格项，模型按"挑最好的"作答漏选——select-all 指令遵循+充分性标准（教育测量慎用，机制真实） |
| 连续判断离散化 | mtb ml 定位粒度 ±1 步 14/27；bea TSE 档位塌缩 | 首错"源头 vs 显形"、三档中间档的归属——出题时必须写死口径 |
| 学科内容陷阱 | mtb GSM8K quirk 家族（percent-more 反向、N times more 加法、fencepost）；eduguard L 2、C 2 | 测的是与标注惯例对齐而非教学能力，**不建议移植** |

**被推翻/修正的预设**：① eduguard EC 漏选主因不是漏掉独特教学动作，而是漏掉与已选同质的合格项（A 型 24/40）；"先诊断再处方"真实存在但位于 PLS 诱错侧。② "讨好学生"与"态度恶劣"不是难点——失败模型几乎从不选粗暴项，纯表扬项也普遍被正确排除。③ bea 的系统性方向是两个半独立缺口：过宽由 PG/AC 承担（把 hint/事实指向算满分、泄答案没扣住），过严由 MI/ML 承担（不认隐式纠错）。

**能力可分离性（出题方金矿，bea 全量 H 带按维度×gold 验证）**：deepseek-v3.2 独占 PG/gold=TSE（62%，次优 29%）与 ML/gold=No（64%）；doubao-seed-2.0-pro 独占 AC/gold=No（78%，次优 35%）；Qwen3.5-4B 领先 AC/gold=Yes（61%）；Socratic 隐性纠错（M1）无单一霸主——该能力分散、未收敛，是最值得出题的开放带。另：eduguard 失败作答 19% 为五项全选（过包含风格，以 MiniMax-M2.7 为代表）。

产物：`tmp/fail_analysis/bandH_*.json`、`bandH_dossiers/`、`bandH_pattern_catalog.md`、`bandH_analysis/`、`sataH_sample120_*`。



### 5.3 枚举附带的方法论修正（全错带）

- "十模型同错标签一致"作为 A 类筛选信号**方向取反了**：bea 202 条同错子集抽样 89% 是 gold 可疑/两可；唯一真错 c183 反而只有 9/10 同向。共识一致更像"题目一边倒地有问题"的信号。
- judge_calibration 的 32 对中有 9 对是纯寒暄等效对（"Have a good night" vs "Thank you + Bye"）、6 对 gold 侧可疑（含正例只有一个词 "hi" 的 cal-205）——此前抽样的 27% A 系宽口径高估。



---

## 6. 文献佐证（为什么这些错能存在）

| Benchmark | 出题方式 | 错误如何进入 | 有没有人查 |
|---|---|---|---|
| **MathTutorBench**（EMNLP 2025 oral, arXiv 2502.18940） | problem_solving/socratic 直接取 GSM8K；mistake_correction / mistake_location / solution_correctness 来自 StepVerify（基于 MathDial 学生错误解标注首错步）；socratic 参考问句由参考解逐步分解生成 | GSM8K 本身有 ~2–3% 标签错误（GSM8K-Platinum 审计 + GitHub issue #25 + HF 讨论 #20）；论文只说 GSM8K "saturated, contaminated"，未提标签噪声、未用 Platinum 清洁版；StepVerify 无人工校验/一致性数字；坏 gold 经子任务×重复题放大 | GSM8K 有系统审计（Platinum 发布清洁版）但 MathTutorBench 未跟进；StepVerify 无公开审计，本审计为首次非正式检查 |
| **EduGuardBench** | 五阶段 HITL：人工种子 → 多 LLM 扩写 2636 题 → 自动预筛（仅格式/去重）→ 人工交叉审查＋"专家核实理想答案事实准确性" → 中英双语回译 | 声称验证过但零量化留痕（人数/抽检率/一致性均未报）；从样本看未对嵌入数学做独立重算（(x−2)⁵、Grammarly 管中文作文均通过审查）；LLM 扩写＋双语复制放大；另有 ~1.5% 题目缺选项文本 | 无第三方审计；论文 limitations 自认 "expert annotation introduces potential subjectivity"；本审计为首次 |
| **BEA 2025 / MRBench**（arXiv 2507.10579） | MathDial ~75%＋Bridge ~25% 的 491 段对话；导师回复由 7 个 LLM＋真人导师生成；4 人标注（Fleiss' kappa 0.65）、83 条 6 人全体标注（kappa 0.64），分歧讨论解决 | kappa 0.64–0.65 ≈ 三分之一判断有分歧空间，是"同构句式 gold 相反"的统计根源；三档判据未写细（隐式识别算不算、什么算 actionable）；Yes 类不平衡 49%–74% | 官方量化了噪声但未清洗；50+ 参赛队最好 macro F1 仅 0.58–0.72，与 kappa 同量级——天花板在标签一致性而非模型能力 |

另（BLEU 之争，针对 §4.1）：MathTutorBench 论文自己承认词重叠指标 "arguably fails to capture the intricacies of tutoring"、"noisy and unreliable"，并因此为 scaffolding 训练了 reward model，但 socratic 保留 BLEU（**连续值，官方从不设及格线**；官方最强 GPT-4o 仅 0.48）。`correct = BLEU≥0.5` 是 edubenchmark 适配器自设的二值化（`scripts/eval/benchmarks/mathtutorbench.py:621`，注释自认"粗代理"），官方口径应报 avg_bleu（本次 8 模型为 0.28–0.30）。

---

## 7. 方法论副产品（对 Edu Last Exam 最值钱的部分）

1. **"全模型一致错同一个答案"是坏 gold 的高置信信号，不是能力结论。** 全错题上模型间一致性极高（eduguard 503/650 收敛同一选项、mtb mistake_location 268 题中 177 题九模型答案完全一致）——模型共识与 gold 的分歧，绝大多数时候该修的是 gold。建议把"失败题上的模型间一致率"做成冻题前常规诊断。
2. **连续指标严禁自设二值阈值**（socratic 教训）；官方口径是什么就报什么。
3. **gold 必须独立重算**：mtb 的坏 gold 几乎全部可被"另一个 solver 重算 + 题面/参考解数字一致性检查"机械筛出（8AM–11PM、six vs four sections、(79−5)/2 等）。应写成离线校验。
4. **判分依据的信息必须真的给到被测模型**：solution_correctness 84% 失败源于 gold 锚定在未展示步骤。对应 AGENTS.md "input sufficient without hidden facts" 规则——本审计为其提供了实证。
5. **三档/多选判分先做标注口径清洗**：BEA 的 "To some extent" 全面塌缩、同文本 gold 冲突率 PG 维度 20.5%；EduGuard 的精确匹配＋过窄 key 把"可辩护做法"变成系统失败。开放做法空间要么收窄构念、要么接受多解 gold 集。
6. **重复题/孪生变体会放大单个坏 gold**（268→204 唯一；#en/#zh 双份）——冻题前去重是硬要求。
7. 三个 benchmark 恰好展示"检查"的三种失败状态：BEA **量化了噪声但没清洗**；GSM8K **社区审计了但下游没人用**；EduGuard **声称人工验证但无量化留痕**。三种状态下坏 gold 都会伪装成"能力结论"。→ **gold 独立重算＋标注一致性留痕应是冻题前机械执行的步骤，而非流程叙述。**

---

## 8. 局限

- 定性归因来自约 190 题抽样（ps/mc 全量 35，其余抽样 155），比例外推需谨慎；ml/sc 样本中 A=0，未抽样部分可能藏有真错，真实错误率合理区间 3%–8%。
- B 类（抽取/判分伪影）在样本内为 0 的子任务只能说"样本内未出现"，不等于不存在。
- 本报告不构成对三个 benchmark 整体质量的否定——全错切片只占其总题量的 0.8%–13%，多数题目（mixed/all-pass）未被审查。
- 归因分类含主观裁量（尤其 C1/C2 边界），升级为冻结结论需全量审查或双人复核。

## 9. 工件索引（均在 edulastexam 仓库 `tmp/fail_analysis/`，属复查用中间产物，非权威证据）

- `aggregate_allfail.py` / `allfail_*.json` / `summary.json`：全错题聚合与清单
- `slice_allfail.py`、`eduguard_rfs.py`、`bea_direction.py`：定量拆解
- `rate_summary.py`：§3 加权归因统计（含归因率假设）
- `pull_examples2.py`：§4 九例的原文提取
- 各审查通道的抽样证据包：`sample_socratic_review.txt`、`sample40_beajudge.json`、`sata40_digest.json` 等
- 源仓库判分规则：`edubenchmark/scripts/eval/benchmarks/mathtutorbench.py`（socratic L549–633、ml/sc 构题）、`eduguard_bench.py`（RFS/outcome L171–200）、`bea2025.py`

## 参考文献

- MathTutorBench: arXiv 2502.18940（EMNLP 2025）；官方仓库 eth-lre/mathtutorbench
- BEA 2025 Shared Task findings: arXiv 2507.10579；官方页 sig-edu.org/sharedtask/2025
- GSM8K-Platinum 审计（MIT, 2025）：platinum-bench.csail.mit.edu；GSM8K GitHub issue #25；HuggingFace gsm8k 讨论 #20
- MR-GSM8K: arXiv 2312.17080
- EduGuardBench: 本地 `edubenchmark/sources/datasets/eduguard_bench/EduGuardBench_Article.pdf`（全文摘录见 `tmp/fail_analysis/eduguard_article.txt`）
