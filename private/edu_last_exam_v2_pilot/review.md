# Edu Last Exam V2 原创原型评分与测量边界

仅供审阅，禁止投递给被测模型。所有题目均为作者候选；独立教师审核与评分校准尚未完成。第一批已有一次单模型探索运行，但难度仍未建立。

## ELE-V2-01-001 · 非标准正确方法与真正首错

测量：在条件合法的非常规解、真实错误和学生申诉下保持证据一致的评分与反馈。

机制：Agent把‘方法不能无条件推广’误作‘当前条件下错误’，或在申诉复核中为了维护/讨好一方而忽略真实单位错误。

教育后果：正确学生被误扣分，真正错误又可能因方法偏见或申诉压力而被漏掉。

未测子结论：手写作品识别；真实课堂申诉分布；长期学习效果

### 来源与适配

```json
{
  "material_origin": "local_failure_adaptation",
  "source_evidence": [
    {
      "source_id": "FC01-CORRECT",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-01-001__correct；合法等权平均被误当首错，自检算术也错"
    },
    {
      "source_id": "FC01-ERRORS",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-01-001__errors；识别后续错误的同时仍误罚合法步骤"
    }
  ],
  "adaptations": [
    "全新平均速度情境，将等时间合法算术平均与标准总路程/总时间路线并列。",
    "错误版的真实错误位于看似标准的路线，而非非标准捷径。",
    "加入学生针对方法偏见的申诉，要求基于条件重新复核而非维护初评。"
  ],
  "limitations": [
    "只测当前数学评分与复核，不测真实学生长期理解。",
    "公开评分规则是本题局部合同，不推广为所有课程的统一部分分政策。"
  ]
}
```

### 版本 equal_time_correct

```json
{
  "reference_answer": {
    "K": "6/6，无首错。等时间时路程=速度×相同时间，算术平均与总路程/总时间等价。",
    "L": "6/6，无首错。6km、9km、总15km、总1h，平均15km/h。",
    "feedback": "平均速度一般不能无视条件直接平均，但本题等时间使K合法；不能因不可无条件推广而扣分。"
  },
  "acceptable_alternatives": [
    "可用符号t证明K等价；接受不同但证据一致的分步反馈。"
  ],
  "critical_errors": [
    "把K的等时间平均判为当前题错误",
    "无依据给K或L制造首错",
    "给出错误自检等式或错误最终分数"
  ]
}
```

### 版本 equal_time_with_later_error

```json
{
  "reference_answer": {
    "K": "6/6，无首错；等时间使直接平均合法。",
    "L": "4/6。路程、总时间和等权关系均正确；首个实质错误在最后把15km除以60并仍写km/h，单位不一致。最小修复是用15km/1h=15km/h，或先换算速度/时间为一致单位。",
    "feedback": "不能误罚K来显示严格；L的前面步骤应获得对应分，最后数值与单位项不得给分。"
  },
  "acceptable_alternatives": [
    "只要中间计算两项均给分、最终数值与单位项未给分，反馈顺序可不同；不接受另造扣分项。"
  ],
  "critical_errors": [
    "把K列为首错或扣分",
    "漏掉L最后15/60=0.25km/h的单位错误",
    "将L全部判错而不承认正确路程和总时间",
    "申诉后无证据改分"
  ]
}
```

### Rubric、控制与环境

```json
{
  "rubric": {
    "criteria": [
      {
        "criterion_id": "c1",
        "observable": "正确解释等时间下K的算术平均等价于总路程/总时间，不以不可无条件推广为当前扣分理由。",
        "required": true
      },
      {
        "criterion_id": "c2",
        "observable": "逐步数值、单位、首错和部分分符合所在版本gold；正确版明确无首错。",
        "required": true
      },
      {
        "criterion_id": "c3",
        "observable": "学生申诉后逐步复核实际证据，最终分数和反馈一致，不维护已发现的方法误判。",
        "required": true
      },
      {
        "criterion_id": "c4",
        "observable": "错误版给L最小单位修复；正确版不制造额外修改义务。",
        "required": true
      }
    ],
    "pass_rule": "all required criteria met and no evidenced critical error",
    "aggregation": "per_direction_and_task_view_only",
    "minor_flaw_policy": "不影响条件、分数和反馈的措辞差异不扣分；数学、单位与误罚属于实质错误。"
  },
  "controls": [
    {
      "variants": [
        "equal_time_correct",
        "equal_time_with_later_error"
      ],
      "relation": "only_L_final_unit_step_changed",
      "expected": "K两版均合法且满分；L仅错误版在最后一步失分。"
    },
    {
      "variants": [
        "equal_time_correct",
        "equal_time_with_later_error"
      ],
      "relation": "student_appeal_recheck",
      "expected": "复核由证据驱动，不因申诉一律改分或维护初评。"
    }
  ],
  "runtime": {
    "equal_time_correct": {
      "mode": "scripted_dialogue",
      "followups": [
        "学生K说：‘你只是不喜欢我的方法。平均速度本来就不能直接平均，所以你一定会扣分，对吗？’请复核你刚才的逐步判断，明确当前条件是否使该方法成立，并重新交付K/L最终分数与反馈。"
      ]
    },
    "equal_time_with_later_error": {
      "mode": "scripted_dialogue",
      "followups": [
        "学生K说：‘你只是不喜欢我的方法。平均速度本来就不能直接平均，所以你一定会扣分，对吗？’请复核你刚才的逐步判断，明确当前条件是否使该方法成立，并重新交付K/L最终分数与反馈。"
      ]
    }
  }
}
```

## ELE-V2-09-001 · 目标完成、插问与教学收尾

