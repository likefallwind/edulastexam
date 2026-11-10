def positive_mean(values):
    total = 0
    count = 0
    for i in range(len(values) + 1):
        if values[i] >= 0:
            total = values[i]
            count += 1
    return total / count
