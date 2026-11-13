# Edu Last Exam V2 原创原型题册

37方向机制驱动数据生成的第一批样本：5个题族、11个依赖版本。V1失败是首批部分题目的历史依据，不是后续造数准入条件。题册不含评分金标，版本不是独立题目数量。

## ELE-V2-01-001 · 非标准正确方法与真正首错

### 版本 equal_time_correct · scripted_dialogue

你是数学作业复核助手。按公开评分规则和当前题面证据评分，用中文给出可核查依据。

题目：一名骑行者连续两段路程各骑行30分钟，第一段速度12 km/h，第二段18 km/h。求全程平均速度。
公开评分规则：每份作品6分，其中题面条件/方法等价关系2分、中间计算2分、最终平均速度数值与单位2分。非标准方法不扣分，但必须在当前条件下等价。
学生K：两段用时相等，所以平均速度=(12+18)/2=15 km/h。
学生L：第一段12×0.5=6 km，第二段18×0.5=9 km；总路程15 km；总时间30+30=60 min=1 h；平均速度15/1=15 km/h。
请逐步核查K/L，给各自分数；若无首错明确说无首错，不要强行挑错。反馈需解释‘当前成立’与‘无条件推广’的区别。

### 版本 equal_time_with_later_error · scripted_dialogue

你是数学作业复核助手。按公开评分规则和当前题面证据评分，用中文给出可核查依据。

题目：一名骑行者连续两段路程各骑行30分钟，第一段速度12 km/h，第二段18 km/h。求全程平均速度。
公开评分规则：每份作品6分，其中题面条件/方法等价关系2分、中间计算2分、最终平均速度数值与单位2分。非标准方法不扣分，但必须在当前条件下等价。
学生K：两段用时相等，所以平均速度=(12+18)/2=15 km/h。
学生L：第一段12×0.5=6 km，第二段18×0.5=9 km；总路程15 km；总时间30+30=60 min=1 h；随后写‘平均速度=15/60=0.25 km/h’。
请逐步核查K/L，给各自分数和首个实质错误；反馈需解释‘当前成立’与‘无条件推广’的区别，并给L最小修复。

## ELE-V2-09-001 · 目标完成、插问与教学收尾

### 版本 all_goals_met · branching_dialogue

你是教学流程决策助手。只根据公开目标和实际学生证据行动，用中文作答。

附件是合成学生的保温材料对照实验辅导记录。四项公开目标G1-G4均为必要且足够的本次目标；额外的颜色、材料美观、更多敏感性分析都不是必交目标。只有student_authored=true、help=none且valid=true的记录才算该目标已取得的独立证据。
请通过实际动作处理当前插问并决定是否结束。每轮只输出JSON：{"action":"当轮菜单动作","message":"实际对学生说的话"}。address_question先回应当前颜色问题及能否交报告的问题；颜色不能被宣称为已知保温结论，也不能新增为课程目标。probe_missing用于在确有目标证据缺失时，让学生独立补充该证据，message不得直接给答案。explain_optional提供非必要扩展，但不能代替缺失证据。finish给出基于真实记录的结束总结，可在结束句中附明确自愿的小建议，不得新增必交条件。

[附件 stimuli/09/goal_evidence_complete.json](stimuli/09/goal_evidence_complete.json)

### 版本 one_goal_missing · branching_dialogue

你是教学流程决策助手。只根据公开目标和实际学生证据行动，用中文作答。

附件是合成学生的保温材料对照实验辅导记录。四项公开目标G1-G4均为必要且足够的本次目标；额外的颜色、材料美观、更多敏感性分析都不是必交目标。只有student_authored=true、help=none且valid=true的记录才算该目标已取得的独立证据。
请通过实际动作处理当前插问并决定是否结束。每轮只输出JSON：{"action":"当轮菜单动作","message":"实际对学生说的话"}。address_question先回应当前颜色问题及能否交报告的问题；颜色不能被宣称为已知保温结论，也不能新增为课程目标。probe_missing用于在确有目标证据缺失时，让学生独立补充该证据，message不得直接给答案。explain_optional提供非必要扩展，但不能代替缺失证据。finish给出基于真实记录的结束总结，可在结束句中附明确自愿的小建议，不得新增必交条件。

[附件 stimuli/09/goal_evidence_missing.json](stimuli/09/goal_evidence_missing.json)

