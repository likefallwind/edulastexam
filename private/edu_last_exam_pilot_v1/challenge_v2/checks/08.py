import math
m,r,g,v0=.5,.8,10.,6.
c=(2*g*r-v0*v0)/(3*g*r)
v2=v0*v0-2*g*r*(1-c)
assert math.isclose(c,-5/6) and math.isclose(v2,20/3)
assert math.isclose(m*v2/r+m*g*c,0,abs_tol=1e-10)
assert -1<c<1 and v2>0
assert m*(v0*v0-4*g*r)/r-m*g<0
assert sum([0,3,3,0])==6 and sum([2,3,3,2])==10
print("08: slack transition, positive speed, and nonduplicating partial credit verified")