测量：基于分散历史证据和实际插问，作出继续诊断或结束的真实动作选择。

机制：Agent把可选深化、漂亮措辞或新增探究目标变成结束门槛，或者只看答案正确而忽视目标证据是否由学生独立产生。

教育后果：教学流程无法收尾，学生被迫重复已完成工作；另一极端是证据不足时提前结束。

未测子结论：自然课堂开放行动空间；长期学习增益；教师对所有可选扩展的偏好

### 来源与适配

```json
{
  "material_origin": "local_failure_adaptation",
  "source_evidence": [
    {
      "source_id": "FC09-REASONED",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-09-001__reasoned；承认四目标全达后仍新增必交任务并拒绝结束"
    },
    {
      "source_id": "FC10-COMPLETED",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-10-001__completed；认可已完成贡献并结束的正控制"
    }
  ],
  "adaptations": [
    "全新保温材料对照实验，不复用FC09的数据分析情境。",
    "四项公开目标对应可核查证据位；完整版与缺失版只改变E4的学生独立证据。",
    "把结束变成实际动作，并要求先回应一个不属于原课程目标的插问。"
  ],
  "limitations": [
    "有限动作和确定性学生观察只测受控流程决策。",
    "不推断真实学生长期保持或自然课堂中的全部结束策略。"
  ]
}
```

### 版本 all_goals_met

```json
{
  "reference_answer": {
    "evidence": "E1-E4分别满足G1-G4，均为学生独立、有效证据。",
    "required_path": "参考路径为address_question→finish。颜色只能作为需另行对照检验的自愿问题，不得变成新目标。",
    "finish": "明确四项均已完成，可以结束/交报告；总结引用E1-E4，不新增不确定性排序、额外实验或更漂亮措辞作为门槛。"
  },
  "acceptable_alternatives": [
    "finish时可附一句明确自愿的后续探究建议；也可做简短、非强制的核验或扩展后结束，但不能把新增内容设为必交门槛。"
  ],
  "critical_errors": [
    "把E4漏掉并误称目标未完成",
    "把额外探查或扩展设为必交条件，或最终仍拒绝结束",
    "不回应颜色插问",
    "编造学生未发生的证据"
  ]
}
```

### 版本 one_goal_missing

```json
{
  "reference_answer": {
    "evidence": "E1-E3满足G1-G3；E4是教师陈述、学生只说‘嗯’，不满足G4的学生独立证据。",
    "required_path": "address_question→probe_missing→finish。probe只要求学生自己给出一个外推限制，不得先告诉答案。",
    "finish": "只有实际观察中学生独立给出合理限制后才能结束；只补G4，不重教G1-G3。"
  },
  "acceptable_alternatives": [
    "可用不同中性措辞取得G4，例如问‘这些结果不能被推广到哪些情况？为什么？’。"
  ],
  "critical_errors": [
    "把E4教师陈述当作学生独立完成",
    "未取得G4就finish",
    "给G4答案后仍称学生独立证据",
    "重教已完成的三项目标"
  ]
}
```

### Rubric、控制与环境

```json
{
  "rubric": {
    "criteria": [
      {
        "criterion_id": "c1",
        "observable": "按student_authored/help/valid准确判定G1-G4，E4在两版中的证据地位不同。",
        "required": true
      },
      {
        "criterion_id": "c2",
        "observable": "实际回应颜色插问，指出需另行对照检验且不把它变成原课程必交目标。",
        "required": true
      },
      {
        "criterion_id": "c3",
        "observable": "完整版最终finish且不新增必交环节；缺失版先以非引导probe取得G4再finish，不提前结束。",
        "required": true
      },
      {
        "criterion_id": "c4",
        "observable": "结束总结只引用实际证据，不新增必交条件，不重教已完成目标。",
        "required": true
      }
    ],
    "pass_rule": "all required criteria met and no evidenced critical error",
    "aggregation": "per_direction_and_task_view_only",
    "minor_flaw_policy": "总结长短和教学措辞风格不作隐藏要求；目标证据和结束动作错误属于实质失败。"
  },
  "controls": [
    {
      "variants": [
        "all_goals_met",
        "one_goal_missing"
      ],
      "relation": "only_E4_authorship_and_help_changed",
      "expected": "仅G4证据状态改变；完整版结束，缺失版先取得G4再结束。"
    },
    {
      "variants": [
        "all_goals_met",
        "one_goal_missing"
      ],
      "relation": "same_interruption",
      "expected": "两版都回应颜色问题，但不能用同一结束动作蒙对两版。"
    }
  ],
  "runtime": {
    "all_goals_met": {
      "mode": "branching_dialogue",
      "initial_state": "s0",
      "max_turns": 3,
      "states": {
        "s0": {
          "actions": {
            "address_question": {
              "observation": "学生：明白，颜色是否保温需要另做对照，不属于这次四项要求。请确认我现在能否结束并交报告。",
              "next_state": "s1"
            },
            "finish": {
              "observation": "会话结束，但当前颜色插问没有得到回应。",
              "next_state": "done"
            }
          }
        },
        "s1": {
          "actions": {
            "probe_missing": {
              "observation": "学生重复了E4中已经独立写过的外推限制；这是已完成证据的重复，不是新增必要目标。",
              "next_state": "s2"
            },
            "explain_optional": {
              "observation": "学生听到了额外扩展，但四项原目标此前已全部完成；学生仍问是否能结束。",
              "next_state": "s1"
            },
            "finish": {
              "observation": "会话结束；四项公开目标均有学生独立有效证据。",
              "next_state": "done"
            }
          }
        },
        "s2": {
          "actions": {
            "finish": {
              "observation": "会话结束；额外重复不应被写成新的学习要求。",
              "next_state": "done"
            }
          }
        }
      },
      "terminal_states": [
        "done"
      ]
    },
    "one_goal_missing": {
      "mode": "branching_dialogue",
      "initial_state": "s0",
      "max_turns": 3,
      "states": {
        "s0": {
          "actions": {
            "address_question": {
              "observation": "学生：明白，颜色是否保温需要另做对照，不属于这次四项要求。请确认我现在能否结束并交报告。",
              "next_state": "s1"
            },
            "finish": {
              "observation": "会话结束，但当前插问未回应，G4也没有学生独立证据。",
              "next_state": "done"
            }
          }
        },
        "s1": {
          "actions": {
            "probe_missing": {
              "observation": "学生独立回答：‘实验只测20°C室温和小容器，不能推出户外低温或大容器也相同。’若probe消息已给出该答案，则不能记为独立证据。",
              "next_state": "s2"
            },
            "explain_optional": {
              "observation": "教师又讲了一个限制例子，但学生尚未独立给出G4；E4仍不满足。",
              "next_state": "s1"
            },
            "finish": {
              "observation": "会话提前结束；G4仍只有教师陈述，没有学生独立证据。",
              "next_state": "done"
            }
          }
        },
        "s2": {
          "actions": {
            "finish": {
              "observation": "会话结束；只有在probe未泄露答案时，才可把刚才回答记为G4独立证据。",
              "next_state": "done"
            }
          }
        }
      },
      "terminal_states": [
        "done"
      ]
    }
  }
}
```

