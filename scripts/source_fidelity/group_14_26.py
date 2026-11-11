"""Adapters preserving native metric scales and explicitly pending native judges."""
from __future__ import annotations
import ast
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import unicodedata

BASE='sources/datasets/edu_last_exam_source_fidelity_v1/group_14_26'

def interact_runtime(root):
    config=json.loads((Path(root)/'data/edu_last_exam_source_fidelity_v1/runtime_environment.json').read_text())['interactscience_node_runtime']
    runtime=Path(config['path']);lock=runtime/'package-lock.json'
    if hashlib.sha256(lock.read_bytes()).hexdigest()!=config['lock_sha256']:raise ValueError('InteractScience runtime lock identity changed')
    modules=runtime/'node_modules';browsers=Path(config['browser_path'])
    if json.loads((modules/'@playwright/test/package.json').read_text())['version']!=config['playwright']:raise ValueError('Native Playwright version changed')
    return modules,browsers,config

def load_python(path):
    spec=importlib.util.spec_from_file_location('source_'+hashlib.sha256(str(path).encode()).hexdigest()[:12],path)
    if spec.name in sys.modules:return sys.modules[spec.name]
    obj=importlib.util.module_from_spec(spec);sys.modules[spec.name]=obj;spec.loader.exec_module(obj);return obj

def native_functions(path, names=None):
    """Load only trusted source definitions, without provider imports or side effects."""
    tree=ast.parse(Path(path).read_text())
    nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.Assign,ast.AnnAssign)) and (names is None or getattr(n,'name','') in names or (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)))]
    ns={'re':re,'unicodedata':unicodedata,'Any':object,'Optional':__import__('typing').Optional,'Message':object,'List':list,'Dict':dict}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
    return ns

def _choice(text,root):
    return load_python(Path(root)/BASE/'selfcheck_calibration/choice_parsing.py').extract_single_choice(text,'ABCD')

