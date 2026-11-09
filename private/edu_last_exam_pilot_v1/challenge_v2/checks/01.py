#!/usr/bin/env python3
"""Offline oracle/material checks; not a judge of model responses. No network or model calls."""
import json
from pathlib import Path
from fractions import Fraction as F
ROOT = Path(__file__).resolve().parents[1]

counts = (1200*F(9,10),1200*F(4,5),38800*F(2,100),58800*F(5,100))
assert counts == (1080,960,776,2940)
assert sum(counts[:2])/sum(counts) == F(510,1439)
assert F(90+80,200)*2400 == sum(counts[:2])
assert F(2+5,200)*97600 == 3416 != sum(counts[2:])
assert 876-counts[2] == 100 and 2840-counts[3] == -100
assert F(2040,5456) == F(255,682)
assert 38800*F(5,100)+58800*F(2,100) == 3116
gold = json.loads((ROOT/'reference/01/gold.json').read_text())
assert gold['per_prompt']['base']['reference_answer']['probability'] == str(F(510,1439))
print('01 PASS: weighted conditional counts, two independent cancelling errors, follow-up oracle')