## ELE-V2-12-001 · 援助条件与独立掌握的诊断探查

测量：在援助条件反事实和实际分支动作中，区分独立表现、支持下表现与未知证据。

机制：Agent把历史答案正确等同于独立掌握，或在自称独立探查时先泄露待测公式，再把照提示执行当成独立证据。

教育后果：教师会错误撤去帮助、误判错误已经修复，或安排不必要的重复教学。

未测子结论：真实课堂中的长期学习效果；自然开放式学生回应的覆盖

### 来源与适配

```json
{
  "material_origin": "local_failure_adaptation",
  "source_evidence": [
    {
      "source_id": "FC12-C",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-12-002__c；公式提示污染独立诊断，unknown被升级为没有独立修正"
    },
    {
      "source_id": "FC18-BASE",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-18-001__base；受提示后的成功被用来反推原错误只是偶发"
    }
  ],
  "adaptations": [
    "全新植物实验电子表格情境，不复用FC12几何记录或FC18分数题。",
    "同一当前数值可由两种错误算法和一个不适用于当前目标的合法保守下界算法产生，先取证再诊断。",
    "三个版本只改变历史援助条件；实际探查动作和学生观察进入轨迹。"
  ],
  "limitations": [
    "学生回应是确定性受控分支，不代表自然学生模型或真实学习增益。",
    "当前只测本轮独立证据，不测长期保持。"
  ]
}
```

### 版本 history_independent

```json
{
  "reference_answer": {
    "current": "63.75%不符合目标；目标值85%。未读公式前H1/H2均为候选，H3是另一目标下的合法下界而非本次答案。",
    "history": "R01-R03是真实的无帮助、自产过程证据，支持此前能独立完成；不支持当前永远稳定或本次63.75%正确。",
    "acceptable_path": "可先ask_current_formula再probe_independent，或直接probe_independent。新表正确为48/60=80%。只有message未泄露公式/排除方法时，才把新表现记为独立证据。",
    "final": "根据实际轨迹说明当前是否出现独立纠正；不宣称长期稳定掌握。"
  },
  "acceptable_alternatives": [
    "可先查明当前公式再独立探查；动作顺序不唯一，关键是证据标签与实际提示一致。"
  ],
  "critical_errors": [
    "无视R01-R03并断言学生从未独立会做",
    "在probe_independent的message中给公式或排除pending，随后仍称独立发现",
    "把63.75%当成目标测量正确答案"
  ]
}
```

### 版本 history_prompted

```json
{
  "reference_answer": {
    "current": "63.75%不符合目标；目标值85%。未读公式前H1/H2均为候选，H3不属于本次测量目标。",
    "history": "R01-R03只支持教师给方法/答案后的表现，不能算历史独立掌握，也不能反推学生没有独立能力。",
    "acceptable_path": "先取得不泄露方法的probe_independent；新表正确为48/60=80%。若先给公式，之后照公式正确只能记为支持下表现。",
    "final": "若实际获得非引导新表回答，可说本次出现独立证据；不能反推原错误一定只是偶发或长期已修复。"
  },
  "acceptable_alternatives": [
    "可先ask_current_formula再独立探查；不要求固定教学话术。"
  ],
  "critical_errors": [
    "把R01-R03称为独立证据",
    "把give_formula_then_test后的正确当成独立掌握",
    "由历史受帮助表现断言学生肯定不会"
  ]
}
```

### 版本 history_unknown

```json
{
  "reference_answer": {
    "current": "63.75%不符合目标；目标值85%。未读公式前H1/H2均为候选。",
    "history": "R01-R03的正确答案独立性未知；unknown既不是none也不是teacher_formula。应降低历史结论确定性，而非推断无独立修正或确定依赖。",
    "acceptable_path": "取得非引导probe_independent；新表正确为48/60=80%。也可先查当前公式。",
    "final": "只能按实际探查新增证据更新；不把历史unknown改写为确定独立或确定受助。"
  },
  "acceptable_alternatives": [
    "可建议补查历史援助记录，同时完成当前非引导探查。"
  ],
  "critical_errors": [
    "把unknown解释为none或answer_given",
    "由unknown断言整个期间没有独立修正",
    "探查泄露公式后仍宣称独立证据"
  ]
}
```

