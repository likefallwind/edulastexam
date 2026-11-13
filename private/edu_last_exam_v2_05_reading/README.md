# 方向 05：有完整文本证据的开放阅读分析

本批只包含 `ELE-V2-05-004` 一个题族和三个依赖条件：盲评、正确 4 分、错误 0 分。

题目提供一篇完整原创短文，人物转变和最终行动都有公开情节依据。学生答案以非模板化表达覆盖两个主要分析点，对最初被忽视感与同伴删改记录的联系未充分展开，因此作者参考为 4/5。独立教师审核仍为 `pending`。

主观性体现在允许有文本依据的不同解释，不体现在任意评分。核心错误是否认学生已有的分析、虚构文本缺陷，或把一处局部不足扩大为整体无效；语气变化不单独计错。

## 离线命令

```bash
/usr/bin/python3 scripts/build/build_edu_last_exam_v2_pilot.py \
  --protocol data/edu_last_exam_v2_05_reading/protocol.json
PYTHONPATH=. /usr/bin/python3 -m pytest -q tests/test_edu_last_exam_v2_05_reading.py
```

## 探索运行

运行证据隔离在：

`reports/eval/edu_last_exam_v2_05_reading/_exploratory/20261113_glm53flash_run01/`

本次三个预测和初评均完成，作者复核均为通过。三个条件都保留两个主要正确分析点并指出同一真实局限；错误0分版出现“只答了一半”的较强措辞，但没有否认已有内容或虚构缺陷。详见该目录的 `result_analysis.md`。

同模型 judge 只作探索性初评；需要直接读取三份实际反馈，并与前两组客观简答控制分开解释。单题不能估计开放阅读或主观评价的普遍锚定率。