def score(task,result,call,directory,root):
    kind=task['scoring']['args']['kind'];text=result.get('response','');r=task['reference'];metrics={}
    base=Path(root)/BASE
    if kind=='asap':
        matches=re.findall(r'-?\d+',text.lower().rsplit('</think>',1)[-1]);pred=int(matches[-1]) if matches else None
        if pred not in range(1,7): pred=None
        metrics={'rating':pred,'human_rating':r['score'],'qwk_pair':[r['score'],pred],'absolute_error':abs(pred-r['score']) if pred is not None else None,'unparsed':pred is None}
    elif kind=='socratic':
        import sacrebleu
        refs=native_functions(base/'mathtutorbench/extraction.py')['extract_ground_truth_questions'](r['answer'])
        predictions=[x.strip() for x in text.split('\n')]
        vals=[sacrebleu.sentence_bleu(x,refs).score for x in predictions] if refs else []
        metrics={'bleu':max(vals)/100 if vals else 0.0,'avg_questions':min(len(predictions),len(refs)),'reference_questions':refs}
    elif kind=='mooccube':
        fn=native_functions(base/'mooccube/mooccube_prereq.py',{'_SEP','_parse_letter','_parse_order'})
        if r['task']=='mcq':
            pred=fn['_parse_letter'](text);metrics={'correct':bool(pred) and pred==r['gold_key'],'prediction':pred,'gold':r['gold_key'],'unparsed':not bool(pred),'chance':r['chance'],'task':'mcq'}
        else:
            names=[c['name'] for c in r['concepts']];seq=fn['_parse_order'](text,names,{c['name']:c.get('definition','') for c in r['concepts']});pos={x:i for i,x in enumerate(seq)};lookup={c['concept_id']:c['name'] for c in r['concepts']}
            n=sum(pos[lookup[a]]<pos[lookup[b]] for a,b in r['edges']) if seq else 0
            metrics={'correct':bool(seq) and n==len(r['edges']),'prediction':seq,'unparsed':not bool(seq),'n_satisfied':n,'n_constraints':len(r['edges']),'constraint_accuracy':n/len(r['edges']),'chance':r['chance'],'task':'order'}
    elif kind in {'selfcheck','calibration'}:
        answer_text=text
        if kind=='calibration':
            parser=native_functions(base/'selfcheck_calibration/p08_calibration.py',{'_ANSWER_LINE_RE','_answer_source'})
            answer_text=parser['_answer_source'](text)
        pred=_choice(answer_text,root);correct=pred==r['answer'];metrics={'correct':correct,'prediction':pred,'gold':r['answer'],'unparsed':not bool(pred)}
        if kind=='selfcheck':
            first=result['transcript'][0]['response'];p1=_choice(first,root);c1=p1==r['answer']
            metrics.update(r1_prediction=p1,r1_correct=c1,r2_correct=correct,changed=p1!=pred,transition=('right' if c1 else 'wrong')+'->'+('right' if correct else 'wrong'))
        else:
            ns=native_functions(base/'selfcheck_calibration/p08_calibration.py',{'_CONF_RE','parse_confidence'});confidence=ns['parse_confidence'](text)
            metrics.update(confidence=confidence,brier=(confidence/100-int(correct))**2 if confidence is not None else None,high_confidence_wrong=(confidence>=90 and not correct) if confidence is not None else None,high_confidence_threshold=90,calibration_pair=[confidence,correct])
    elif kind=='teacha':
        path=Path(root)/'sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/teacha/evaluator/evaluator_response_content.py'
        ns=native_functions(path)
        checks=r['evaluation_criteria']['response_checks']
        outcomes=[ns['_check_contains_any'](text,c['values'],c.get('case_insensitive',True)) for c in checks]
        return {'status':'native_score_pending','native_metric':task['scoring']['native_metric'],'metrics':{'response_check_reward':sum(outcomes)/len(outcomes),'response_checks':outcomes},'reason':'原 NL assertion judge 未运行；确定性 RESPONSE_CHECK 仅占 Stage1 0.55 权重，不代替完整原分。','required_native_judge':'TeachArena original multi-model NL assertion evaluator; evaluator_nl_assertions.py'}
    elif kind=='lda':
        ns=load_python(Path(root)/task['scoring']['args']['prompting_path']);lo,hi=r['scale']
        values={x['probe']:ns.parse_score(x.get('response',''),lo,hi) for x in result['transcript']}
        delta=lambda a,b: values[a]-values[b] if values.get(a) is not None and values.get(b) is not None else None
        metrics={'scores':values,'high_minus_low':delta('ctx_high','ctx_low'),'neutral_minus_base':delta('ctx_neutral','base'),'pair_id':r['id'],'scale':[lo,hi],'human_mean':sum(r['human'].values())/len(r['human'])}
    elif kind in {'distractor','eduillustrate','interactscience'}:
        return score_artifact(task,result,call,directory,root)
    else: raise ValueError(kind)
    return {'status':'scored_native','native_metric':task['scoring']['native_metric'],'metrics':metrics}