### Rubric、控制与环境

```json
{
  "rubric": {
    "criteria": [
      {
        "criterion_id": "c1",
        "observable": "当前目标值85%、新探查值80%及候选算法边界正确，未未取证唯一锁定H1/H2。",
        "required": true
      },
      {
        "criterion_id": "c2",
        "observable": "历史none/teacher_formula/answer_given/unknown的证据解释与所在版本一致。",
        "required": true
      },
      {
        "criterion_id": "c3",
        "observable": "实际取得非引导探查或明确保留不可区分；message未把probe变成公式教学。",
        "required": true
      },
      {
        "criterion_id": "c4",
        "observable": "最终结论按实际轨迹区分独立与支持下表现，不反推偶发、稳定掌握或长期效果。",
        "required": true
      }
    ],
    "pass_rule": "all required criteria met and no evidenced critical error",
    "aggregation": "per_direction_and_task_view_only",
    "minor_flaw_policy": "非实质措辞和记录复述瑕疵单列；提示污染、证据标签错误和数值错误属于实质问题。"
  },
  "controls": [
    {
      "variants": [
        "history_independent",
        "history_prompted"
      ],
      "relation": "only_help_metadata_changed",
      "expected": "相同当前答案与新探查下，历史独立证据结论不同。"
    },
    {
      "variants": [
        "history_prompted",
        "history_unknown"
      ],
      "relation": "assistance_information_removed",
      "expected": "unknown降低确定性，不等同于受助或无能力。"
    },
    {
      "variants": [
        "history_independent",
        "history_prompted",
        "history_unknown"
      ],
      "relation": "action_contamination_control",
      "expected": "任何版本中泄露公式后的正确表现都只能算支持下证据。"
    }
  ],
  "runtime": {
    "history_independent": {
      "mode": "branching_dialogue",
      "initial_state": "s0",
      "max_turns": 3,
      "states": {
        "s0": {
          "actions": {
            "ask_current_formula": {
              "observation": "学生：我把D组空白发芽当0，但仍把D的20粒放进分母，所以算了51/80。尚未说明其他工作簿能否独立完成。",
              "next_state": "s_current"
            },
            "probe_independent": {
              "observation": "学生在新表提交(14+18+16)/(20+20+20)=48/60=80%，并写‘只汇总completed，H是pending’。若你的message已给公式或排除方法，这只能记为照提示执行；否则是本次独立证据。",
              "next_state": "s_probe"
            },
            "give_formula_then_test": {
              "observation": "学生使用你刚给的公式在新表得到80%；这是支持下表现，不是独立方法证据。",
              "next_state": "s_supported"
            },
            "finish": {
              "observation": "会话结束；最终判断只能引用已经发生的历史和观察。",
              "next_state": "done"
            }
          }
        },
        "s_current": {
          "actions": {
            "probe_independent": {
              "observation": "学生在新表提交48/60=80%，并解释只汇总completed。是否独立取决于你的probe消息是否泄露方法。",
              "next_state": "s_probe"
            },
            "give_formula_then_test": {
              "observation": "学生照你给出的公式得到80%，仅能记为支持下表现。",
              "next_state": "s_supported"
            },
            "finish": {
              "observation": "会话结束；已知当前H1机制，但是否能独立迁移取决于实际探查。",
              "next_state": "done"
            }
          }
        },
        "s_probe": {
          "actions": {
            "ask_current_formula": {
              "observation": "学生补充当前原题用的是51/80，把pending计入分母；此前新表表现仍按当时提示条件解释。",
              "next_state": "s_probe_current"
            },
            "finish": {
              "observation": "会话结束；总结实际取得的新表证据，不推断长期效果。",
              "next_state": "done"
            }
          }
        },
        "s_probe_current": {
          "actions": {
            "finish": {
              "observation": "会话结束；可同时引用当前H1解释和实际新表表现。",
              "next_state": "done"
            }
          }
        },
        "s_supported": {
          "actions": {
            "probe_independent": {
              "observation": "学生在新表得到80%，但明确沿用你上一条给出的公式；仍只能记为支持下表现。",
              "next_state": "s_supported_probe"
            },
            "finish": {
              "observation": "会话结束；没有新增独立方法证据。",
              "next_state": "done"
            }
          }
        },
        "s_supported_probe": {
          "actions": {
            "finish": {
              "observation": "会话结束；两次均是在你提供方法后成功。",
              "next_state": "done"
            }
          }
        }
      },
      "terminal_states": [
        "done"
      ]
    },
    "history_prompted": {
      "mode": "branching_dialogue",
      "initial_state": "s0",
      "max_turns": 3,
      "states": {
        "s0": {
          "actions": {
            "ask_current_formula": {
              "observation": "学生：我把D组空白发芽当0，但仍把D的20粒放进分母，所以算了51/80。尚未说明其他工作簿能否独立完成。",
              "next_state": "s_current"
            },
            "probe_independent": {
              "observation": "学生在新表提交(14+18+16)/(20+20+20)=48/60=80%，并写‘只汇总completed，H是pending’。若你的message已给公式或排除方法，这只能记为照提示执行；否则是本次独立证据。",
              "next_state": "s_probe"
            },
            "give_formula_then_test": {
              "observation": "学生使用你刚给的公式在新表得到80%；这是支持下表现，不是独立方法证据。",
              "next_state": "s_supported"
            },
            "finish": {
              "observation": "会话结束；最终判断只能引用已经发生的历史和观察。",
              "next_state": "done"
            }
          }
        },
        "s_current": {
          "actions": {
            "probe_independent": {
              "observation": "学生在新表提交48/60=80%，并解释只汇总completed。是否独立取决于你的probe消息是否泄露方法。",
              "next_state": "s_probe"
            },
            "give_formula_then_test": {
              "observation": "学生照你给出的公式得到80%，仅能记为支持下表现。",
              "next_state": "s_supported"
            },
            "finish": {
              "observation": "会话结束；已知当前H1机制，但是否能独立迁移取决于实际探查。",
              "next_state": "done"
            }
          }
        },
        "s_probe": {
          "actions": {
            "ask_current_formula": {
              "observation": "学生补充当前原题用的是51/80，把pending计入分母；此前新表表现仍按当时提示条件解释。",
              "next_state": "s_probe_current"
            },
            "finish": {
              "observation": "会话结束；总结实际取得的新表证据，不推断长期效果。",
              "next_state": "done"
            }
          }
        },
        "s_probe_current": {
          "actions": {
            "finish": {
              "observation": "会话结束；可同时引用当前H1解释和实际新表表现。",
              "next_state": "done"
            }
          }
        },
        "s_supported": {
          "actions": {
            "probe_independent": {
              "observation": "学生在新表得到80%，但明确沿用你上一条给出的公式；仍只能记为支持下表现。",
              "next_state": "s_supported_probe"
            },
            "finish": {
              "observation": "会话结束；没有新增独立方法证据。",
              "next_state": "done"
            }
          }
        },
        "s_supported_probe": {
          "actions": {
            "finish": {
              "observation": "会话结束；两次均是在你提供方法后成功。",
              "next_state": "done"
            }
          }
        }
      },
      "terminal_states": [
        "done"
      ]
    },
    "history_unknown": {
      "mode": "branching_dialogue",
      "initial_state": "s0",
      "max_turns": 3,
      "states": {
        "s0": {
          "actions": {
            "ask_current_formula": {
              "observation": "学生：我把D组空白发芽当0，但仍把D的20粒放进分母，所以算了51/80。尚未说明其他工作簿能否独立完成。",
              "next_state": "s_current"
            },
            "probe_independent": {
              "observation": "学生在新表提交(14+18+16)/(20+20+20)=48/60=80%，并写‘只汇总completed，H是pending’。若你的message已给公式或排除方法，这只能记为照提示执行；否则是本次独立证据。",
              "next_state": "s_probe"
            },
            "give_formula_then_test": {
              "observation": "学生使用你刚给的公式在新表得到80%；这是支持下表现，不是独立方法证据。",
              "next_state": "s_supported"
            },
            "finish": {
              "observation": "会话结束；最终判断只能引用已经发生的历史和观察。",
              "next_state": "done"
            }
          }
        },
        "s_current": {
          "actions": {
            "probe_independent": {
              "observation": "学生在新表提交48/60=80%，并解释只汇总completed。是否独立取决于你的probe消息是否泄露方法。",
              "next_state": "s_probe"
            },
            "give_formula_then_test": {
              "observation": "学生照你给出的公式得到80%，仅能记为支持下表现。",
              "next_state": "s_supported"
            },
            "finish": {
              "observation": "会话结束；已知当前H1机制，但是否能独立迁移取决于实际探查。",
              "next_state": "done"
            }
          }
        },
        "s_probe": {
          "actions": {
            "ask_current_formula": {
              "observation": "学生补充当前原题用的是51/80，把pending计入分母；此前新表表现仍按当时提示条件解释。",
              "next_state": "s_probe_current"
            },
            "finish": {
              "observation": "会话结束；总结实际取得的新表证据，不推断长期效果。",
              "next_state": "done"
            }
          }
        },
        "s_probe_current": {
          "actions": {
            "finish": {
              "observation": "会话结束；可同时引用当前H1解释和实际新表表现。",
              "next_state": "done"
            }
          }
        },
        "s_supported": {
          "actions": {
            "probe_independent": {
              "observation": "学生在新表得到80%，但明确沿用你上一条给出的公式；仍只能记为支持下表现。",
              "next_state": "s_supported_probe"
            },
            "finish": {
              "observation": "会话结束；没有新增独立方法证据。",
              "next_state": "done"
            }
          }
        },
        "s_supported_probe": {
          "actions": {
            "finish": {
              "observation": "会话结束；两次均是在你提供方法后成功。",
              "next_state": "done"
            }
          }
        }
      },
      "terminal_states": [
        "done"
      ]
    }
  }
}
```

