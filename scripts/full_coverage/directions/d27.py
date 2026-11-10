"""Deterministic structural/math checks for a full lesson plan, not teacher rating."""
import json,re,math
from fractions import Fraction
from pathlib import Path

def parse(text):
    text=text.strip()
    if text.startswith('```'):
        m=re.search(r'```(?:json)?\s*([\s\S]*?)```',text);text=m.group(1) if m else text
    return json.loads(text)

def validate_artifact(response_text,output_dir,prompt_id):
    checks=[]
    try:
        d=parse(response_text)
        activities=d['activities']
        assert isinstance(activities,list) and 1<=len(activities)<=12,'activities must contain 1–12 steps'
        total=0
        for a in activities:
            m=a['minutes'];assert isinstance(m,(int,float)) and not isinstance(m,bool) and math.isfinite(m) and m>0,'minutes must be positive finite numbers'
            total+=m
            for k in ['teacher_action','student_action','evidence','materials']:assert a.get(k),'activity missing '+k
        checks.append({'name':'duration_20_minutes','passed':abs(total-20)<1e-8,'observed':total})
        for k in ['title','objectives','worked_example','independent_check','contingencies','source_ids']:assert d.get(k),'missing '+k
        for k in ['worked_example','independent_check']:
            e=d[k];m=re.fullmatch(r'\s*(\d+)/(\d+)\s*\+\s*(\d+)/(\d+)\s*',str(e['problem']));a=re.fullmatch(r'\s*(\d+)/(\d+)\s*',str(e['answer']))
            assert m and a,'problem must use a/b+c/d and answer p/q, as specified'
            x,y,z,w=map(int,m.groups());v,q=map(int,a.groups());expected=Fraction(x,y)+Fraction(z,w)
            checks.append({'name':k+'_arithmetic','passed':Fraction(v,q)==expected})
        ids=d['source_ids'];checks.append({'name':'source_identifiers','passed':isinstance(ids,list) and bool(ids) and all(s in ['F1','F2','F3','F4'] for s in ids)})
        passed=all(c['passed'] for c in checks)
        out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);(out/'lesson.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        return {'passed':passed,'checks':checks,'public_feedback':'结构与可计算条件已检查。'+('检查通过；教学针对性另由语义审阅评价。' if passed else '存在课时、来源标识或练习算术不符合合同，请重新核对。'),'artifacts':['lesson.json'],'semantic_review_required':True,'scope':'duration_and_explicit_math_only'}
    except (ValueError,TypeError,KeyError,AssertionError,ZeroDivisionError) as e:
        return {'passed':False,'checks':checks,'public_feedback':str(e),'semantic_review_required':True}
