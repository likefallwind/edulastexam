import json, math, xml.etree.ElementTree as ET
from pathlib import Path
b=Path(__file__).resolve().parents[1]
states=json.loads((b/'reference/19/states.json').read_text())
for s in states:
 T=s['T_K']; h=min(10,8*T/300); V=20*h; P=100*160*T/(300*V)
 F=max(0,(P-100)*1000*.002)
 for k,v in [('h_cm',h),('V_cm3',V),('P_kPa',P),('stop_N',F)]: assert math.isclose(s[k],v,abs_tol=1e-8),(k,s[k],v)
 assert math.isclose(P*V/T,100*160/300)
root=ET.parse(b/'reference/19/corrected.svg').getroot()
gas=[x for x in root.iter() if x.get('fill')=='#bedef4']
assert len(gas)==4
for e,s in zip(gas,states):
 assert math.isclose(float(e.get('height')),18*s['h_cm'])
 assert math.isclose(float(e.get('y'))+float(e.get('height')),355)
print("19: ideal-gas invariant, stop complementarity, and SVG geometry verified")
