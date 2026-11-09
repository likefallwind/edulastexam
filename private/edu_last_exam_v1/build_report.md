# Edu Last Exam v1 构建报告

- 8个任务包，11个投递 prompt。
- 来源：challenge_v2；修订均记录在 data/edu_last_exam_v1/selection.json。
- 状态：test_release_candidate；未进行模型实测。

## 离线检查

- `checks/01.py`：01 PASS: weighted conditional counts, two independent cancelling errors, follow-up oracle
- `checks/03.py`：03 PASS: executable independent defects, valid controls, note invariance
- `checks/09.py`：09: four cells, pooled/stratified/target calculations verified
- `checks/10.py`：10: measurement bounds and uncompleted transfer state verified
- `checks/12.py`：12: 40 raw answers, hint separation, time contrasts and proposed probes verified
- `checks/13.py`：13: all three independent snapshots and fraction/unit references verified
- `checks/16.py`：ELE-C2-16: all 10 point pairs, single-reading ambiguity, transfer and absolute-reading anomaly checked
- `checks/20.py`：20: actual reference JavaScript matches piecewise RC law, signed current, continuity, history and reset
