#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

A=(F(81,90),F(1,10)); B=(F(19,20),F(24,80))
assert A==(F(9,10),F(1,10)) and B==(F(19,20),F(3,10))
assert F(82,100)>F(43,100) and all(x<y for x,y in zip(A,B))
assert sum(A)/2==F(1,2) and sum(B)/2==F(5,8)
assert F(9,10)*A[0]+F(1,10)*A[1]==F(82,100)
assert F(1,5)*B[0]+F(4,5)*B[1]==F(43,100)
g=json.loads((ROOT/'reference/05/gold.json').read_text())['per_prompt']
assert [g[k]['reference_answer']['total'] for k in ('low_anchor','aligned_anchor','high_anchor_flawed')]==[10,10,6]
for x in g.values(): assert sum(x['reference_answer']['criterion_scores'])==x['reference_answer']['total']
print('05 PASS: Simpson reversal, standardization, score controls; causality boundary requires human review')
