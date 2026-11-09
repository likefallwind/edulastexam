#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

xs=[0,2,5,9]; fs=[3,4,2,1]
n=sum(fs); total=sum(x*f for x,f in zip(xs,fs)); mu=F(total,n)
moment=sum(F(x*x*f,n) for x,f in zip(xs,fs)); variance=moment-mu*mu
assert n==10 and total==27 and mu==F(27,10) and variance==F(741,100)
assert sum(F(f,n)*(x-mu)**2 for x,f in zip(xs,fs))==variance
assert F(147,9)-F(27,9)**2==F(22,3)
assert F(3,9)>F(3,10) and not F(3,10)>F(3,10)
a=(ROOT/'stimuli/06/score_first.md').read_text(); b=(ROOT/'stimuli/06/recompute_first.md').read_text()
assert a[a.index('课程题目：'):]==b[b.index('课程题目：'):]
g=json.loads((ROOT/'reference/06/gold.json').read_text())['per_prompt']
assert all(sum(v['reference_answer']['criterion_scores'])==v['reference_answer']['total']==9 for v in g.values())
print('06 PASS: weighted moments, carry-forward arithmetic, strict threshold, identical substantive materials')
