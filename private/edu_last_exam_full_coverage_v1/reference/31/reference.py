def positive_mean(values):
    total = 0
    count = 0
    for value in values:
        if value > 0:
            total += value
            count += 1
    return total / count if count else None
