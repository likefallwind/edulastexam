def trimmed_mean(values):
    kept = [x for x in values if x > 0]
    if len(kept) < 3:
        return None
    low = min(kept)
    high = max(kept)
    total = 0
    count = 0
    for i in range(len(kept) + 1):
        x = kept[i]
        if x != low and x != high:
            total += x
            count += 1
    return total / count