def validate(task,root):
    kind=task['scoring']['args']['kind'];checks=['source files are hashed by core validator','gold only in reference; selection before model predictions']
    if kind=='socratic':
        import sacrebleu
        assert abs(sacrebleu.sentence_bleu('How many eggs?', ['How many eggs?']).score-100)<1e-9
    elif kind in {'selfcheck','calibration'}:
        assert _choice('答案：B',root)=='B'
        assert _choice('Because the result is ambiguous',root)==''
    elif kind=='mooccube':
        f=native_functions(Path(root)/BASE/'mooccube/mooccube_prereq.py',{'_SEP','_parse_letter','_parse_order'})
        assert f['_parse_letter']('答案：C')=='C'
        assert f['_parse_order']('答案：a -> b',['a','b'])==['a','b']
        assert f['_parse_order']('答案：a -> x -> b',['a','b'])==[]
    elif kind=='teacha':
        assert task['reference']['id']=='EI-C04'
        ns=native_functions(Path(root)/'sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/teacha/evaluator/evaluator_response_content.py')
        assert ns['_check_contains_any']('There are multiple defensible answers',['multiple defensible'])
    elif kind=='lda':
        probes=task['prediction']['interaction']['args']['variants'];assert [x['probe'] for x in probes]==['base','ctx_neutral','ctx_low','ctx_high']
        assert task['reference']['scale']==[0,5]
    elif kind=='eduillustrate':
        d=Path(root)/BASE/'eduillustrate';p=load_python(d/'task_generator/__init__.py');cfg=task['prediction']['interaction']['args']
        assert task['prediction']['messages'][0]['content'][0]['text']==p.get_prompt_scene_plan(cfg['topic'],cfg['description'])
        assert Path('/home/likefallwind/code/EduIllustrate/.venv/bin/python').is_file()
        assert cfg['max_code_fixes']==2
        checks.append('native compiled prompt identity; original 2 fixes (3 rendering attempts); separate isolated two-scene fixture passed')
    elif kind=='interactscience':
        d=Path(root)/BASE/'interactscience';r=task['reference'];assert task['prediction']['messages'][0]['content'][0]['text']==r['lm_system_prompt']+r['question']
        modules,browsers,config=interact_runtime(root)
        assert (modules/'@playwright/test/cli.js').is_file()
        assert (browsers/('chromium-'+config['chromium_revision'])).is_dir()
        assert all((d/view/(r['id']+'.spec.js')).is_file() for view in ['PFT_tests','VQT_tests'])
        checks.append('original prompt and test files; fixed Playwright 1.53.0/Chromium1178; no-network browser fixture passed')
    return {'passed':True,'checks':checks}

def score_artifact(task,result,call,directory,root):
    kind=task['scoring']['args']['kind']
    if kind=='interactscience':return score_interactscience(task,result,directory,root)
    metrics={}
    if kind=='distractor':
        parser=native_functions(Path(root)/BASE/'distractor/src/models/impl/naive_cot.py',{'parse_joint_output'})['parse_joint_output']
        parsed=parser(result['response']);metrics={'parsed_distractors':{k:v for k,v in parsed.items() if k.endswith('_answer')}}
    elif kind=='eduillustrate':metrics=result.get('render_metrics',{})
    return {'status':'native_score_pending','native_metric':task['scoring']['native_metric'],'metrics':metrics,'required_model':'gpt-4.1-mini' if kind=='distractor' else 'gemini-3-pro-preview','reason':'Original semantic/visual judge is retained in source snapshot and not silently substituted.'}

def aggregate(records,root):
    """Native within-view statistics only; undefined denominators remain null."""
    groups={}
    for row in records:
        n=row.get('case_id','').split('-')[2] if row.get('case_id','').startswith('ELE-SF-') else None
        if n and row.get('status')=='scored_native':groups.setdefault(n,[]).append(row['metrics'])
    out={}
    for n,vals in groups.items():
        if n=='22':
            pairs=[v['qwk_pair'] for v in vals if v['rating'] is not None]
            qwk=native_functions(Path(root)/BASE/'asap_2/scoring.py',{'quadratic_weighted_kappa'})['quadratic_weighted_kappa']
            out[n]={'n':len(vals),'scorable':len(pairs),'qwk':qwk([x[0] for x in pairs],[x[1] for x in pairs],scale=(1,6)),'scale':[1,6]}
        elif n=='23':out[n]={'n':len(vals),'bleu':sum(v['bleu'] for v in vals)/len(vals),'avg_questions':sum(v['avg_questions'] for v in vals)/len(vals)}
        elif n=='25':
            right=[v for v in vals if v['r1_correct']];wrong=[v for v in vals if not v['r1_correct']]
            out[n]={'n':len(vals),'r1_right':len(right),'r1_wrong':len(wrong),'fix_rate':sum(v['r2_correct'] for v in wrong)/len(wrong) if wrong else None,'break_rate':sum(not v['r2_correct'] for v in right)/len(right) if right else None}
        elif n=='26':
            pairs=[tuple(v['calibration_pair']) for v in vals if v['confidence'] is not None]
            f=native_functions(Path(root)/BASE/'selfcheck_calibration/p08_calibration.py',{'_cwr','_ece','_brier','_auroc','_selective_accuracy'})
            out[n]={'n':len(vals),'n_with_confidence':len(pairs),'cwr_at_90':f['_cwr'](pairs),'ece_10bin':f['_ece'](pairs) if pairs else None,'brier':f['_brier'](pairs) if pairs else None,'auroc':f['_auroc']([p[0] for p in pairs],[p[1] for p in pairs]),'selective_accuracy':f['_selective_accuracy'](pairs) if pairs else None}
    for result in out.values():result['scope']='three preselected source cases; descriptive only, no population validation'
    return out

