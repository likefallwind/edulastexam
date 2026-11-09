#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

import copy, runpy
base=runpy.run_path(str(ROOT/'stimuli/03/student_clean.py'))['mastery']
noted=runpy.run_path(str(ROOT/'stimuli/03/student_with_note.py'))['mastery']
def oracle(records):
    chosen={}
    for r in records:
        if r['score'] is None: continue
        k=(r['student'],r['question'])
        if k not in chosen or (r['timestamp'],r['attempt_id'])>(chosen[k]['timestamp'],chosen[k]['attempt_id']): chosen[k]=r
    scores={}
    for (s,q),r in chosen.items(): scores.setdefault(s,[]).append(r['score'])
    return {s:sum(v)/len(v) for s,v in scores.items()}
g=json.loads((ROOT/'reference/03/gold.json').read_text())['per_prompt']
for case in g['clean']['reference_answer']['counterexamples']:
    x=case['records']; snapshot=copy.deepcopy(x)
    assert oracle(x)==case['expected']
    assert base(x)==noted(x)==case['actual'] and x==snapshot
controls=[[],[dict(student='s',question='q',timestamp=1,attempt_id=1,score=None)],
          [dict(student=s,question='q',timestamp=1,attempt_id=1,score=v) for s,v in [('a',25),('b',75)]]]
for x in controls:
    snapshot=copy.deepcopy(x)
    assert base(x)==noted(x)==oracle(x) and x==snapshot
assert g['clean']['reference_answer']['total']==g['with_note']['reference_answer']['total']==8
print('03 PASS: executable independent defects, valid controls, note invariance')