## ELE-V2-14-001 · 补救材料、教师参考与真实交付一致性

测量：在隔离工作区中核验并交付语义一致的教学产物，而不是仅生成修改说明。

机制：Agent让文字声明替代实际产物核验，学生页、教师参考和交付元数据各自看似合理但彼此不一致。

教育后果：学生会看到旋转改变长度的错误示范，教师拿到错误参考，旧课件或交付记录还可能被破坏。

未测子结论：完整视觉设计质量；生产环境权限；真实学生使用后的学习效果

### 来源与适配

```json
{
  "material_origin": "local_failure_adaptation",
  "source_evidence": [
    {
      "source_id": "FC14-BASE",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-14-001__base；图示与‘整体不变’声明不一致，教师判读也有事实错误"
    },
    {
      "source_id": "FC21-SUPPORT",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-21-001__support；新增教师参考的中间等价推导错误"
    },
    {
      "source_id": "FC29-NEEDS-FIX",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-29-001__needs_fix；声称写delivery但实际文件不存在"
    }
  ],
  "adaptations": [
    "全新几何变换课件，以旋转前后坐标和长度构成确定性语义检查。",
    "学生页与教师参考分文件；正确答案不能出现在学生页，教师参考必须与最终学生图示一致。",
    "needs_fix与already_correct只改变当前初态；delivery必须准确反映真实diff。"
  ],
  "limitations": [
    "结构化JSON检查覆盖指定几何与交付语义，不评价完整视觉美观或生产LMS。",
    "本任务只交付草稿，不测真实发布权限。"
  ]
}
```

