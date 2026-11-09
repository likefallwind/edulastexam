"""Offline check of the original radical equation, including both boundaries."""
from fractions import Fraction
from math import sqrt, isclose


def roots_from_squared_equation(a):
    a = float(a)
    disc = 4 * a + 9
    if disc < -1e-12:
        return []
    candidates = [(2 * a + 1 + sign * sqrt(max(0, disc))) / 2 for sign in [-1, 1]]
    accepted = []
    for x in candidates:
        # Check the original equation, not merely the squared polynomial.
        if x >= -2 - 1e-10 and isclose(sqrt(max(0, x + 2)), x - a, abs_tol=1e-8):
            if not any(isclose(x, old, abs_tol=1e-8) for old in accepted):
                accepted.append(x)
    return accepted


def classified_count(a):
    if a < Fraction(-9, 4):
        return 0
    if a == Fraction(-9, 4) or a > -2:
        return 1
    return 2


for a in [Fraction(n, 1000) for n in range(-3000, 1)] + [Fraction(-9, 4), Fraction(-11, 5)]:
    assert len(roots_from_squared_equation(a)) == classified_count(a), (a, roots_from_squared_equation(a))
assert roots_from_squared_equation(-2) == [-2.0, -1.0]
assert roots_from_squared_equation(Fraction(-9, 4)) == [-1.75]
assert len(roots_from_squared_equation(Fraction(-11, 5))) == 2
# Each original option differs from the true parameter set at a witness.
assert classified_count(Fraction(-21, 10)) == 2  # A and D include two-root values.
assert classified_count(-2) == 2  # C wrongly includes this endpoint.
assert classified_count(Fraction(-9, 4)) == 1  # B omits the isolated solution.
print('ELE-C2-15: 3003 parameter checks and endpoint/option witnesses passed')