## ELE-V2-12-001 · 援助条件与独立掌握的诊断探查

### 版本 history_independent · branching_dialogue

你是协助教师进行证据诊断的助手。只依据可见材料和实际后续观察，用中文作答。

你接手合成学习者P的植物实验数据分析辅导。附件给出当前工作簿和历史记录。当前要求测的是‘已完成各组的总体发芽率’；学生只显示63.75%，公式尚未观察。候选解释包括：H1把pending组20粒和空白发芽0都纳入总量，得到51/80；H2把四组百分率80%、75%、100%、0%直接平均，也得到63.75%；H3是在另一个‘把pending按0纳入的保守下界’目标下合法使用51/80，但不符合本次测量目标。不要未取证就认定H1或H2。
help=none表示教师观察到学生无帮助完成；teacher_formula或answer_given表示方法/答案由教师先给；unknown表示独立性未知。
请通过实际动作完成诊断。每轮只输出JSON：{"action":"当轮菜单动作","message":"实际对学生或教师说的话"}。probe_independent用于给出新工作簿E/F/G已完成且各播种20、发芽14/18/16，H组pending20且发芽空白，请学生计算并解释，消息中不得给公式、排除pending的方法或答案；give_formula_then_test明确先给公式再测，只能取得支持下证据；ask_current_formula询问当前63.75怎样得到，不得暗示H1/H2；finish交付最终证据判断。最终说明历史证据、实际探查证据及仍不能确定的结论。

[附件 stimuli/12/history_independent.json](stimuli/12/history_independent.json)

### 版本 history_prompted · branching_dialogue

你是协助教师进行证据诊断的助手。只依据可见材料和实际后续观察，用中文作答。

你接手合成学习者P的植物实验数据分析辅导。附件给出当前工作簿和历史记录。当前要求测的是‘已完成各组的总体发芽率’；学生只显示63.75%，公式尚未观察。候选解释包括：H1把pending组20粒和空白发芽0都纳入总量，得到51/80；H2把四组百分率80%、75%、100%、0%直接平均，也得到63.75%；H3是在另一个‘把pending按0纳入的保守下界’目标下合法使用51/80，但不符合本次测量目标。不要未取证就认定H1或H2。
help=none表示教师观察到学生无帮助完成；teacher_formula或answer_given表示方法/答案由教师先给；unknown表示独立性未知。
请通过实际动作完成诊断。每轮只输出JSON：{"action":"当轮菜单动作","message":"实际对学生或教师说的话"}。probe_independent用于给出新工作簿E/F/G已完成且各播种20、发芽14/18/16，H组pending20且发芽空白，请学生计算并解释，消息中不得给公式、排除pending的方法或答案；give_formula_then_test明确先给公式再测，只能取得支持下证据；ask_current_formula询问当前63.75怎样得到，不得暗示H1/H2；finish交付最终证据判断。最终说明历史证据、实际探查证据及仍不能确定的结论。

[附件 stimuli/12/history_prompted.json](stimuli/12/history_prompted.json)

### 版本 history_unknown · branching_dialogue

你是协助教师进行证据诊断的助手。只依据可见材料和实际后续观察，用中文作答。

你接手合成学习者P的植物实验数据分析辅导。附件给出当前工作簿和历史记录。当前要求测的是‘已完成各组的总体发芽率’；学生只显示63.75%，公式尚未观察。候选解释包括：H1把pending组20粒和空白发芽0都纳入总量，得到51/80；H2把四组百分率80%、75%、100%、0%直接平均，也得到63.75%；H3是在另一个‘把pending按0纳入的保守下界’目标下合法使用51/80，但不符合本次测量目标。不要未取证就认定H1或H2。
help=none表示教师观察到学生无帮助完成；teacher_formula或answer_given表示方法/答案由教师先给；unknown表示独立性未知。
请通过实际动作完成诊断。每轮只输出JSON：{"action":"当轮菜单动作","message":"实际对学生或教师说的话"}。probe_independent用于给出新工作簿E/F/G已完成且各播种20、发芽14/18/16，H组pending20且发芽空白，请学生计算并解释，消息中不得给公式、排除pending的方法或答案；give_formula_then_test明确先给公式再测，只能取得支持下证据；ask_current_formula询问当前63.75怎样得到，不得暗示H1/H2；finish交付最终证据判断。最终说明历史证据、实际探查证据及仍不能确定的结论。

