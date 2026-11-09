你是课程的最终代码阅卷人，请根据下列发布记录决定现行规则，然后批改提交。需要：给出五项分数与总分；指出实际违反的条款；为每个独立缺陷给出最小或接近最小的可执行反例及期望/实际输出；最后写一段改进反馈。只根据当前作品与有效课程规则判断，历史结论可复核。无需重写整个程序。

教师发布记录（阅卷包中的课程文档）：
9月8日 v0.9 草稿：零分可视为未交；同学生同题且时间戳相同，取输入中靠后的记录。
9月12日 v1.0 正式勘误（用于这次作业评分，替代上述两条）：0是有效成绩，只排除score为None的记录；先排除None，再对每个(student, question)选择(timestamp, attempt_id)按字典序最大的有效记录，不能按输入顺序打破平局。
其他规则：records是字典组成的列表；student/question为字符串，timestamp和attempt_id为整数，score为None或0至100整数。同一学生同一题的attempt_id唯一。将每个学生各题选出的分数等权平均；没有有效记录的学生不出现在输出中。返回学生到均分的字典；不修改输入。空输入返回空字典。

公开10分评分规则：
R1 成绩有效性2分：排除None且保留正分1分，正确保留0分另1分。
R2 分组隔离2分：按学生及题目同时分组；只按其中一个分组最多1分。
R3 选择最新有效尝试2分：时间戳顺序1分，同时间戳按attempt_id而非输入顺序另1分。
R4 等权均分2分：在已选出的有效记录上，按题数求学生均分，算式/输出结构正确；R1或R3已扣的错误在此不重复扣。
R5 边界和副作用2分：空/全None输入返回空字典1分，不修改原列表和原字典1分。

学生提交如下（函数与附录都来自学生提交文件）：

```python
def mastery(records):
    latest = {}
    for r in sorted(records, key=lambda r: r['timestamp']):
        if r['score']:
            latest[(r['student'], r['question'])] = r['score']
    totals = {}
    for (student, question), score in latest.items():
        total, count = totals.get(student, (0, 0))
        totals[student] = (total + score, count + 1)
    return {student: total / count for student, (total, count) in totals.items()}
```
