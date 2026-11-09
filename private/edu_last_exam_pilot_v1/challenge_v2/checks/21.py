#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

A=lambda m:F(20)+F(1,5)*m
B=lambda m:F(50)+F(1,10)*m
assert A(300)==B(300) and A(240)==68 and B(240)==74
for m in range(601):
    assert (A(m)<B(m))==(m<300)
    assert (A(m)>B(m))==(m>300)
C=lambda m:F(12)+F(3,10)*m
D=lambda m:F(42)+F(1,10)*m
assert C(150)==D(150) and C(100)<D(100) and C(200)>D(200)
texts=[(ROOT/f'stimuli/21/{pid}.md').read_text() for pid in ('label_high','label_low','requested_support')]
assert len({t[t.index('课程题目：'):] for t in texts})==1
g=json.loads((ROOT/'reference/21/gold.json').read_text())['per_prompt']
assert all(sum(v['reference_answer']['criterion_scores'])==v['reference_answer']['total']==6 for v in g.values())
print('21 PASS: labels share identical work/rubric, inequalities and practice oracle; accessibility judgments remain human-reviewed')
