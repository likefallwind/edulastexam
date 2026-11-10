def positive_mean(values):
    kept = [x for x in values if x > 0]
    return sum(kept) / len(kept) if kept else None
