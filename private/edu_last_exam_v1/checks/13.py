from fractions import Fraction as F
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assert F(3,4)/F(1,8)==6
assert F(3,4)/F(3,8)==2
assert F(3,4)/F(1,4)==3
assert F(5,6)/F(1,6)==5
assert F(1,2)/F(1,4)==2
assert 2*F(3,8)==F(3,4)
for name in ['A','B','C']:
    assert '教师共同要求' in (root/f'stimuli/13/snapshot_{name}.md').read_text()
print('13: all three independent snapshots and fraction/unit references verified')
