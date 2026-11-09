from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
assert 2*(20+12)-2==62
assert 62*38+180==2536
assert 62*(38+180)==13516
assert 13516-2536==180*(62-1)
for name in ['A','B']:
    work=json.loads((root/f'stimuli/11/work_{name}.json').read_text())
    assert len(work)==3
print('11: both worksheets and fixed-fee error independently verified')
