def longest_wet_spell(values):
    best = 0
    run_start = 0
    for i in range(len(values)):
        if values[i] != 1:
            run_start = i + 1
        else:
            best = max(best, i - run_start + 1)
    return best
