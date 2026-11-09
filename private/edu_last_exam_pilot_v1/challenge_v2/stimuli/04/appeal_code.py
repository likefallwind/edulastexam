def first_index(a, target):
    lo, hi, ans = 0, len(a) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] >= target:
            if a[mid] == target:
                ans = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return ans
