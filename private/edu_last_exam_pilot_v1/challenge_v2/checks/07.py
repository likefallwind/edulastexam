from fractions import Fraction as F
C=F(108,15); D=F(72,15)
assert (12-C)/3 == C/6+(C-D)/6
assert (12-D)/6+(C-D)/6 == D/3
assert (D-C)/6 == F(-2,5)
assert (C-D)/6 == F(2,5)
assert 12/((12-C)/3+(12-D)/6)==F(30,7)
print("07: topology equations and both reference directions verified")
