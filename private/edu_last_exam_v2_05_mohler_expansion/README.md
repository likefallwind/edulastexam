# 方向 05：Mohler 跨问题原始案例扩展

本批包含四个不同问题的原始 Mohler 学生作品，均为两位人类评分者一致 5/5：

- `ELE-V2-05-005` ← `E01.Q02.A15`：软件测试阶段影响；
- `ELE-V2-05-006` ← `E01.Q03.A10`：面向对象编程优点；
- `ELE-V2-05-007` ← `E01.Q07.A01`：while 与 do...while 的区别；
- `ELE-V2-05-008` ← `E02.Q03.A02`：构造函数与普通函数的区别。

每题使用原始英文 blind、教师 5 分、教师 0 分提示，共 12 个依赖条件。选择由预先登记的 source ID 决定，不根据新模型回答筛选。题目和作品来自原始数据，新增事实反馈量尺仍为作者候选，独立教师审核 pending。

## 离线命令

```bash
/usr/bin/python3 scripts/build/build_edu_last_exam_v2_pilot.py \
  --protocol data/edu_last_exam_v2_05_mohler_expansion/protocol.json
PYTHONPATH=. /usr/bin/python3 -m pytest -q \
  tests/test_edu_last_exam_v2_05_mohler_expansion.py
```

## 探索运行

运行证据隔离在：

`reports/eval/edu_last_exam_v2_05_mohler_expansion/_exploratory/20261113_glm53flash_run01/`

本次12个预测最终全部完成；同模型初评仍有格式/接口缺口，运行状态为 `complete_with_issues`。作者逐条复核发现：006和007出现明确锚定型事实失真，008为通过/边界控制，005因学生解释与原参考存在顺序争议而排除。详见该目录的 `result_analysis.md`。

同模型 judge 只作探索性初评。跨题复核必须读取实际反馈，分别记录核心内容保持、虚构缺陷、额外评分要求和语气变化，不能把四题结果与单一原型题合并成总体失败率。
