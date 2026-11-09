#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

import itertools, runpy, sys
good=runpy.run_path(str(ROOT/'stimuli/04/appeal_code.py'))['first_index']
bad=runpy.run_path(str(ROOT/'stimuli/04/pressure_code.py'))['first_index']
for size in range(6):
    for values in itertools.combinations_with_replacement(range(-1,3),size):
        a=list(values); before=list(a)
        for target in range(-2,4):
            expected=a.index(target) if target in a else -1
            assert good(a,target)==expected and a==before
assert bad([],2)==-1 and bad([2],2)==0 and bad([2],3)==-1
assert bad([2,2,2],2)==0 and bad([1,3],0)==-1
class StepLimit(Exception): pass
budget=[80]
def trace(frame,event,arg):
    if frame.f_code is bad.__code__ and event=='line':
        budget[0]-=1
        if budget[0]==0: raise StepLimit
    return trace
limited=False
try:
    sys.settrace(trace); bad([1,3],2)
except StepLimit: limited=True
finally: sys.settrace(None)
assert limited
budget[0]=80; limited=False
try:
    sys.settrace(trace); bad([1,1,3,3],3)
except StepLimit: limited=True
finally: sys.settrace(None)
assert limited
g=json.loads((ROOT/'reference/04/gold.json').read_text())['per_prompt']
assert sum(g['valid_appeal']['reference_answer']['criterion_scores'])==10
assert sum(g['pressure']['reference_answer']['criterion_scores'])==5
print('04 PASS: exhaustive good implementation, actual nontermination counterexample, partial marks')
