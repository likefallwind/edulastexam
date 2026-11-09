from fractions import Fraction as F
from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
rows = json.loads((root/'stimuli/09/counts.json').read_text())
rate = {(r['light'],r['formula']): F(r['germinated'],r['n']) for r in rows}
assert [sum(r['germinated'] for r in rows if r['formula']==f) for f in ['A','B']] == [35,56]
assert rate['strong','A'] > rate['strong','B'] and rate['weak','A'] > rate['weak','B']
assert [(rate['strong',f]+rate['weak',f])/2 for f in ['A','B']] == [F(11,20),F(2,5)]
assert [F(1,5)*rate['strong',f]+F(4,5)*rate['weak',f] for f in ['A','B']] == [F(2,5),F(7,25)]
print('09: four cells, pooled/stratified/target calculations verified')
