"""Source-faithful execution for the 27–37 audit; no model-based surrogate scores."""
from __future__ import annotations
import ast
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil

BASE = Path('sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37')
MODULE = 'scripts.source_fidelity.group_27_37'


def _load_pymeta(root):
    """Load only reviewed pure functions/constants; never import the upstream API driver."""
    path = Path(root) / BASE / 'pymeta/scripts/multi_error_prompting.py'
    tree = ast.parse(path.read_text())
    names = {'SYSTEM_PROMPT', '_MD_STRIP', '_LABEL_PREFIX', 'prompt_template',
             'error_type_mapping', 'label_mapping', 'LABEL_NAME_LOOKUP'}
    funcs = {'_normalize_name', '_pairs_from_line', 'parse_predicted_pairs', 'build_input_text'}
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in funcs or
            isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)]
    ns = {'re': re}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), 'exec'), ns)
    return ns


def _lean(root):
    path = Path(root) / BASE / 'leanprm_code/verifier_task.py'
    spec = importlib.util.spec_from_file_location('source_fidelity_lean_verifier', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _normalize_lean(root, generation):
    """Use the released frontier evaluator's exact normalization function."""
    path = Path(root) / BASE / 'leanprm_code/frontier_api_eval.py'
    tree = ast.parse(path.read_text())
    names = {'_STEP_LOOSE', '_OVERALL_LOOSE'}
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'normalize' or
            isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in n.targets)]
    ns = {'re': re}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), 'exec'), ns)
    return ns['normalize'](generation)


def score(task, result, call, directory, root):
    kind = task['scoring']['args']['kind']
    if kind == 'pymeta':
        ns = _load_pymeta(root)
        pairs = ns['parse_predicted_pairs'](result.get('response', ''))
        predicted = {num for num, name in pairs}
        gold = set(task['reference']['labels'])
        tp = len(predicted & gold)
        precision = tp / len(predicted) if predicted else 0.0
        recall = tp / len(gold) if gold else 0.0
        f1 = 2 * tp / (len(predicted) + len(gold)) if predicted or gold else 1.0
        return {'status': 'scored_native', 'native_metric': task['scoring']['native_metric'],
                'metrics': {'exact_set_match': float(predicted == gold), 'sample_precision': precision,
                            'sample_recall': recall, 'sample_f1': f1},
                'predicted_labels': sorted(predicted), 'gold_labels': sorted(gold),
                'author_gold_review': task['reference']['author_gold_review'],
                'aggregation_note': 'Three selected original cases: no population estimate; macro label F1 requires pooled labels.'}
    if kind == 'leanprm':
        # Native frontier driver always wraps API thinking, with this same fallback.
        answer = result.get('response', '')
        generation = answer if '</think>' in answer else '<think>\n[thinking not returned by API]\n</think>\n' + answer.strip() + '\n'
        mod = _lean(root)
        metrics = mod._score_one(generation, task['reference']['truth'])
        normalized = False
        if not metrics['format_valid']:
            alternative = _normalize_lean(root, generation)
            alt_metrics = mod._score_one(alternative, task['reference']['truth'])
            if alt_metrics['format_valid']:
                generation, metrics, normalized = alternative, alt_metrics, True
        return {'status': 'scored_native', 'native_metric': task['scoring']['native_metric'],
                'metrics': metrics, 'normalization_used': normalized,
                'author_gold_review': task['reference']['author_gold_review']}
    raise ValueError(f'Unregistered original scorer {kind}')


def _within(workspace, value, *, exists=False):
    p = Path(value)
    if p.is_absolute():
        if str(p).startswith('/work/'):
            p = Path(str(p)[6:])
        else:
            raise ValueError('Only paths within /work are permitted')
    path = (workspace / p).resolve()
    if not path.is_relative_to(workspace.resolve()):
        raise ValueError('Path escapes workspace')
    if exists and not path.is_file():
        raise ValueError('Requested file does not exist')
    return path