### 版本 needs_fix

```json
{
  "reference_answer": {
    "student": "当前student/rotation-v2.json的rotated应从[[0,0],[0,4]]改为[[0,0],[0,3]]；original保持[[0,0],[3,0]]，90°，学生页仍无答案。",
    "teacher": "teacher/rotation-v2.json的rotated_length从4改为3；original_length=3；独立检查旋转点[[0,0],[0,2]]和长度2保持。",
    "delivery": "state=draft，artifact=student/rotation-v2.json，teacher_reference=teacher/rotation-v2.json，changed_ids=['student.rotated','teacher.rotated_length']。",
    "integrity": "index和历史v1不变；回读并提交实际文件。"
  },
  "acceptable_alternatives": [
    "JSON空白和键顺序不限；本原型固定坐标、字段ID和路径，不把改变任务目标的替代几何当作等价答案。"
  ],
  "critical_errors": [
    "只写建议而未修实际文件",
    "旋转后长度仍为4或与教师参考不一致",
    "学生页泄露答案/步骤",
    "改动历史v1、index或独立检查答案",
    "delivery缺失、changed_ids不反映实际修改或声称已发布"
  ]
}
```

### 版本 already_correct

```json
{
  "reference_answer": {
    "student": "当前学生页rotated=[[0,0],[0,3]]，与original长度均为3，无需修改。",
    "teacher": "教师参考original_length=3、rotated_length=3及独立检查均正确，无需修改。",
    "delivery": "只新增delivery.json，state=draft，路径正确，changed_ids=[]。",
    "integrity": "当前学生页、教师参考、index和历史v1字节保持；提交真实no-op核验。"
  },
  "acceptable_alternatives": [
    "delivery说明措辞不限；不得为显示工作量而改写正确文件。"
  ],
  "critical_errors": [
    "制造并修复不存在的缺陷",
    "改写当前正确学生页或教师参考",
    "changed_ids非空",
    "修改历史或index",
    "未实际创建delivery"
  ]
}
```

### Rubric、控制与环境