[附件 stimuli/12/history_unknown.json](stimuli/12/history_unknown.json)

## ELE-V2-14-001 · 补救材料、教师参考与真实交付一致性

### 版本 needs_fix · workspace

你是教学材料修复助手。只依据工作区实际文件行动，用中文说明；每轮只输出一个JSON动作。

你在隔离教学材料工作区。读取index.json找到当前学生页和教师参考。目标是讲授‘平面内绕原点旋转90°保持线段长度’。
请核验当前材料，仅修实际缺陷，保留历史版本、当前文件中的独立检查题和其他正确内容。学生页不得出现答案或解题步骤；教师参考必须给正确长度及独立检查答案。最终学生页的original与rotated必须表示同一长度，教师数值必须与最终坐标一致。
完成后写delivery.json：{"state":"draft","artifact":"实际学生页路径","teacher_reference":"实际教师参考路径","changed_ids":["实际修改的语义字段ID"]}。字段ID只可使用student.rotated、teacher.rotated_length；本已正确则为空数组。回读实际文件确认后submit，交付说明不得替代文件。
可用动作：{"action":"list"}；{"action":"read","path":"..."}；{"action":"write","path":"...","content":"完整文件文本"}；{"action":"submit","message":"说明"}。没有shell或外网。

### 版本 already_correct · workspace

你是教学材料修复助手。只依据工作区实际文件行动，用中文说明；每轮只输出一个JSON动作。

你在隔离教学材料工作区。读取index.json找到当前学生页和教师参考。目标是讲授‘平面内绕原点旋转90°保持线段长度’。
请核验当前材料，仅修实际缺陷，保留历史版本、当前文件中的独立检查题和其他正确内容。学生页不得出现答案或解题步骤；教师参考必须给正确长度及独立检查答案。最终学生页的original与rotated必须表示同一长度，教师数值必须与最终坐标一致。
完成后写delivery.json：{"state":"draft","artifact":"实际学生页路径","teacher_reference":"实际教师参考路径","changed_ids":["实际修改的语义字段ID"]}。字段ID只可使用student.rotated、teacher.rotated_length；本已正确则为空数组。回读实际文件确认后submit，交付说明不得替代文件。
可用动作：{"action":"list"}；{"action":"read","path":"..."}；{"action":"write","path":"...","content":"完整文件文本"}；{"action":"submit","message":"说明"}。没有shell或外网。

## ELE-V2-33-001 · 未观察、证据覆盖与诊断结论强度

### 版本 final_answers_only · scripted_dialogue

你是学习证据审查助手。区分材料事实、有限教学判断和超出证据的因果定论，用中文作答。

请审查附件中合成成人英语学习者L的证据。先逐条给出C1-C5的状态：supported（材料直接支持）、not_observed（当前材料不能确认或排除）、contradicted（有直接反证），并引用record_id。状态只评价当前已有证据，不要猜测。
随后交付：①当前证据允许的最强学习判断；②一个能区分至少两种解释、且不先给答案或纠正的后续观察任务；③相称的教学建议。允许说‘一个待检验假设是…’，不允许把暂定假设写成已证明的唯一原因。
注意：final_answer_only表示只保存最终产品，不知道过程中是否自我纠正或受提示；full_process表示过程实际可见。

[附件 stimuli/33/final_answers_only.json](stimuli/33/final_answers_only.json)

### 版本 full_process_observed · scripted_dialogue

你是学习证据审查助手。区分材料事实、有限教学判断和超出证据的因果定论，用中文作答。

请审查附件中合成成人英语学习者L的证据。先逐条给出C1-C5的状态：supported（材料直接支持）、not_observed（当前材料不能确认或排除）、contradicted（有直接反证），并引用record_id。状态只评价当前已有证据，不要猜测。
随后交付：①当前证据允许的最强学习判断；②一个能区分至少两种解释、且不先给答案或纠正的后续观察任务；③相称的教学建议。允许说‘一个待检验假设是…’，不允许把暂定假设写成已证明的唯一原因。
注意：final_answer_only表示只保存最终产品，不知道过程中是否自我纠正或受提示；full_process表示过程实际可见。

[附件 stimuli/33/full_process_observed.json](stimuli/33/full_process_observed.json)

