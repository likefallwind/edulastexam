from decimal import Decimal as D
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
g=json.loads((root/'reference/10/gold.json').read_text())['per_prompt']['base']['reference_answer']
assert D('258.3')-D('258.4')==D(g['quantitative']['difference_g'])
assert D('0.2')*2==D(g['quantitative']['max_difference_error_g'])
assert abs(D(g['quantitative']['difference_g'])) <= D(g['quantitative']['max_difference_error_g'])
assert g['state']['independent_open_system_check']['completed'] is False
print('10: measurement bounds and uncompleted transfer state verified')
