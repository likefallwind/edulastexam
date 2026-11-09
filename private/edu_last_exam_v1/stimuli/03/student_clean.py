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
