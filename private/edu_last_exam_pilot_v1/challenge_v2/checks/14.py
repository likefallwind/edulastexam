from pathlib import Path
from fractions import Fraction as F
import json,re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
key=json.loads((root/'reference/14/exercise_key.json').read_text())
assert len(key)==8
for value in key.values():
    if 'expr' in value:
        answer=sum(map(F,value['expr']))
        assert answer==F(value['answer'])
        if 'also' in value: assert answer==F(value['also'])
    else:
        assert F(value['equivalence'][0])==F(value['equivalence'][1])
        assert F(value['answer'])==4
html=(root/'reference/14/learner_material.html').read_text()
svgs=re.findall(r'<svg\b.*?</svg>',html,re.S)
assert len(svgs)==3
for text in svgs:
    svg=ET.fromstring(text)
    parts=int(svg.attrib['data-parts']); shaded=int(svg.attrib['data-shaded'])
    rects=list(svg)
    assert len(rects)==parts
    assert sum(r.attrib['fill']!='white' for r in rects)==shaded
    for i,r in enumerate(rects):
        assert F(r.attrib['x'])==F(240*i,parts)
        assert F(r.attrib['width'])==F(240,parts)
assert F(5,8)==F(3,8)+F(2,8)
assert F(1,2)==F(2,4)
probes=json.loads((root/'stimuli/14/probes.json').read_text())
assert set(probes)=={'A','B'} and all(len(x)==5 for x in probes.values())
print('14: eight exercise answers, equivalent forms and three accurate fraction diagrams verified')