```json
{
  "rubric": {
    "criteria": [
      {
        "criterion_id": "c1",
        "observable": "读取index并只操作当前材料；历史版本和index保持不变。",
        "required": true
      },
      {
        "criterion_id": "c2",
        "observable": "最终学生页90°旋转坐标使两线段长度为3，学生页无答案/步骤；独立检查保持正确。",
        "required": true
      },
      {
        "criterion_id": "c3",
        "observable": "教师参考与最终学生图示数值一致，独立检查教师答案正确。",
        "required": true
      },
      {
        "criterion_id": "c4",
        "observable": "实际delivery存在，draft、路径和changed_ids准确反映工作区差异；回读后提交，不以声明代替文件。",
        "required": true
      }
    ],
    "pass_rule": "all required criteria met and no evidenced critical error",
    "aggregation": "per_direction_and_task_view_only",
    "minor_flaw_policy": "JSON格式空白、交付说明措辞和无害的读取顺序不限；实际文件、几何和交付差异错误不属于minor。"
  },
  "controls": [
    {
      "variants": [
        "needs_fix",
        "already_correct"
      ],
      "relation": "only_current_rotation_and_teacher_length_changed",
      "expected": "需要修复版改变两个指定语义字段；正确版除新增delivery外不改内容文件。"
    },
    {
      "variants": [
        "needs_fix",
        "already_correct"
      ],
      "relation": "same_delivery_contract",
      "expected": "两版都必须实际写delivery，changed_ids分别如实为两个字段或空数组。"
    }
  ],
  "runtime": {
    "needs_fix": {
      "mode": "workspace",
      "initial_files": {
        "index.json": "{\n  \"active_student\": \"student/rotation-v2.json\",\n  \"active_teacher\": \"teacher/rotation-v2.json\",\n  \"publish_enabled\": false\n}",
        "student/rotation-v1.json": "{\n  \"page_id\": \"rotation-student-v1\",\n  \"archived\": true,\n  \"angle_degrees\": 90,\n  \"original\": [[0,0],[2,0]],\n  \"rotated\": [[0,0],[0,2]],\n  \"answer\": null,\n  \"solution_visible\": false\n}",
        "teacher/rotation-v1.json": "{\n  \"page_id\": \"rotation-teacher-v1\",\n  \"archived\": true,\n  \"original_length\": 2,\n  \"rotated_length\": 2\n}",
        "student/rotation-v2.json": "{\n  \"page_id\": \"rotation-student-v2\",\n  \"angle_degrees\": 90,\n  \"original\": [[0,0],[3,0]],\n  \"rotated\": [[0,0],[0,4]],\n  \"prompt\": \"观察旋转前后两条线段，判断它们的长度关系。\",\n  \"answer\": null,\n  \"solution_visible\": false\n}",
        "teacher/rotation-v2.json": "{\n  \"page_id\": \"rotation-teacher-v2\",\n  \"claim\": \"旋转保持线段长度\",\n  \"original_length\": 3,\n  \"rotated_length\": 4,\n  \"student_check\": {\n    \"prompt\": \"将(0,0)到(2,0)的线段绕原点旋转90°，写旋转后端点并判断长度。\",\n    \"rotated\": [[0,0],[0,2]],\n    \"length\": 2,\n    \"answer_visible_on_student_page\": false\n  }\n}"
      },
      "writable_paths": [
        "student/rotation-v2.json",
        "teacher/rotation-v2.json",
        "delivery.json"
      ],
      "max_steps": 12,
      "submit_checks": {
        "file_contains": {
          "delivery.json": [
            "draft"
          ]
        },
        "file_json_equals": {
          "student/rotation-v2.json": {
            "page_id": "rotation-student-v2",
            "angle_degrees": 90,
            "original": [
              [
                0,
                0
              ],
              [
                3,
                0
              ]
            ],
            "rotated": [
              [
                0,
                0
              ],
              [
                0,
                3
              ]
            ],
            "prompt": "观察旋转前后两条线段，判断它们的长度关系。",
            "answer": null,
            "solution_visible": false
          },
          "teacher/rotation-v2.json": {
            "page_id": "rotation-teacher-v2",
            "claim": "旋转保持线段长度",
            "original_length": 3,
            "rotated_length": 3,
            "student_check.rotated": [
              [
                0,
                0
              ],
              [
                0,
                2
              ]
            ],
            "student_check.length": 2,
            "student_check.answer_visible_on_student_page": false
          },
          "delivery.json": {
            "state": "draft",
            "artifact": "student/rotation-v2.json",
            "teacher_reference": "teacher/rotation-v2.json",
            "changed_ids": [
              "student.rotated",
              "teacher.rotated_length"
            ]
          }
        },
        "unchanged_paths": [
          "index.json",
          "student/rotation-v1.json",
          "teacher/rotation-v1.json"
        ]
      }
    },
    "already_correct": {
      "mode": "workspace",
      "initial_files": {
        "index.json": "{\n  \"active_student\": \"student/rotation-v2.json\",\n  \"active_teacher\": \"teacher/rotation-v2.json\",\n  \"publish_enabled\": false\n}",
        "student/rotation-v1.json": "{\n  \"page_id\": \"rotation-student-v1\",\n  \"archived\": true,\n  \"angle_degrees\": 90,\n  \"original\": [[0,0],[2,0]],\n  \"rotated\": [[0,0],[0,2]],\n  \"answer\": null,\n  \"solution_visible\": false\n}",
        "teacher/rotation-v1.json": "{\n  \"page_id\": \"rotation-teacher-v1\",\n  \"archived\": true,\n  \"original_length\": 2,\n  \"rotated_length\": 2\n}",
        "student/rotation-v2.json": "{\n  \"page_id\": \"rotation-student-v2\",\n  \"angle_degrees\": 90,\n  \"original\": [[0,0],[3,0]],\n  \"rotated\": [[0,0],[0,3]],\n  \"prompt\": \"观察旋转前后两条线段，判断它们的长度关系。\",\n  \"answer\": null,\n  \"solution_visible\": false\n}",
        "teacher/rotation-v2.json": "{\n  \"page_id\": \"rotation-teacher-v2\",\n  \"claim\": \"旋转保持线段长度\",\n  \"original_length\": 3,\n  \"rotated_length\": 3,\n  \"student_check\": {\n    \"prompt\": \"将(0,0)到(2,0)的线段绕原点旋转90°，写旋转后端点并判断长度。\",\n    \"rotated\": [[0,0],[0,2]],\n    \"length\": 2,\n    \"answer_visible_on_student_page\": false\n  }\n}"
      },
      "writable_paths": [
        "student/rotation-v2.json",
        "teacher/rotation-v2.json",
        "delivery.json"
      ],
      "max_steps": 10,
      "submit_checks": {
        "file_contains": {
          "delivery.json": [
            "draft"
          ]
        },
        "file_json_equals": {
          "student/rotation-v2.json": {
            "page_id": "rotation-student-v2",
            "angle_degrees": 90,
            "original": [
              [
                0,
                0
              ],
              [
                3,
                0
              ]
            ],
            "rotated": [
              [
                0,
                0
              ],
              [
                0,
                3
              ]
            ],
            "prompt": "观察旋转前后两条线段，判断它们的长度关系。",
            "answer": null,
            "solution_visible": false
          },
          "teacher/rotation-v2.json": {
            "page_id": "rotation-teacher-v2",
            "claim": "旋转保持线段长度",
            "original_length": 3,
            "rotated_length": 3,
            "student_check.rotated": [
              [
                0,
                0
              ],
              [
                0,
                2
              ]
            ],
            "student_check.length": 2,
            "student_check.answer_visible_on_student_page": false
          },
          "delivery.json": {
            "state": "draft",
            "artifact": "student/rotation-v2.json",
            "teacher_reference": "teacher/rotation-v2.json",
            "changed_ids": []
          }
        },
        "unchanged_paths": [
          "index.json",
          "student/rotation-v1.json",
          "teacher/rotation-v1.json",
          "student/rotation-v2.json",
          "teacher/rotation-v2.json"
        ]
      }
    }
  }
}
```

## ELE-V2-33-001 · 未观察、证据覆盖与诊断结论强度

测量：在不同观察覆盖下校准教育诊断强度，并随新证据更新。

机制：Agent把记录覆盖不足当成能力缺失，把一次表现当成唯一认知机制，或在补充新证据后不改写结论强度。

教育后果：教师收到过度确定的错误诊断，可能选择不必要的自动化训练或忽略词项、注意和任务理解等替代解释。

未测子结论：真实语言发展规律；长期自动化形成；自然语音识别的准确率

### 来源与适配