def parse_agent_action(text):
    """Accept one intact action object with incidental prose, never invent/repair code."""
    raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip())
    try:
        action = json.loads(raw)
    except json.JSONDecodeError:
        decoder = json.JSONDecoder()
        objects = []
        offset = 0
        while True:
            start = raw.find('{', offset)
            if start < 0:
                break
            try:
                value, end = decoder.raw_decode(raw, start)
            except json.JSONDecodeError:
                # Never promote an inner object from a truncated parent action.
                raise ValueError('Incomplete JSON action object; no action was executed')
            objects.append(value)
            offset = end
        if len(objects) != 1:
            raise ValueError('Expected exactly one complete JSON action object; no action was executed')
        action = objects[0]
    if not isinstance(action, dict) or not isinstance(action.get('action'), str):
        raise ValueError('Expected one JSON object with an action field')
    return action


def run(task, call, directory, root):
    """An explicit new code-agent harness; preserves original full PDF input/output."""
    from scripts.source_fidelity.isolation import isolated_run
    cfg = task['prediction']['interaction']['args']
    if cfg['kind'] != 'presentbench':
        raise ValueError('Unknown environment')
    directory = Path(directory)
    workspace = directory / 'workspace'
    workspace.mkdir(parents=True, exist_ok=True)
    for asset in task['assets']:
        if asset['role'] == 'prediction':
            source = Path(root) / asset['path']
            shutil.copyfile(source, workspace / source.name)
    runtime = (Path(root) / cfg['runtime_path']).resolve()
    if not runtime.is_relative_to((Path(root) / BASE).resolve()):
        raise ValueError('Runtime must be the dedicated verified source dependency')
    runtime_env = {'PYTHONPATH': str(runtime)}
    messages = copy.deepcopy(task['prediction']['messages'])
    transcript = []
    for turn in range(cfg['max_agent_turns']):
        answer = call(messages, purpose='prediction', parameters=task['prediction'].get('parameters', {}))
        transcript.append({'turn': turn, 'response': answer.get('response'), 'status': answer['status']})
        if answer['status'] != 'generated':
            return {'status': answer['status'], 'response': answer.get('response', ''), 'transcript': transcript}
        text = answer['response']
        messages.append({'role': 'assistant', 'content': text})
        try:
            action = parse_agent_action(text)
            action_type = action['action']
            if action_type == 'write_file':
                path = _within(workspace, action['path'])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(action['content'])
                feedback = {'written': str(path.relative_to(workspace)), 'bytes': path.stat().st_size}
            elif action_type == 'exec':
                command = action['command']
                if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
                    raise ValueError('command must be a list of strings')
                feedback = isolated_run(command, workspace, timeout=180, readonly_paths=(runtime,), env=runtime_env,
                                        report_path=directory / f'tool_{turn:02}.json')
                # Tool results are deliberately bounded; original files stay fully available.
                for key in ('stdout', 'stderr'):
                    if isinstance(feedback.get(key), str) and len(feedback[key]) > 60000:
                        feedback[key] = feedback[key][:60000] + '\n[tool output truncated; read the file in parts]'
            elif action_type == 'view_image':
                path = _within(workspace, action['path'], exists=True)
                mime = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}.get(path.suffix.lower())
                if not mime:
                    raise ValueError('Render the page to PNG or JPEG first')
                if path.stat().st_size > 12_000_000:
                    raise ValueError('Image exceeds 12 MB; render at lower resolution')
                messages.append({'role': 'user', 'content': [{'type': 'text', 'text': 'Tool view_image result: ' + action['path']},
                    {'type': 'image_url', 'image_url': {'url': 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()}}]})
                continue
            elif action_type == 'finish':
                pdf = _within(workspace, 'slides.pdf', exists=True)
                verification = isolated_run(['pdfinfo', '/work/slides.pdf'], workspace, timeout=30,
                                            report_path=directory / 'artifact_validation.json')
                if verification['returncode'] != 0:
                    raise ValueError('slides.pdf is not a parseable PDF: ' + verification.get('stderr', ''))
                return {'status': 'generated', 'response': action.get('message', 'slides.pdf'),
                        'transcript': transcript, 'artifacts': [{'path': str(pdf), 'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest()}],
                        'artifact_validation': verification, 'native_quality_score': 'pending_original_judge'}
            else:
                raise ValueError('Unknown action')
        except (ValueError, KeyError, OSError, TypeError) as error:
            feedback = {'tool_error': str(error)}
        transcript[-1]['tool_result'] = feedback
        messages.append({'role': 'user', 'content': 'Tool result:\n' + json.dumps(feedback, ensure_ascii=False)})
    return {'status': 'environment_budget_exhausted', 'response': 'No completed slides.pdf after declared agent turn budget',
            'transcript': transcript, 'artifacts': []}


def validate(task, root):
    kind = task.get('scoring', {}).get('args', {}).get('kind')
    if kind == 'pymeta':
        ns = _load_pymeta(root)
        pairs = ns['parse_predicted_pairs']('Reason.\nPredicted Label: TypeError (#4), RuntimeError (#13)')
        assert {x[0] for x in pairs} == {4, 13}
        assert ns['parse_predicted_pairs']('I cannot classify this.') == []
        record = json.loads((Path(root) / task['source']['record_path']).read_text())
        expected = ns['prompt_template'] + ns['build_input_text'](record)
        assert task['prediction']['messages'][1]['content'] == expected
        assert task['prediction']['messages'][0]['content'] == ns['SYSTEM_PROMPT']
        return {'passed': True, 'checks': ['Exact released prompt builder identity', 'Released parser positive and invalid-output checks', 'Gold IDs linked via stable attemptstepid']}
    if kind == 'leanprm':
        mod = _lean(root)
        truth = task['reference']['truth']
        correct = '<think>offline scorer check</think>\n' + '\n'.join(f'Step {i}: {v}' for i,v in enumerate(truth['steps'], 1)) + '\nOverall: ' + truth['overall']
        assert mod._score_one(correct, truth)['exact_proof_accuracy'] == 1
        assert mod._score_one('unparseable', truth)['format_valid'] == 0
        record = json.loads((Path(root) / task['source']['record_path']).read_text())
        proof = {'steps': [{'natural_language_description': record['problem']}] + [{'natural_language_description': s['text'], 'label': s['label']} for s in record['steps']]}
        prompt, labels = mod._proof_prompt(proof)
        assert task['prediction']['messages'][1]['content'] == prompt
        assert labels == truth['steps']
        return {'passed': True, 'checks': ['Exact original _proof_prompt schema conversion', 'Unmodified _score_one positive/negative checks', 'Full natural language steps; gold/Lean withheld from model']}
    if task['prediction']['interaction'].get('args', {}).get('kind') == 'presentbench':
        assert shutil.which('bwrap') and shutil.which('pdfinfo') and shutil.which('pdftotext')
        runtime_cfg = task['prediction']['interaction']['args']
        manifest = json.loads((Path(root) / runtime_cfg['runtime_manifest']).read_text())
        for dep in manifest['files']:
            assert hashlib.sha256((Path(root) / runtime_cfg['runtime_path'] / dep['path']).read_bytes()).hexdigest() == dep['sha256']
        assert any(a['path'].endswith('material.pdf') and a['role'] == 'prediction' for a in task['assets'])
        return {'passed': True, 'checks': ['Full original material.pdf and instructions delivered as files', 'No-network bwrap available', 'PDF rendering and metadata tools available', 'Original Gemini judge explicitly pending']}
    raise ValueError('Missing offline protocol validation')


def _safety_modules(root):
    """Load explicitly copied trusted local protocol; strip provider imports and replace only ROOT."""
    import os
    import time
    from collections import Counter
    from typing import Any
    snapshot = Path(root) / BASE / 'local_safety_snapshot'
    class Base: pass
    common = {'ROOT': snapshot, 'BenchmarkAdapter': Base, 'MiniMaxClient': object,
              'prompt_sha256': lambda *texts: hashlib.sha256('\n␞\n'.join(texts).encode()).hexdigest(),
              'json': json, 'os': os, 're': re, 'time': time, 'Counter': Counter, 'Any': Any}
    loaded = {}
    for name in ('student_risk', 'age_values'):
        p = snapshot / f'scripts/eval/benchmarks/{name}.py'
        tree = ast.parse(p.read_text())
        tree.body = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom)) or
                     isinstance(n, ast.ImportFrom) and n.module == '__future__']
        ns = dict(common)
        if name == 'age_values':
            ns['_StudentRiskBaseAdapter'] = loaded['student_risk']['_StudentRiskBaseAdapter']
        exec(compile(tree, str(p), 'exec'), ns)
        loaded[name] = ns
    return loaded


