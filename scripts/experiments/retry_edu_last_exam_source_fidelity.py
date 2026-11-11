#!/usr/bin/env python3
"""Retry only unfinished predictions, preserving the first run and native scores."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import fcntl
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.source_fidelity import core
from scripts.experiments import run_edu_last_exam_source_fidelity as runner

SELECTED = ['ELE-SF-19-001', 'ELE-SF-23-001', 'ELE-SF-23-002', 'ELE-SF-23-003', 'ELE-SF-28-001']
BASE = Path('reports/eval/edu_last_exam_source_fidelity_v1/_exploratory')


def retry_task(task, previous, socratic_transport='neutral_user'):
    if previous['status'] == 'generated':
        raise ValueError('Do not regenerate successful predictions')
    if previous['status'] == 'original_condition_unavailable_not_measured':
        raise ValueError('Original input/environment is unavailable; no substitute is authorized')
    adapted = copy.deepcopy(task)
    if task['case_id'].startswith('ELE-SF-23-'):
        assert all(m['role'] == 'system' for m in task['prediction']['messages'])
        if socratic_transport in {'split_roles','split_roles_client_stop'}:
            text = task['prediction']['messages'][0]['content']
            boundary = text.rfind('\n\nProblem: ')
            if boundary < 0:
                raise ValueError('Cannot split original problem without changing text')
            adapted['prediction']['messages'] = [{'role':'system','content':text[:boundary]},
                                                  {'role':'user','content':text[boundary:]}]
            if socratic_transport == 'split_roles_client_stop':
                stops = adapted['prediction']['parameters'].pop('stop')
                adapted['retry_protocol'] = {'visible_content_stop':stops,
                    'reason':'Provider applied original newline stop to reasoning_content and returned empty content; enforce original stop on visible answer locally.'}
        else:
            adapted['prediction']['messages'].append({'role':'user','content':'Please complete the task above.'})
    return adapted


def visible_stop_result(result, stops):
    """Apply the original stopping strings only to delivered answer content."""
    if result['status'] != 'generated':
        return result
    result = copy.deepcopy(result)
    raw = result.get('raw_response', result['response'])
    offsets = [raw.find(stop) for stop in stops if stop and raw.find(stop) >= 0]
    response = raw[:min(offsets)] if offsets else raw
    result.update(response=response, raw_response=raw,
                  visible_content_stop={'stops':stops,'truncated':response!=raw,'applied_to_reasoning':False})
    if result.get('transcript'):
        result['transcript'][-1].update(response=response, raw_response=raw)
    if not response.strip():
        result['status'] = 'empty_response'
    return result


def inputs(parent, selected_cases=SELECTED, socratic_transport='neutral_user'):
    audits, tasks, checks = core.load(ROOT)
    selected = []
    identities = {}
    old_manifest = json.loads((parent / 'run_manifest.json').read_text())
    for task in tasks:
        if task['case_id'] not in selected_cases:
            continue
        if core.digest(task) != old_manifest['task_sha256'][task['case_id']]:
            raise ValueError('Original task differs from the first run')
        path = parent / 'cases' / task['case_id'] / 'result.json'
        previous = json.loads(path.read_text())
        identities[task['case_id']] = core.digest(path.read_bytes())
        adapted = retry_task(task, previous, socratic_transport)
        core.validate_task(adapted, ROOT)
        selected.append(adapted)
    if {t['case_id'] for t in selected} != set(selected_cases):
        raise ValueError('Incomplete retry task selection')
    return audits, selected, identities


class NoPaidJudge:
    def supports_model(self, model):
        return False

    def __call__(self, *args, **kwargs):
        raise RuntimeError('User requested direct Codex review; no external judge is invoked')


def run(args):
    audits, tasks, previous = inputs(args.parent_run, args.cases, args.socratic_transport)
    identity = {'parent_run':str(args.parent_run), 'parent_prediction_sha256':previous,
                'selected_cases':args.cases, 'model':args.model, 'endpoint':args.endpoint,
                'concurrency':args.concurrency, 'token_ceiling':'omitted',
                'task_sha256':{t['case_id']:core.digest(t) for t in tasks},
                'code_sha256':runner.code_identity(ROOT) | {str(Path(__file__).relative_to(ROOT)):core.digest(Path(__file__).read_bytes())},
                'changes':{'19':'Reuse successful original stage calls; retry truncated stage with unchanged parameters',
                           '23':args.socratic_transport + ': preserve original content; declared gateway message-role adaptation',
                           '28':'Extract one intact JSON action from incidental prose; preserve original full inputs, 40 turns and isolated tools'},
                'judging':'native deterministic metrics plus separate Codex author review; no paid judge'}
    if args.dry_run:
        print(json.dumps({'status':'dry_run_passed','cases':len(tasks),'original_inputs_unchanged_except_declared_transport':True}))
        return
    key = os.environ.get('GLM_API')
    if not key:
        raise ValueError('GLM_API is absent')
    args.output.mkdir(parents=True, exist_ok=True)
    lock = (args.output / '.run.lock').open('w')
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    path = args.output / 'run_manifest.json'
    if path.exists() and json.loads(path.read_text()) != identity:
        raise ValueError('Retry identity changed; use another output directory')
    core.write_json(path, identity)
    core.write_json(args.output / 'adapted_tasks.json', tasks)
    cache_source = args.parent_run / 'cases/ELE-SF-19-001/calls'
    cache_target = args.output / 'cases/ELE-SF-19-001/calls'
    if 'ELE-SF-19-001' in args.cases and not cache_target.exists():
        shutil.copytree(cache_source, cache_target)
    predictions, scores = {}, {}
    gate = threading.BoundedSemaphore(args.concurrency)
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = {pool.submit(runner.execute, task, args, key, gate):task for task in tasks}
        runner.save(args, audits, tasks, predictions, scores, 'predicting', args.cases)
        for future in as_completed(futures):
            task = futures[future]
            ident = task['case_id']
            predictions[ident] = future.result()
            if task.get('retry_protocol',{}).get('visible_content_stop'):
                case_directory = args.output / 'cases' / ident
                unprocessed_path = case_directory/'unprocessed_result.json'
                if not unprocessed_path.exists():
                    core.write_json(unprocessed_path,predictions[ident])
                predictions[ident] = visible_stop_result(predictions[ident],task['retry_protocol']['visible_content_stop'])
                core.write_json(case_directory/'result.json',predictions[ident])
                (case_directory/'response.md').write_text(predictions[ident].get('response',''))
            directory = args.output / 'cases' / ident / 'scoring'
            try:
                score = core.score(task, predictions[ident], NoPaidJudge(), directory, ROOT, args.model)
            except Exception as error:
                score = {'status':'scoring_error_not_scored','error':str(error).replace(key,'[REDACTED]')}
            scores[ident] = {'case_id':ident,'direction_ids':task['direction_ids'],**score}
            core.write_json(directory / 'score.json', scores[ident])
            runner.save(args, audits, tasks, predictions, scores, 'predicting', [t['case_id'] for f,t in futures.items() if not f.done()])
    core.write_json(args.output / 'prediction_finished.json', {'at':runner.now(),'records':len(predictions)})
    state = 'complete_with_unmeasured_or_pending' if any(p['status'] != 'generated' for p in predictions.values()) or any(s['status'] != 'scored_native' for s in scores.values()) else 'complete'
    summary = runner.save(args, audits, tasks, predictions, scores, state)
    core.write_json(args.output / 'finished.json', {'at':runner.now(),'state':state,'selected_cases':len(tasks),'prediction_records':len(predictions),'score_records':len(scores)})
    print(json.dumps(summary, ensure_ascii=False))


def launch(args):
    from scripts.experiments.launch_edu_last_exam_full_coverage import SUPERVISOR
    if not re.fullmatch('[a-z0-9_]+', args.name):
        raise ValueError('Invalid retry label')
    if not os.environ.get('GLM_API'):
        raise ValueError('GLM_API is absent')
    output = ROOT / BASE / args.name / 'GLM-5.3-Flash'
    source = output.parent / 'source_snapshot'
    control = ROOT / 'eval' / ('source_fidelity_' + args.name)
    if output.exists() or control.exists():
        raise ValueError('Output exists; preserve it and choose another label')
    output.mkdir(parents=True)
    control.mkdir(parents=True)
    shutil.copytree(args.parent_run.parent / 'source_snapshot', source,
                    ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for relative in ['scripts/source_fidelity/group_27_37.py', 'scripts/experiments/retry_edu_last_exam_source_fidelity.py',
                     'data/edu_last_exam_source_fidelity_v1/codex_review_protocol_2026-11-11.md']:
        shutil.copy2(ROOT / relative, source / relative)
    core.write_json(output.parent / 'source_snapshot_manifest.json',
                    {str(p.relative_to(source)):core.digest(p.read_bytes()) for p in sorted(source.rglob('*')) if p.is_file()})
    command = [sys.executable, str(source / 'scripts/experiments/retry_edu_last_exam_source_fidelity.py'),
               '--parent-run',str(args.parent_run),'--output',str(output), '--cases', *args.cases,
               '--concurrency',str(args.concurrency),'--socratic-transport',args.socratic_transport]
    with (control / 'dry_run.json').open('w') as file:
        subprocess.run([*command,'--dry-run'],cwd=source,stdout=file,check=True)
    config = {'root':str(ROOT),'source_snapshot':str(source),'output':str(output),'command':command,
              'api_key_env':'GLM_API','concurrency':args.concurrency,'tmux_socket':'edu_retry_'+args.name,'tmux_session':'edu_retry_'+args.name}
    core.write_json(control / 'config.json', config)
    (control / 'supervisor.py').write_text(SUPERVISOR)
    shell = 'exec ' + shlex.quote(sys.executable) + ' ' + shlex.quote(str(control/'supervisor.py')) + ' >> ' + shlex.quote(str(control/'supervisor.log')) + ' 2>&1'
    env = {k:v for k,v in os.environ.items() if k in {'PATH','HOME','LANG','LC_ALL','TERM','GLM_API','TMPDIR'}}
    subprocess.run(['tmux','-L',config['tmux_socket'],'new-session','-d','-s',config['tmux_session'],'-c',str(source),shell],env=env,check=True)
    print(json.dumps({'status':'launched','output':str(output),'control':str(control),'cases':args.cases}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch',action='store_true')
    parser.add_argument('--name',default='20261111_source_fidelity_retry01')
    parser.add_argument('--parent-run',type=Path,default=ROOT/BASE/'20261110_source_fidelity_glm53flash/GLM-5.3-Flash')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--cases',nargs='+',choices=SELECTED,default=SELECTED)
    parser.add_argument('--concurrency',type=int,choices=range(1,5),default=4)
    parser.add_argument('--socratic-transport',choices=['neutral_user','split_roles','split_roles_client_stop'],default='neutral_user')
    args = parser.parse_args()
    args.parent_run = args.parent_run.resolve()
    args.model,args.endpoint,args.timeout,args.retries = 'GLM-5.3-Flash',runner.transport.ENDPOINT,600,2
    if args.launch:
        launch(args)
    else:
        if args.output is None:
            parser.error('--output is required when running')
        args.output = args.output.resolve()
        run(args)


if __name__ == '__main__':
    main()