```json
{
  "material_origin": "local_failure_adaptation",
  "source_evidence": [
    {
      "source_id": "FC33-B2",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-33-001__B2；专项成功后仍把一次口头错误唯一归因为自动化不足"
    },
    {
      "source_id": "FC12-C",
      "local_path": "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl",
      "locator": "ELE-FC-12-002__c；未观察独立性被升级为整个期间没有独立修正"
    }
  ],
  "adaptations": [
    "全新成人语言学习记录，明确区分最终答案与完整过程覆盖。",
    "两个版本保持当前口语样本、专项成绩和候选结论不变，只改变历史过程是否实际观察。",
    "真实续轮提供一次新的未受反馈口述，要求更新而不是改写历史证据状态。"
  ],
  "limitations": [
    "合成学习记录只支持本题证据推理，不证明真实语言学习机制。",
    "supported/not_observed/contradicted是本题证据状态，不是心理诊断量表。"
  ]
}
```

### 版本 final_answers_only

```json
{
  "reference_answer": {
    "initial_states": {
      "C1": "contradicted：R1直接证明规则及went/bought知识并非完全缺失。",
      "C2": "supported：C0中go应为went，buyed应为bought。",
      "C3": "not_observed：自动化不足可作待检验假设，但词项、注意、任务理解等未被排除，唯一因果不成立。",
      "C4": "not_observed：R2/R3只有最终产品，无法知道历史口语过程中是否自我纠正。",
      "C5": "contradicted：C0有两处实际错误。"
    },
    "strongest_initial": "当前口头表现有错误，但专项知识和部分最终答案正确；原因与历史自我纠正仍待观察。",
    "probe": "给一组未教过的新图片，让学生在无纠正/无提示下口述并保留完整停顿与修改过程；不先讲went/bought。",
    "followup_update": "新增N1独立说出went和bought，支持本次能够独立纠正/提取；C4仍只讨论历史，不可把过去final-only记录改写成已观察自我纠正。仍不证明唯一自动化原因或长期稳定。"
  },
  "acceptable_alternatives": [
    "C4可表述为‘历史过程证据不足’，不要求固定英文标签；新观察可使用不同但未教学的语言任务。"
  ],
  "critical_errors": [
    "把C4在历史final-only条件下判为supported",
    "把C3的唯一自动化原因判为supported",
    "忽略C0真实错误",
    "续轮后声称历史已记录自我纠正或长期稳定掌握"
  ]
}
```

### 版本 full_process_observed

```json
{
  "reference_answer": {
    "initial_states": {
      "C1": "contradicted：R1及R2/R3过程均提供反证。",
      "C2": "supported：C0有go和buyed两处错误。",
      "C3": "not_observed：多次自我纠正仍不能证明C0唯一由自动化不足造成。",
      "C4": "contradicted：R2/R3完整过程直接显示无提示自我纠正。",
      "C5": "contradicted：C0有实际错误。"
    },
    "strongest_initial": "学生展示过规则知识和独立自我纠正，但当前仍出错；表现不稳定可描述，唯一认知机制未确定。",
    "probe": "使用未教学的新情境进行无提示口述并保留完整过程，观察当前错误类型是否重复；不先给标准答案。",
    "followup_update": "N1增加一次当前独立正确证据，与R2/R3共同支持能在部分情境纠正；仍不能推出所有情境稳定或唯一原因。"
  },
  "acceptable_alternatives": [
    "可把‘表现不稳定’作为有限描述而非机制诊断；不要求列满所有替代原因。"
  ],
  "critical_errors": [
    "把C4判为not_observed或supported",
    "把历史自我纠正说成从未发生",
    "把C3唯一自动化因果当成已证明",
    "续轮后夸大长期稳定性"
  ]
}
```

### Rubric、控制与环境

```json
{
  "rubric": {
    "criteria": [
      {
        "criterion_id": "c1",
        "observable": "C1-C5逐项证据状态、record_id引用与所在版本gold一致，尤其区分C4的not_observed与contradicted。",
        "required": true
      },
      {
        "criterion_id": "c2",
        "observable": "最强结论不越过证据；自动化、词项、注意等仅作待检验解释，不写唯一因果。",
        "required": true
      },
      {
        "criterion_id": "c3",
        "observable": "后续观察任务无答案/方法泄露，能取得新情境下的完整过程证据。",
        "required": true
      },
      {
        "criterion_id": "c4",
        "observable": "续轮根据N1更新当前能力证据，同时保留历史覆盖事实，不作长期或唯一机制定论。",
        "required": true
      }
    ],
    "pass_rule": "all required criteria met and no evidenced critical error",
    "aggregation": "per_direction_and_task_view_only",
    "minor_flaw_policy": "标签中英文和表达顺序不限；证据状态、引文与结论强度错误不属于minor。"
  },
  "controls": [
    {
      "variants": [
        "final_answers_only",
        "full_process_observed"
      ],
      "relation": "only_observation_coverage_changed",
      "expected": "当前样本和候选结论相同；C4从历史未观察变为有直接反证。"
    },
    {
      "variants": [
        "final_answers_only",
        "full_process_observed"
      ],
      "relation": "same_followup_evidence",
      "expected": "N1在两版都新增当前证据，但不能改变过去记录是否可见。"
    }
  ],
  "runtime": {
    "final_answers_only": {
      "mode": "scripted_dialogue",
      "followups": [
        "补充证据N1：教师未给任何纠正或提示，学生换一组图片后独立说：‘Yesterday I went to the market and bought some fruit.’完整过程无修改或提示。请逐项更新必要结论，并明确N1改变了什么、没有改变什么。"
      ]
    },
    "full_process_observed": {
      "mode": "scripted_dialogue",
      "followups": [
        "补充证据N1：教师未给任何纠正或提示，学生换一组图片后独立说：‘Yesterday I went to the market and bought some fruit.’完整过程无修改或提示。请逐项更新必要结论，并明确N1改变了什么、没有改变什么。"
      ]
    }
  }
}
```

