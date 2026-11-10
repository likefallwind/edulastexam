"""Trusted slides JSON -> editable PPTX -> rendered PDF; no model code execution."""
from __future__ import annotations
import json,math,re,subprocess,tempfile
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE

def parse(text):
    text=text.strip()
    if text.startswith('```'):
        m=re.search(r'```(?:json)?\s*([\s\S]*?)```',text);text=m.group(1) if m else text
    return json.loads(text)

def _text(slide,text,x,y,w,h,size=22,color='183D36',bold=False):
    box=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=box.text_frame
    tf.word_wrap=True;tf.auto_size=MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    tf.margin_left=tf.margin_right=Inches(.02)
    for i,line in enumerate(text.split('\n')):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='Noto Sans CJK SC';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(14)
    return box

def _render(d,out):
    prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
    for idx,s in enumerate(d['slides']):
        slide=prs.slides.add_slide(prs.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=RGBColor.from_string('F5F5EF')
        _text(slide,s['title'],.65,.5,12,.85,32,bold=True)
        _text(slide,'\n'.join(s['body']),.7,1.7,5.9,3.5,23)
        groups=s['groups'];bottom=4.8
        for j,g in enumerate(groups):
            h=2.2*g['mean']/100;x=7.35+j*2.45
            shape=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(bottom-h),Inches(1.2),Inches(h));shape.fill.solid();shape.fill.fore_color.rgb=RGBColor.from_string('2C6E61' if j==0 else 'AD6942');shape.line.fill.background()
            _text(slide,str(g['mean'])+'分',x-.2,bottom-h-.5,1.7,.4,21,bold=True)
            _text(slide,g['label']+'\n'+str(g['n'])+'人',x-.2,bottom+.15,1.9,.85,18)
        _text(slide,'班级均分（0–100分）',7.15,1.55,5.1,.5,18)
        if s['kind'] in ['explain','answer']:
            _text(slide,s['worked_calculation']+'\n合并均分：'+str(s['combined_mean'])+'分',.7,6.0,11.8,.8,21,bold=True)
        _text(slide,'来源：'+', '.join(s['source_ids'])+'   |   '+str(idx+1)+'/4',.7,7.0,12,.3,11,color='52665E')
    pptx=out/'lesson.pptx';prs.save(pptx)
    # Read back the real editable file; fields were not rasterized.
    actual=Presentation(pptx)
    assert len(actual.slides)==4
    text='\n'.join(sh.text for sl in actual.slides for sh in sl.shapes if sh.has_text_frame)
    assert all(s['title'] in text for s in d['slides'])
    (out/'extracted_text.txt').write_text(text)
    with tempfile.TemporaryDirectory(prefix='lo-profile-',dir=out) as profile:
        cmd=['/usr/bin/libreoffice','-env:UserInstallation='+Path(profile).resolve().as_uri(),'--headless','--convert-to','pdf','--outdir',str(out),str(pptx)]
        r=subprocess.run(cmd,text=True,capture_output=True,timeout=90)
        (out/'render.log').write_text(r.stdout+'\n'+r.stderr)
        if r.returncode or not (out/'lesson.pdf').is_file():raise RuntimeError('PPTX saved, but LibreOffice PDF rendering did not complete.')
    subprocess.run(['/usr/bin/pdftoppm','-png','-scale-to','1200',str(out/'lesson.pdf'),str(out/'slide')],check=True,capture_output=True,timeout=60)
    images=sorted(out.glob('slide-*.png'))
    if len(images)!=4:raise RuntimeError('Rendered slide count is not four.')
    return ['lesson.pptx','lesson.pdf','extracted_text.txt',*[p.name for p in images]]

def validate_artifact(response_text,output_dir,prompt_id):
    checks=[];out=Path(output_dir).resolve();out.mkdir(parents=True,exist_ok=True)
    try:
        d=parse(response_text);slides=d['slides'];assert isinstance(slides,list) and len(slides)==4,'slides must contain four pages'
        expected_kinds=['intro','explain','practice','answer'];assert [s['kind'] for s in slides]==expected_kinds,'page kinds/order differ from contract'
        first=[(20,90),(20,70)] if prompt_id=='equal' else [(10,90),(30,70)]
        for i,s in enumerate(slides):
            assert isinstance(s['title'],str) and s['title'].strip(),'empty title'
            assert isinstance(s['body'],list) and 1<=len(s['body'])<=4 and all(isinstance(b,str) and b.strip() for b in s['body']),'body must contain 1–4 nonempty strings'
            groups=s['groups'];assert len(groups)==2,'two source groups required'
            expected=first if i<2 else [(12,60),(18,80)]
            values=[(g['n'],g['mean']) for g in groups]
            checks.append({'name':f'page_{i+1}_source_data','passed':values==expected})
            checks.append({'name':f'page_{i+1}_source_ids','passed':s['source_ids']==(['D1'] if i<2 else ['D2'])})
            assert all(isinstance(g['label'],str) and g['label'].strip() and all(isinstance(g[k],(int,float)) and not isinstance(g[k],bool) and math.isfinite(g[k]) for k in ['n','mean']) for g in groups),'invalid groups'
            if i in [1,3]:
                assert isinstance(s['combined_mean'],(int,float)) and math.isfinite(s['combined_mean']),'numeric mean required'
                expected_mean=sum(n*m for n,m in expected)/sum(n for n,m in expected)
                checks.append({'name':f'page_{i+1}_combined_mean','passed':abs(s['combined_mean']-expected_mean)<1e-8})
                assert isinstance(s['worked_calculation'],str) and s['worked_calculation'].strip(),'worked calculation required'
            if i==2:
                leak='combined_mean' in s or 'worked_calculation' in s or bool(re.search(r'(?<!\d)72(?:\.0)?(?!\d)',' '.join(s['body'])+' '+s['title']))
                checks.append({'name':'practice_answer_withheld','passed':not leak})
        if not all(c['passed'] for c in checks):
            return {'passed':False,'checks':checks,'public_feedback':'源数据、合并均分、引用或练习展示不符合任务合同；请自行复核。','semantic_review_required':True}
        (out/'slides.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        artifacts=_render(d,out);checks.append({'name':'editable_pptx_and_four_rendered_pages','passed':True})
        return {'passed':True,'checks':checks,'artifacts':artifacts,'public_feedback':'四页PPTX已生成并渲染；数值和数据结构检查通过。教学解释与视觉可读性另行审阅。','semantic_review_required':True}
    except (ValueError,TypeError,KeyError,AssertionError,RuntimeError,subprocess.SubprocessError,OSError) as e:
        return {'passed':False,'checks':checks,'public_feedback':str(e),'semantic_review_required':True,'environment_error':isinstance(e,(subprocess.SubprocessError,OSError,RuntimeError))}
