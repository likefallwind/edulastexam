"""Validate a bounded scientific diagram specification and render trusted SVG."""
import html,json,math,re
from pathlib import Path

def parse(text):
    try:return json.loads(text)
    except (ValueError,TypeError):pass
    for m in re.finditer(r'```(?:json)?\s*([\s\S]*?)```',text):
        try:return json.loads(m.group(1))
        except ValueError:pass
    raise ValueError('Expected JSON diagram specification.')

def validate_artifact(response_text, output_dir, prompt_id):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True);checks=[]
    try:
        obj=parse(response_text);states=obj['states'];assert len(states)==4,'Exactly four states required.'
        assert obj.get('layout','horizontal') in {'horizontal','vertical'},'layout must be horizontal or vertical.'
        ids=['initial','touch','hot','cool'];expected=[(300,8,100,160,0),(375,10,100,200,0),(450,10,120,200,40),(330,8.8,100,176,0)]
        assert [s['id'] for s in states]==ids,'State ids/order must be initial,touch,hot,cool.'
        keys=['temperature_K','piston_height_cm','pressure_kPa','volume_cm3','stop_force_N']
        for s,g in zip(states,expected):
            for k,e in zip(keys,g):
                v=s[k];assert isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v),f'{s["id"]}.{k}: finite number required.'
                checks.append({'id':s['id']+'.'+k,'passed':abs(v-e)<=1e-5,'observed':v})
        cols=4 if obj.get('layout','horizontal')=='horizontal' else 1;rows=4//cols
        width=cols*260;height=rows*390
        parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>']
        for i,s in enumerate(states):
            x=(i%cols)*260;y=(i//cols)*390;h=s['piston_height_cm'];py=280-h*20
            assert 0<=h<=12,'Height outside drawable range.'
            parts.append(f'<g id="{s["id"]}" transform="translate({x},{y})"><text x="20" y="25" font-size="18">{html.escape(s["id"])}</text>')
            parts.append(f'<rect x="55" y="{py}" width="140" height="{h*20}" fill="#c7e8f4"/><path d="M55 40 V280 H195 V40" fill="none" stroke="#283747" stroke-width="3"/><path d="M45 80 H65 M185 80 H205" stroke="#bb3e03" stroke-width="5"/><path d="M52 {py} H198" stroke="#172b4d" stroke-width="7"/>')
            for j,(label,k,unit) in enumerate([('T','temperature_K','K'),('h','piston_height_cm','cm'),('P','pressure_kPa','kPa'),('V','volume_cm3','cm³'),('Fstop','stop_force_N','N')]):
                parts.append(f'<text x="18" y="{303+j*17}" font-size="14">{label}={s[k]:g} {unit}</text>')
            if s['stop_force_N']>0:parts.append(f'<path d="M125 42 V65 l-5 -8 M125 65 l5 -8" fill="none" stroke="#bb3e03" stroke-width="3"/>')
            parts.append('</g>')
        parts.append('</svg>');svg=''.join(parts)
        (out/'diagram.svg').write_text(svg);(out/'diagram.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
        checks.append({'id':'trusted_svg_render_source','passed':True})
        return {'passed':all(c['passed'] for c in checks),'checks':checks,'artifacts':['diagram.svg','diagram.json'],'public_feedback':{'checks':[{'id':c['id'],'passed':c['passed']} for c in checks],'note':'几何、标签和图示由你给出的状态生成；修复可根据公开物理条件重新计算。'},'scope':'bounded_declarative_diagram; pedagogical_readability_requires_review'}
    except (ValueError,TypeError,KeyError,AssertionError,OverflowError) as exc:
        return {'passed':False,'checks':checks+[{'id':'schema_and_render','passed':False,'detail':str(exc)}],'public_feedback':str(exc)}
