def trimmed_mean(values):
    ordered = sorted(x for x in values if x > 0)
    n = len(ordered)
    if n < 3:
        return None
    return sum(ordered[i] for i in range(1, n - 1)) / (n - 2)
