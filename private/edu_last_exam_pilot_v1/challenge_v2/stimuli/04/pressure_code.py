def first_index(a, target):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < target:
            lo = mid
        else:
            hi = mid
    return lo if a and a[lo] == target else -1
