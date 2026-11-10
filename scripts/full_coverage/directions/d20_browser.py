"""Offline browser validation of trusted direction 19/20 reference artifacts."""
from pathlib import Path
import json,math,shutil
from playwright.sync_api import sync_playwright
import d19, d20
R=Path('/home/likefallwind/code/edulastexam');B=R/'private/edu_last_exam_full_coverage_v1/reference'
scratch=R/'tmp/full_coverage_reference_browser'
for n,mod,file in [('19',d19,'correct_spec.json'),('20',d20,'correct_config.json')]:
 result=mod.validate_artifact((B/n/file).read_text(),scratch/n,'generate')
 assert result['passed'],result
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True)
 context=browser.new_context(viewport={'width':1150,'height':850});context.route('**/*',lambda r:r.abort())
 page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content((scratch/'19/diagram.svg').read_text());page.wait_for_load_state('networkidle')
 assert page.locator('svg g').count()==4
 page.screenshot(path=str(B/'19/correct_diagram.png'),full_page=True)
 shutil.copyfile(scratch/'19/diagram.svg',B/'19/correct_diagram.svg')
 page.set_content((scratch/'20/simulator.html').read_text());page.wait_for_load_state('networkidle')
 page.locator('#dt').fill('0.3');page.locator('#advance').click()
 state=page.evaluate('eduSimulator.state()');assert abs(state['voltage']-10*(1-math.exp(-1.5)))<1e-6
 history=state['history'];page.locator('#mode').select_option('discharge');page.locator('#resistance').fill('1000');page.locator('#resistance').dispatch_event('change')
 state=page.evaluate('eduSimulator.state()');assert state['history']==history and state['current']<0
 page.locator('#dt').fill('0.1');page.locator('#advance').click();state=page.evaluate('eduSimulator.state()');assert abs(state['voltage']-10*(1-math.exp(-1.5))*math.exp(-1))<1e-6
 page.locator('#reset').click();state=page.evaluate('eduSimulator.state()');assert state['time']==0 and state['voltage']==0 and state['history']==[[0,0]] and abs(state['current']-.005)<1e-12
 page.locator('#dt').fill('2');page.locator('#advance').click();assert int(page.locator('#plot').get_attribute('data-samples'))==201
 points=page.locator('#curve').get_attribute('points').split();x,y=map(float,points[100].split(','));assert abs((320-y)/29-10*(1-math.exp(-5)))<1e-6
 page.screenshot(path=str(B/'20/correct_simulator.png'),full_page=True)
 shutil.copyfile(scratch/'20/simulator.html',B/'20/correct_simulator.html')
 report={'browser':'chromium headless','network':'blocked','checks':['four SVG states','charge advance via button','mode/resistance continuity and preserved history','discharge advance via button','reset defaults','201 rendered samples','t=1 rendered coordinate matches 9.932621V'],'console_errors':errors,'status':'passed' if not errors else 'failed'}
 (B/'20/browser_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');assert not errors
 browser.close();print(json.dumps(report,ensure_ascii=False))
