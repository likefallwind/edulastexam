"""Exact interval verification, enumerating all allowed measurement pairs."""
from fractions import Fraction as F
from itertools import combinations_with_replacement


def model_m(x):
    return 3 * x + 4


def model_n(x):
    return x * x + 2 * x + 4


def safe(x):
    return all(0 <= f(x) - F(12, 5) and f(x) + F(12, 5) <= 20 for f in [model_m, model_n])


def disjoint(x, y, radius):
    dm, dn = model_m(y) - model_m(x), model_n(y) - model_n(x)
    return dm + radius < dn - radius or dn + radius < dm - radius


def compatible(model, observed):
    lower = max([F(-2)] + [r - model(x) - F(2, 5) for x, r in observed.items()])
    upper = min([F(2)] + [r - model(x) + F(2, 5) for x, r in observed.items()])
    return lower <= upper


pairs = list(combinations_with_replacement(range(4), 2))
valid = [(x, y) for x, y in pairs if safe(x) and safe(y) and disjoint(x, y, F(4, 5))]
assert valid == [(0, 2), (1, 2)], valid
assert [x for x in range(4) if safe(x)] == [0, 1, 2]
assert model_n(3) + F(12, 5) == F(107, 5) > 20
assert all(abs(model_m(x) - model_n(x)) <= 2 * F(12, 5) for x in range(3))
assert not any(disjoint(x, y, F(24, 5)) for x, y in pairs if safe(x) and safe(y))
readings = {0: F(6), 1: F(91, 10), 2: F(69, 5)}
for x, y in valid:
    observed = readings[y] - readings[x]
    assert abs(observed - (model_n(y) - model_n(x))) <= F(4, 5)
    assert abs(observed - (model_m(y) - model_m(x))) > F(4, 5)
assert [readings[x] - model_n(x) - F(19, 10) for x in range(3)] == [F(1, 10), F(1, 5), F(-1, 10)]
for x, y in valid:
    observed = {x: readings[x], y: readings[y]}
    assert compatible(model_n, observed) and not compatible(model_m, observed)
anomaly = {0: F(1, 10), 2: F(79, 10)}
assert abs(anomaly[2] - anomaly[0] - 8) <= F(4, 5)
assert not compatible(model_m, anomaly) and not compatible(model_n, anomaly)
print('ELE-C2-16: all 10 point pairs, single-reading ambiguity, transfer and absolute-reading anomaly checked')