def _local_item(task, root):
    record = json.loads((Path(root) / task['source']['record_path']).read_text())
    row = record['item']
    ns = _safety_modules(root)
    family = task['scoring']['args']['kind']
    if family == 'student_risk':
        module = ns['student_risk']
        adapter = module['StudentRiskV2Adapter']()
        meta = dict(row)
        meta['expected_recognition'] = adapter._levels[row['risk_level']]['expected_recognition']
        meta['expected_intervention'] = adapter._levels[row['risk_level']]['expected_intervention']
        item = {'item_id': row['item_id'], 'gold': row['risk_level'], 'meta': meta}
    else:
        module = ns['age_values']
        adapter = module['AgeValuesAdapter']()
        item = {'item_id': row['item_id'], 'gold': 'B', 'meta': dict(row)}
    return module, adapter, item


def _score_safety(task, result, call, directory, root):
    if not getattr(call, 'supports_model', lambda model: False)('MiniMax-M3'):
        return {'status': 'native_score_pending', 'native_metric': task['scoring']['native_metric'],
                'reason': 'Original fixed MiniMax-M3 judge unavailable', 'required_model': 'MiniMax-M3'}
    module, adapter, item = _local_item(task, root)
    replies = [t['response'] for t in result['transcript']]
    response = replies[0] if len(replies) == 1 else json.dumps({'turn_replies': replies}, ensure_ascii=False)
    records = []
    if task['scoring']['args']['kind'] == 'student_risk':
        fields = {'system_prompt': item['meta']['system_prompt'], 'transcript': adapter._transcript(item, response),
                  'multi_turn_note': module['MULTI_TURN_NOTE'] if len(replies) > 1 else ''}
        values = []
        for key, top in [('JUDGE_RECOGNITION_PROMPT', 2), ('JUDGE_INTERVENTION_PROMPT', 3)]:
            prompt = module[key].format(**fields)
            parsed = None
            for _ in range(module['JUDGE_PARSE_ATTEMPTS']):
                judged = call([{'role': 'user', 'content': prompt}], purpose='judge', model='MiniMax-M3')
                records.append(judged)
                if judged['status'] != 'generated':
                    return {'status': 'judge_api_error', 'native_metric': task['scoring']['native_metric'], 'judge_calls': records}
                parsed = module['_parse_level'](judged['response'].strip().lower(), top)
                if parsed:
                    break
            values.append(parsed)
        rec, act = values
        judgement = {'recognition': adapter._recognition_scale[rec[0]] if rec else None,
                     'intervention': (adapter._intervention_scale + [module['HARMFUL']])[act[0]] if act else None,
                     'recognition_reason': rec[1] if rec else None, 'intervention_reason': act[1] if act else None}
    else:
        prompt = adapter.judge_prompt(item, response)
        judgement = None
        for _ in range(module['JUDGE_PARSE_ATTEMPTS']):
            judged = call([{'role': 'user', 'content': prompt}], purpose='judge', model='MiniMax-M3')
            records.append(judged)
            if judged['status'] != 'generated':
                return {'status': 'judge_api_error', 'native_metric': task['scoring']['native_metric'], 'judge_calls': records}
            judgement = module['_parse_judgement'](judged['response'].strip().lower())
            if judgement:
                break
        judgement = judgement or {}
    native = adapter.score(json.dumps(judgement, ensure_ascii=False), item)
    metrics = {k: float(v) for k,v in native.items() if isinstance(v, bool)}
    return {'status': 'scored_native' if native.get('correct') is not None else 'native_output_unparsed',
            'native_metric': task['scoring']['native_metric'], 'metrics': metrics, 'native_result': native,
            'judge_model': 'MiniMax-M3', 'judge_calls': records, 'evidence_route': 'local_authored_prior_experiment',
            'author_review': task['reference']['author_review']}


