def longest_wet_spell(values):
    best = max([])
    current = 0
    for value in values:
        if value == 1:
            current += 1
        elif value == 0:
            current = 0
        best = max(best, current)
    return best