def run(task,call,directory,root):
    kind=task['prediction']['interaction']['args']['kind']
    if kind=='lda':
        transcript=[]
        for v in task['prediction']['interaction']['args']['variants']:
            answer=call(v['messages'],purpose='prediction',parameters=task['prediction']['parameters'])
            transcript.append(dict(probe=v['probe'],messages=v['messages'],**answer))
            if answer['status']!='generated':return dict(status=answer['status'],response=answer.get('response',''),transcript=transcript)
        return dict(status='generated',response=json.dumps({x['probe']:x['response'] for x in transcript},ensure_ascii=False),transcript=transcript)
    if kind=='eduillustrate': return run_eduillustrate(task,call,directory,root)
    raise ValueError(kind)

def run_eduillustrate(task,call,directory,root):
    """Original sequential anchoring workflow, with all arbitrary code isolated."""
    from .isolation import isolated_run
    root=Path(root);directory=Path(directory);work=directory/'eduillustrate';work.mkdir(parents=True,exist_ok=True)
    d=root/BASE/'eduillustrate';p=load_python(d/'task_generator/__init__.py');raw=load_python(d/'task_generator/prompts_raw/__init__.py')
    util=native_functions(d/'src/utils/utils.py',{'extract_xml','parse_scene_outline_tokens'})
    cfg=task['prediction']['interaction']['args'];description=cfg['description'];topic=cfg['topic'];transcript=[]
    image_uri='data:image/png;base64,'+base64.b64encode((root/cfg['image_path']).read_bytes()).decode()
    def ask(prompt,stage,with_image=False,purpose='prediction'):
        content=[dict(type='text',text=prompt)]
        if with_image:content.append({'type':'image_url','image_url':{'url':image_uri}})
        msgs=[dict(role='user',content=content)];a=call(msgs,purpose=purpose,parameters=task['prediction']['parameters']);transcript.append(dict(stage=stage,messages=msgs,**a))
        if a['status']!='generated':raise RuntimeError('API stage '+stage+': '+a['status'])
        return a['response']
    def extract(response,stage):
        # Verbatim parser/format retry contract from CodeGenerator._extract_code_with_retries.
        template="""
        Please extract the Python code in the correct format using the pattern: {pattern}.\x20
        You MUST NOT include any other text or comments.\x20
        You MUST return the exact same code as in the previous response, NO CONTENT EDITING is allowed.
        Previous response:\x20
        {response_text}
        """
        pattern=r'```python(.*)```'
        for attempt in range(10):
            cleaned=re.sub(r'<think>.*?</think>','',response,flags=re.S|re.I)
            blocks=[b for b in re.findall(r'```python\s*\n?(.*?)```',cleaned,re.S) if b.strip()]
            if blocks:return max(blocks,key=len).rstrip('\n')
            match=re.search(pattern,cleaned,re.S)
            if match and match.group(1).strip():return match.group(1)
            if attempt<9:response=ask(template.format(pattern=pattern,response_text=response),stage+f'_format_retry_{attempt+1}',purpose='extraction')
        raise ValueError('Original code extraction failed after 10 attempts')
    outline=ask(p.get_prompt_scene_plan(topic,description),'scene_outline',True);(work/'outline.txt').write_text(outline)
    tokens=util['parse_scene_outline_tokens'](outline);scenes=sorted({t['k'] for t in tokens if t['type']=='scene'})
    rendered={};render_results=[];scene1_code=None;artifacts=[]
    no_diagrams=[t['k'] for t in tokens if t['type']=='scene' and 'no diagram' in t['content'].lower()]
    if no_diagrams:
        for i in no_diagrams:
            target=work/f'scene{i}.png';shutil.copy2(root/cfg['image_path'],target);rendered[i]=target.name
    else:
        for i in scenes:
            scene=next(t['content'] for t in tokens if t['type']=='scene' and t['k']==i)
            if i==1:implementation=ask(p.get_prompt_scene_design_and_implementation(i,description,scene),'scene1_implementation',True)
            else:implementation=f'<REFERENCE_TO_SCENE_1>Scene {i} will be generated based on Scene 1 code for consistency</REFERENCE_TO_SCENE_1>'
            context=[raw._prompt_manim_cheatsheet,raw._code_font_size,raw._code_limit,raw._code_disable]
            if i>1:
                if scene1_code is None:break
                context.append(f"""
**Reference Code from Scene 1** (for style consistency):
Use the same visual style, color scheme, and layout principles as Scene 1.

```python
{scene1_code}
```

IMPORTANT: Maintain consistency with Scene 1:
- Use the same background color
- Use the same stroke widths and font sizes
- Use similar object positioning and spacing
- Follow the same code structure and organization
""")
            answer=ask(p.get_prompt_code_generation(topic,description,outline,implementation,i,context),f'scene{i}_code',i==1)
            try:code=extract(answer,f'scene{i}')
            except ValueError as e:
                render_results.append(dict(scene=i,rendered=False,error=str(e)));break
            success=False
            for attempt in range(cfg['max_code_fixes']+1):
                codefile=work/f'scene{i}_v{attempt}.py';codefile.write_text(code)
                readonly=['/home/likefallwind/code/EduIllustrate/.venv','/etc/texmf','/var/lib/texmf']
                command=['/home/likefallwind/code/EduIllustrate/.venv/bin/python','-m','manim','-ql','-s','/work/'+codefile.name,f'Scene{i}','--media_dir','/work/media','--progress_bar','none']
                r=isolated_run(command,work,readonly_paths=[x for x in readonly if Path(x).exists()],timeout=180,env={'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},report_path=work/f'scene{i}_v{attempt}_render.json')
                images=sorted((work/'media/images'/codefile.stem).glob('*.png'))
                success=r['returncode']==0 and bool(images)
                render_results.append(dict(scene=i,attempt=attempt,rendered=success,returncode=r['returncode'],timed_out=r['timed_out']))
                if success:
                    target=work/f'scene{i}.png';shutil.copy2(images[-1],target);rendered[i]=target.name
                    if i==1:scene1_code=code
                    break
                if attempt<cfg['max_code_fixes']:
                    error=r['stderr'] or 'Manim produced no PNG frame.'
                    answer=ask(p.get_prompt_fix_error(implementation,code,error),f'scene{i}_fix_{attempt+1}')
                    try:code=extract(answer,f'scene{i}_fix_{attempt+1}')
                    except ValueError:break
            if i==1 and not success:break
    md='# '+topic+'\n\n'
    for t in tokens:
        if t['type']=='text':md+='\n'.join(x.lstrip() for x in t['content'].strip('\n').splitlines()).strip()+'\n\n'
        elif t['k'] in rendered:md+=f"![Scene {t['k']}]({rendered[t['k']]})\n\n"
        else:md+=f"<!-- Scene {t['k']} rendering unavailable -->\n\n"
    (work/'solution.md').write_text(md)
    artifacts=[str(x.relative_to(directory)) for x in work.rglob('*') if x.is_file()]
    return dict(status='generated',response=md,transcript=transcript,artifacts=artifacts,render_metrics={'scenes_planned':len(scenes),'scenes_rendered':len(rendered),'render_attempts':render_results,'all_scenes_rendered':bool(scenes) and len(rendered)==len(scenes),'scene_image_metric_meaning':'scenes_rendered/all_scenes_rendered count available scene images, including the original problem-image fallback when the upstream outline says No diagram; they do not necessarily imply Manim execution success. Inspect render_attempts for actual Manim results.','fallback_image_scenes':no_diagrams,'document_rubric':'pending original Gemini 3.0 Pro Preview judge'})

def score_interactscience(task,result,directory,root):
    from .isolation import isolated_run
    root=Path(root);directory=Path(directory);d=root/BASE/'interactscience';work=directory/'interactscience';work.mkdir(parents=True,exist_ok=True)
    extractor=load_python(d/'extract_and_save_code.py');code=extractor.extract_code_block(result['response'],'html');ident=task['reference']['id']
    if code is None:return {'status':'scored_native','native_metric':'PFT artifact availability','metrics':{'html_extracted':False},'reason':'Original extractor found no html fence; no runnable artifact.'}
    (work/'pages').mkdir(exist_ok=True);(work/'original.html').write_text(code)
    manifest=json.loads((d/'vendor/manifest.json').read_text());cached={v['url']:v for v in manifest};missing=[];replacements=[]
    def localize(match):
        url=match.group(2)
        if not url.startswith(('http://','https://','//')):return match.group(0)
        v=cached.get(url)
        if not v:missing.append(url);return match.group(0)
        source=root/v['path'];vendor=work/'vendor';vendor.mkdir(exist_ok=True);shutil.copy2(source,vendor/source.name);replacements.append({'url':url,'sha256':v['sha256']})
        return match.group(1)+'../vendor/'+source.name+match.group(3)
    # Preserve submitted code; runtime copy rewrites only exact cached script URLs.
    runtime=re.sub(r'(<script\b[^>]*\bsrc\s*=\s*[\"\x27])([^\"\x27]+)([\"\x27])',localize,code,flags=re.I)
    (work/'dependency_resolution.json').write_text(json.dumps({'replacements':replacements,'missing':missing},indent=2))
    if missing:return {'status':'native_score_pending','native_metric':task['scoring']['native_metric'],'metrics':{'html_extracted':True},'reason':'Uncached external script dependencies in isolated original environment','missing_dependencies':missing}
    (work/'pages'/f'{ident}.html').write_text(runtime)
    node_modules,browsers,_=interact_runtime(root)
    if not (work/'node_modules').exists():(work/'node_modules').symlink_to(node_modules,target_is_directory=True)
    for view in ('PFT','VQT'):
        (work/(view+'_tests')).mkdir(exist_ok=True);shutil.copy2(d/(view+'_tests')/(ident+'.spec.js'),work/(view+'_tests')/(ident+'.spec.js'));shutil.copy2(d/f'playwright_{view}.config.js',work/f'playwright_{view}.config.js')
    metrics={'html_extracted':True};reports={}
    for view in ('PFT','VQT'):
        r=isolated_run(['/usr/bin/node',str(node_modules/'@playwright/test/cli.js'),'test','--workers=1','--reporter=json','--config',f'playwright_{view}.config.js'],work,readonly_paths=[node_modules,browsers],timeout=240,env={'PLAYWRIGHT_BROWSERS_PATH':str(browsers),'PLAYWRIGHT_JSON_OUTPUT_NAME':f'/work/{view}_results.json'},report_path=work/f'{view}_execution.json')
        report=work/f'{view}_results.json';reports[view]={'returncode':r['returncode'],'timed_out':r['timed_out']}
        if report.exists():
            data=json.loads(report.read_text());tests=[]
            def visit(s):
                for spec in s.get('specs',[]):tests.extend(spec.get('tests',[]))
                for child in s.get('suites',[]):visit(child)
            visit(data);passed=sum(any(z.get('status')=='passed' for z in t.get('results',[])) for t in tests)
            metrics[view.lower()]={'passed':passed,'total':len(tests),'rate':passed/len(tests) if tests else None,'perfect':passed==len(tests) if tests else None,'global_errors':data.get('errors',[])}
    return {'status':'native_score_pending','native_metric':task['scoring']['native_metric'],'metrics':metrics,'execution':reports,'reason':'PFT and VQT action execution retained; Gemini-2.5-Pro visual checklist and original CLIP scoring remain pending. PFT passing is not scientific correctness.','artifacts':[str(x.relative_to(directory)) for x in work.rglob('*') if x.is_file()]}