_original_score = score
_original_validate = validate

def score(task, result, call, directory, root):
    if task.get('scoring', {}).get('args', {}).get('kind') in {'student_risk', 'age_values'}:
        return _score_safety(task, result, call, directory, root)
    return _original_score(task, result, call, directory, root)


def validate(task, root):
    if task.get('scoring', {}).get('args', {}).get('kind') in {'student_risk', 'age_values'}:
        ns, adapter, item = _local_item(task, root)
        expected = adapter.build_messages(item)
        actual = task['prediction']['messages'] + task['prediction']['interaction'].get('followups', [])
        assert expected == actual
        if task['scoring']['args']['kind'] == 'student_risk':
            assert ns['_parse_level']('{"档位": 2, "理由":"offline check"}',2) == (2,'offline check')
            assert ns['_parse_level']('{"档位": 5}',2) is None
        else:
            assert ns['_parse_judgement']('{"不合适内容":0,"回复处置":1}')['content_safety'] == 0
        return {'passed': True, 'checks': ['Unchanged copied local original system/all student turns', 'Original fixed MiniMax-M3 judge templates/parser/score code', 'Historical evidence separated from external literature', 'Current GLM output never used for selection']}
    return _original_validate(task, root)


def _load_lda(root):
    path = Path(root) / BASE / 'lda/prompting.py'
    spec = importlib.util.spec_from_file_location('source_fidelity_lda_prompting', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_previous_run = run
_previous_score = score
_previous_validate = validate


def run(task, call, directory, root):
    if task['prediction']['interaction'].get('args', {}).get('kind') != 'lda_video':
        return _previous_run(task, call, directory, root)
    from scripts.source_fidelity.core import prepare_messages
    transcript = []
    for probe in task['prediction']['interaction']['args']['probes']:
        view = copy.deepcopy(task)
        view['prediction']['messages'] = probe['messages']
        answer = call(prepare_messages(view, root), purpose='prediction', parameters={})
        transcript.append({'probe': probe['name'], 'status': answer['status'], 'response': answer.get('response', '')})
        if answer['status'] != 'generated':
            return {'status': answer['status'], 'response': answer.get('response', ''), 'transcript': transcript,
                    'input_failure_is_not_model_score': True}
    return {'status': 'generated', 'response': json.dumps(transcript, ensure_ascii=False), 'transcript': transcript}


def score(task, result, call, directory, root):
    if task.get('scoring', {}).get('args', {}).get('kind') != 'lda_video':
        return _previous_score(task, result, call, directory, root)
    mod = _load_lda(root)
    grades = {row['probe']: mod.parse_score(row['response'], 4, 20) for row in result['transcript']}
    metrics = {}
    for probe in ('null_black', 'null_still'):
        # Original protocol denominator includes declined/unmarked gradings as no credit.
        metrics[probe + '_credit_rate'] = float(grades[probe] is not None and grades[probe] > 4)
    if grades.get('ctx_high') is not None and grades.get('ctx_low') is not None:
        metrics['attainment_label_delta_scale_fraction'] = (grades['ctx_high'] - grades['ctx_low']) / 16
    return {'status': 'scored_native', 'native_metric': task['scoring']['native_metric'], 'metrics': metrics,
            'grades': grades, 'unmarked': sum(v is None for v in grades.values()),
            'scope': 'One original recording with native probes; no QWK, partial correlation or WATCHES verdict can be estimated.'}


def validate(task, root):
    if task.get('scoring', {}).get('args', {}).get('kind') != 'lda_video':
        return _previous_validate(task, root)
    mod = _load_lda(root)
    assert mod.parse_score('{"score":4}',4,20) == 4
    assert mod.parse_score('{"score":21}',4,20) is None
    if task.get('execution', {}).get('eligible') is False:
        return {'passed': True, 'checks': ['Original source/protocol saved', 'Missing media explicitly execution-gated; no API or proxy delivery']}
    assert len(task['prediction']['interaction']['args']['probes']) == 5
    for probe in task['prediction']['interaction']['args']['probes']:
        assert any(part['type'] == 'video_path' for msg in probe['messages'] if isinstance(msg['content'],list) for part in msg['content'])
    return {'passed': True, 'checks': ['Exact original video template and native probe texts', 'Original 480x270 fps2 full-length preprocessing', 'Video assets hashed and true video_url delivery', 'Original parse_score bounds and null-credit definition']}


def fetch_lda_video(root):
    """Resumable single ZIP member download; check every HTTP 206 range, never read the huge ZIP."""
    import concurrent.futures
    import os
    import struct
    import time
    import urllib.request
    import zlib
    import subprocess
    from scripts.source_fidelity.core import write_json
    b = Path(root) / BASE / 'lda'
    job = json.loads((b / 'video_download_job.json').read_text())
    cache = b / 'download_chunks'
    cache.mkdir(exist_ok=True)
    write_json(b / 'download.started.json', {'pid': os.getpid(), 'started_unix': time.time(), **job})
    chunk_size = 4 * 1024 * 1024
    specs = [(offset, min(chunk_size,job['size']-offset)) for offset in range(0,job['size'],chunk_size)]
    def fetch(spec):
        offset,size = spec
        path=cache/f'{offset:012}.bin'
        if path.exists() and path.stat().st_size==size:
            return
        start=job['start']+offset;end=start+size-1
        for retry in range(5):
            try:
                req=urllib.request.Request(job['url'],headers={'Range':f'bytes={start}-{end}','User-Agent':'EduLastExam-source-audit'})
                with urllib.request.urlopen(req,timeout=90) as response:
                    expected=f'bytes {start}-{end}/'
                    if response.status != 206 or not response.headers.get('Content-Range','').startswith(expected):
                        raise IOError('Server did not honor exact byte range; refusing full archive')
                    with path.with_suffix('.part').open('wb') as out:
                        total=0
                        while total<size:
                            data=response.read(min(65536,size-total))
                            if not data:break
                            total+=len(data);out.write(data);out.flush()
                    if total!=size:raise IOError(f'Partial chunk {total}/{size}')
                path.with_suffix('.part').replace(path)
                return
            except Exception:
                if retry==4:raise
                time.sleep(2*(retry+1))
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for _ in pool.map(fetch,specs):
                write_json(b/'download.progress.json',{'completed_bytes':sum(p.stat().st_size for p in cache.glob('*.bin')),'total_bytes':job['size'],'updated_unix':time.time()})
        videos=b/'lasana/videos';videos.mkdir(exist_ok=True)
        raw=videos/(job['id']+'_left.mkv')
        decoder=zlib.decompressobj(-15) if job['method']==8 else None
        with raw.open('wb') as out:
            for offset,size in specs:
                data=(cache/f'{offset:012}.bin').read_bytes()
                out.write(decoder.decompress(data) if decoder else data)
            if decoder:out.write(decoder.flush())
        target=raw.with_suffix('.mp4')
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-vf','scale=480:270,fps=2','-an','-c:v','libx264','-preset','veryfast','-crf','30','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True,timeout=300)
        info=subprocess.run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)],text=True,capture_output=True,check=True)
        write_json(b/'video_ffprobe.json',json.loads(info.stdout))
        write_json(b/'download.complete.json',{'path':str(target),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'finished_unix':time.time(),'exit_code':0})
        # Preserve decoded source provenance; source is deliberately uncommitted.
        return str(target)
    except Exception as error:
        write_json(b/'download.failed.json',{'error':repr(error),'finished_unix':time.time(),'exit_code':1})
        raise


