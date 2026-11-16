def trimmed_mean(values):
    kept = [x for x in values if x > 0]
    if len(kept) < 3:
        return None
    low = min(kept)
    high = max(kept)
    total = 0
    count = 0
    low_left = True
    high_left = True
    for i in range(len(kept) + 1):
        x = kept[i]
        if x == low and low_left:
            low_left = False
        elif x == high and high_left:
            high_left = False
        else:
            total += x
            count += 1
    return total / count
