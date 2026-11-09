from pathlib import Path
from fractions import Fraction as F
import csv,json
root=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((root/'stimuli/12/attempts.csv').open()))
key=json.loads((root/'reference/12/row_key.json').read_text())
assert len(rows)==len(key)==40
assert [r['record_id'] for r in rows]==[f'R{i:02}' for i in range(1,41)]
assert [r['date'] for r in rows]==sorted(r['date'] for r in rows)
for r,k in zip(rows,key):
    expected=F(k['c']-k['b'],k['a'])
    assert expected==F(k['expected'])
    assert k['a']*expected+k['b']==k['c']
    for part in ['first','final']:
        actual=F(r['response_'+part].replace('−','-'))
        assert (actual==expected)==k[part+'_correct']
old=[k for k in key if k['category']=='distribution' and not k['assisted'] and k['date']<'2026-09-24']
new=[k for k in key if k['category']=='distribution' and not k['assisted'] and k['date']>='2026-09-24']
fee=[k for k in key if k['category']=='fixed_fee' and not k['assisted']]
assert len(old)==4 and sum(k['first_correct'] for k in old)==0
assert len(new)==8 and all(k['first_correct'] for k in new)
assert len(fee)==8 and not any(k['first_correct'] for k in fee)
assert all(k['first_correct'] for k in key if k['category']=='word_other')
assert F(15-6,-3)==-3
assert F(37-9,4)==7 and F(24-6,3)==6
print('12: 40 raw answers, hint separation, time contrasts and proposed probes verified')
