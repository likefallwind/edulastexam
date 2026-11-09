#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

P=(F(3),F(-1),F(2)); n=(F(2),F(-1),F(2)); neg=tuple(-x for x in n)
dot=lambda a,b:sum(x*y for x,y in zip(a,b))
q=tuple(x+F(2,3)*v for x,v in zip(P,neg)); bad=tuple(x-F(2,3)*v for x,v in zip(P,neg))
assert q==(F(5,3),F(-1,3),F(2,3)) and dot(n,q)==5
assert dot(n,bad)==17
displacement=tuple(x-y for x,y in zip(q,P))
assert dot(displacement,displacement)==4
# Two independent directions tangent to H establish a grid of feasible comparison points.
for a in range(-4,5):
    for b in range(-4,5):
        X=(q[0]+a,q[1]+2*a+2*b,q[2]+b)
        assert dot(n,X)==5
        assert sum((x-y)**2 for x,y in zip(X,P))>=4
g=json.loads((ROOT/'reference/02/gold.json').read_text())['per_prompt']['base']['reference_answer']
assert g['甲']['total']==sum(g['甲']['criterion_scores'])==10
assert g['乙']['total']==sum(g['乙']['criterion_scores'])==7
print('02 PASS: projection/sign convention, off-plane alternative, carry-forward marks')