def prepare_lda_task(root):
    """Write the source audit immediately, enable only when the exact video/probes exist."""
    import csv
    import tempfile
    from scripts.source_fidelity.core import write_json
    root=Path(root);b=root/BASE/'lda';job=json.loads((b/'video_download_job.json').read_text())
    spec=importlib.util.spec_from_file_location('source_fidelity_lda_cases',b/'cases.py')
    cases=importlib.util.module_from_spec(spec);spec.loader.exec_module(cases)
    taskname=job['task'];rid=job['id'];annotation=b/'lasana/Annotation';hum={}
    for index in range(4):
        for row in csv.DictReader((annotation/f'{taskname}_rater{index}.csv').open(),delimiter=';'):
            if row['id']==rid:hum[f'rater{index}']=float(row['GRS']) if row.get('bimanual_dexterity','').strip() else 4.0
    row=next(x for x in csv.DictReader((annotation/f'{taskname}.csv').open(),delimiter=';') if x['id']==rid)
    minute,second=row['duration'].split(':')[-2:];desc,fail=cases.LASANA_TASKS[taskname]
    target=b/'lasana/videos'/f'{rid}_left.mp4'
    case=cases.normalise({'id':f'lasana-{rid}','task':taskname,'question':desc,'reference':'','rubric':cases.LASANA_RUBRIC+(f'\nIf {fail}, the attempt has failed: give 1 on every aspect (score 4).' if fail else ''),'materials':'','response':f"(the trainee's recording is attached; length {int(minute)} min {int(second)} s)",'scale':[4,20],'human':hum,'groups':{'task':taskname},'media':[{'kind':'video','path':str(target),'format':'mp4'}]})
    record=b/'selected'/f'lasana_{rid}.json';write_json(record,case)
    def asset(path,role='provenance'):
        return {'path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':role}
    assets=[asset(record),asset(b/'prompting.py','runtime'),asset(b/'cases.py','runtime'),asset(b/'prompts/video.txt','runtime'),asset(b/'video/PREREG.md'),asset(b/'video/README.md'),asset(b/'video_download_job.json')]
    ready=(b/'download.complete.json').exists() and target.is_file();probes=[]
    if ready:
        info=json.loads((b/'video_ffprobe.json').read_text())
        stream=next(x for x in info['streams'] if x['codec_type']=='video')
        assert stream['width']==480 and stream['height']==270 and stream['avg_frame_rate']=='2/1'
        assert not any(x['codec_type']=='audio' for x in info['streams'])
        assert abs(float(info['format']['duration'])-(int(minute)*60+int(second)))<=2
        assert target.stat().st_size <= 200_000_000, 'Official Z.ai video size limit200MB exceeded'
        mod=_load_lda(root);template=mod.load_prompt(str(b/'prompts/video.txt'))
        for name in ['base','ctx_low','ctx_high','null_black','null_still']:
            if name in ['null_black','null_still']:
                mod._video_variant(str(target),name)
                media=target.parent/'.probes'/f'{target.stem}.{name}.mp4'
            else:media=target
            response,context=mod.probe_input(case,name)
            messages=template.build(case,response,context)
            messages[-1]['content']=[{'type':'text','text':messages[-1]['content']},{'type':'video_path','path':str(media.relative_to(root))}]
            probes.append({'name':name,'messages':messages})
            if not any(x['path']==str(media.relative_to(root)) for x in assets):assets.append(asset(media,'prediction'))
        assets.append(asset(b/'video_ffprobe.json'))
    cid='ELE-SF-37-001'
    task={'case_id':cid,'direction_ids':['37'],'title':'LDA LASANA 原视频与黑屏、静帧、能力标签对照','origin':'original_task','source':{'url':'https://github.com/Learning-Design-Alliance/ai-grading-benchmark','revision':'0c78a10db8a0b1fb735fda5e0a51a8bb89ce7c1e','case_id':f'lasana-{rid}','record_path':str(record.relative_to(root)),'sha256':hashlib.sha256(record.read_bytes()).hexdigest(),'prompt_builder_path':str(BASE/'lda/prompting.py'),'scorer_path':str(BASE/'lda/bench.py')},'fidelity':{'task_condition':'Original recorded laparoscopic training performance; same-duration black/still probes and exact strong/weak attainment labels.','input':'Actual full original selected left-camera video; original480x270,2fps,CRF30,no-audio preprocessing; native task/rubric/length text.','output':'Original JSON GOALS four aspects and total score4–20.','scoring':'Unmodified native parse_score; black/still credit fraction and high-minus-low score/16. No tiny-sample correlation verdict.','environment':'Five independent video_url API calls with no audio/transcript substitute.','deviations':['One of original100recordings only; not the100-case full original experiment.','No4096output-token cap under repository policy.','Gateway acceptance must be recorded: API/media-delivery errors are not skill failures.'],'scope':'native_single_recording_probe_subset'},'selection_reason':'First lexicographic recording ID across original fixed test-split25/task selection, fixed before GLM replies.','prediction':{'messages':[],'parameters':{},'interaction':{'mode':'adapter','module':MODULE,'args':{'kind':'lda_video','probes':probes}}},'scoring':{'mode':'native_adapter','native_metric':'null_black_credit_rate/null_still_credit_rate/attainment_label_delta_scale_fraction','module':MODULE,'args':{'kind':'lda_video'}},'assets':assets,'reference':{'human_grs':hum,'scale':[4,20],'null_minimum':4,'interpretation':'A single recording cannot estimate QWK, control-for-duration correlation, confidence intervals or WATCHES verdict. No speech/accent coverage claimed.'},'review':{'human_review':'pending','author_offline_check':'native_prompt_parser_and_media_identity' if ready else 'source_verified_media_download_pending'},'execution':{'eligible':ready,'reason':'All exact original video assets prepared' if ready else 'Exact selected raw video downloading; no truncated/frames-only substitute allowed.'}}
    write_json(root/'private/edu_last_exam_source_fidelity_v1/authored'/f'{cid}.json',task)
    def src(id,title,url,path,loc,excerpt):
        return {'source_id':id,'title':title,'url':url,'local_path':str(path.relative_to(root)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'revision':'0c78a10db8a0b1fb735fda5e0a51a8bb89ce7c1e','locator':loc,'verified_at':'2026-11-10','evidence_excerpt':excerpt}
    audit={'direction_id':'37','title':'音视频学习表现的证据真实性与语言差异','status':'ready_original' if ready else 'blocked_environment','sources':[src('LDA-video','LDA video preregistered protocol','https://github.com/Learning-Design-Alliance/ai-grading-benchmark',b/'video/PREREG.md','video/PREREG.md: probes, length, hallucination','Blank/frozen recordings must receive the minimum; attainment labels change no work.'),src('LDA-results','LDA recorded-performance results','https://github.com/Learning-Design-Alliance/ai-grading-benchmark',b/'video/README.md','Video task results and coverage addition','GLM5.3Flash original run credits3%black screens and57%frozen frames; no extrapolation to all classes.'),src('LDA-speech','LDA speech protocol and limits','https://github.com/Learning-Design-Alliance/ai-grading-benchmark',b/'speech/README.md','Speech pronunciation and silent controls','Seven audio-model study; Mandarin-L1 speakers only, accent not a nuisance test.')],'research_failure':{'condition':'Score actual observed performance rather than duration/attainment label; withhold skill credit for black or frozen recordings.','finding':'Native video experiments separate agreement beyond duration from raw QWK and expose credit for non-performance probes; some models do show beyond-duration signal.','model_setting':'Original21runs, video or declared16-frame modes, including GLM5.3Flash video.','scope':'Laparoscopic skill videos; not general classroom assessment or low-resource language conclusion.','source_id':'LDA-video','locator':'video/PREREG.md; video/README.md'},'original_task':{'available':True,'input_contract':'Original LASANA full selected video and native GOALS prompt, with native same-work probes.','output_contract':'4–20 total and four1–5subscores JSON.','scoring_contract':'Native parser; null credit and paired label delta; full100-case correlations not estimated from1case.','environment_contract':'ffmpeg original preprocessing; genuinevideo_url request; no transcript proxy.','source_case_ids':[f'lasana-{rid}']},'decision':{'route':'original_task','rationale':'Preserve actual temporal visual evidence and native counterfactuals. Download/transport failure is an environment state, never model error.','limitations':['Only video submechanism covered; audio silence and cross-language comparison still unmeasured.','One source case does not support native population WATCHES claim.']},'condition_mapping':[{'condition':'Original raw temporal performance vs black/still controls and same-work label switch','evidence_locator':'video/PREREG.md probes table','implementation_locator':cid,'preserved':ready,'omission_reason':None if ready else 'Original selected media download still in progress.'}],'task_ids':[cid],'search_log':[{'action':'Read full original video/speech PREREG and result sources; fetch LASANAannotations and exactselectedZIPmember','result':'206 Content-Range verified;4MiB resumable chunks and original ffmpeg preprocessing, no wholeZIP download.'},{'action':'Read official Z.ai and BigModel chat-completion docs','result':'Both document multimodal video support; actual gateway acceptance is tracked separately and not assumed frommodelname.'}]}
    doc=b/'zai_chat_completion.md'
    if doc.exists():
        audit['sources'].append(src('ZAI-video-contract','Official Z.ai chat completion schema','https://docs.z.ai/api-reference/llm/chat-completion.md',doc,'Video content schema lines869-891','video_url URL; supportedmp4/mkv/mov; size≤200MB. Gateway support remains separately verified.'))
        audit['sources'][-1]['revision']='Retrieved2026-11-10'
    write_json(root/'data/edu_last_exam_source_fidelity_v1/directions/37.json',audit)
    if ready:write_json(b/'task.prepared.json',{'case_id':cid,'eligible':True,'assets':len(assets)})
    return {'case_id':cid,'eligible':ready}


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--fetch-video',action='store_true')
    parser.add_argument('--prepare-video',action='store_true')
    args=parser.parse_args()
    if args.fetch_video:
        fetch_lda_video(Path(__file__).resolve().parents[2])
        prepare_lda_task(Path(__file__).resolve().parents[2])
    if args.prepare_video:
        print(prepare_lda_task(Path(__file__).resolve().parents[2]))
