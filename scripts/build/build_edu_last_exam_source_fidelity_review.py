#!/usr/bin/env python3
"""Validate source-bound Codex reviews and generate a separate review report."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import fcntl
import hashlib
import html
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.source_fidelity.core import write_json

ORIGINAL = Path('reports/eval/edu_last_exam_source_fidelity_v1/_exploratory/20261110_source_fidelity_glm53flash/GLM-5.3-Flash')
REVIEW = Path('private/edu_last_exam_source_fidelity_v1/review_20261111')
OUTPUT = Path('reports/source_fidelity_v1/codex_review_20261111')
VERDICTS = {'pass','fail','mixed','disputed','descriptive_only','not_evaluable','pending_rerun'}
LABELS = {'pass':'通过','fail':'未通过','mixed':'配对/条件表现混合','disputed':'存在争议','descriptive_only':'描述性结果','not_evaluable':'无法评价','pending_rerun':'待补跑/待补跑复核'}


def validate_review(row, root):
    required = {'case_id','direction_ids','source_run','prediction_sha256','reviewer','review_scope','verdict','reason','criteria','evidence','native_score_interpretation','limitations'}
    if required - row.keys():
        raise ValueError(f"Review fields missing for {row.get('case_id')}: {required-row.keys()}")
    if row['reviewer'] != 'Codex' or row['review_scope'] != 'author_related_offline_review' or row['verdict'] not in VERDICTS:
        raise ValueError('Unexpected reviewer identity or verdict')
    source = Path(row['source_run'])
    if source.is_absolute() or '..' in source.parts:
        raise ValueError('source_run must be repository relative')
    path = root / source / 'cases' / row['case_id'] / 'result.json'
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['prediction_sha256']:
        raise ValueError(f"Reviewed prediction changed: {row['case_id']}")
    prediction = json.loads(path.read_text())
    if row['verdict'] in {'pass','fail'} and prediction['status'] != 'generated':
        raise ValueError('Incomplete predictions cannot receive a completed-answer verdict')
    if not row['reason'] or not isinstance(row['criteria'],list) or not isinstance(row['evidence'],list):
        raise ValueError('Review requires explicit rationale, criteria, and evidence')
    if prediction['status'] == 'generated' and (not row['criteria'] or not row['evidence']):
        raise ValueError('Generated answers must be actually reviewed against evidence')
    for evidence in row['evidence']:
        if isinstance(evidence,dict) and evidence.get('path'):
            target = Path(evidence['path'])
            if not target.is_absolute():
                target = root / target
            if not target.exists():
                raise ValueError(f"Evidence file missing: {target}")
    return prediction


def latest_reviews(rows, predictions):
    latest = {}
    for row in sorted(rows,key=lambda r:r['source_run']):
        previous = latest.get(row['case_id'])
        new_complete = predictions[(row['source_run'],row['case_id'])]['status'] == 'generated'
        old_complete = previous and predictions[(previous['source_run'],previous['case_id'])]['status'] == 'generated'
        if not old_complete or new_complete:
            latest[row['case_id']] = row
    return latest


def _build_unlocked(root=ROOT, allow_partial=False):
    root = Path(root)
    tasks = {t['case_id']:t for t in map(json.loads,(root/ORIGINAL.parent/'source_snapshot/private/edu_last_exam_source_fidelity_v1/items.jsonl').read_text().splitlines())}
    rows = []
    for file in sorted((root/REVIEW).glob('reviews_*.jsonl')):
        rows.extend(json.loads(line) for line in file.read_text().splitlines() if line.strip())
    identities = set()
    predictions = {}
    for row in rows:
        identity = (row['source_run'],row['case_id'])
        if identity in identities or row['case_id'] not in tasks:
            raise ValueError(f'Duplicate or unregistered review: {identity}')
        identities.add(identity)
        predictions[identity] = validate_review(row,root)
    original = [r for r in rows if r['source_run'] == str(ORIGINAL)]
    missing = sorted(set(tasks)-{r['case_id'] for r in original})
    if missing and not allow_partial:
        raise ValueError(f'Missing original review records: {missing}')
    latest = latest_reviews(rows,predictions)
    latest_rows = [latest[k] for k in sorted(latest)]
    run_states = {}
    unreviewed_retries = []
    for run in sorted((root/ORIGINAL.parent.parent).glob('20261111_source_fidelity_retry*/GLM-5.3-Flash')):
        relative = str(run.relative_to(root))
        if (run/'summary.json').exists():
            status = json.loads((run/'summary.json').read_text())
            run_states[relative] = {k:status.get(k) for k in ['state','selected_cases','prediction_records','prediction_status_counts','pending_predictions']}
        for path in sorted(run.glob('cases/*/result.json')):
            pred = json.loads(path.read_text())
            if pred['status'] == 'generated' and (relative,pred['case_id']) not in identities:
                unreviewed_retries.append({'case_id':pred['case_id'],'source_run':relative})
    direction_counts = defaultdict(Counter)
    for row in latest_rows:
        for direction in row['direction_ids']:
            direction_counts[direction][row['verdict']] += 1
    summary = {'updated_at':datetime.now(timezone.utc).isoformat(),'reviewer':'Codex','review_scope':'author_related_offline_review','independent_teacher_review':False,
               'original_run':str(ORIGINAL),'expected_original_cases':len(tasks),'original_review_records':len(original),
               'original_generated_reviewed':sum(predictions[(r['source_run'],r['case_id'])]['status']=='generated' for r in original),
               'original_verdict_counts':dict(Counter(r['verdict'] for r in original)),
               'latest_review_records':len(latest_rows),'latest_verdict_counts':dict(Counter(r['verdict'] for r in latest_rows)),
               'direction_verdict_counts':{k:dict(v) for k,v in sorted(direction_counts.items())},
               'missing_original_reviews':missing,'retry_run_states':run_states,'unreviewed_successful_retries':unreviewed_retries,
               'cross_construct_accuracy':None,'native_scores_unchanged':True,'frozen_benchmark':False}
    output = root/OUTPUT
    output.mkdir(parents=True,exist_ok=True)
    write_json(output/'summary.json',summary)
    write_json(output/'validation.json',{'passed':True,'review_records':len(rows),'all_original_cases_accounted_for':not missing,'prediction_hashes_verified':True})
    for name,values in [('case_reviews.jsonl',rows),('latest_case_reviews.jsonl',latest_rows)]:
        (output/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in values))
    escape = lambda x:html.escape(str(x))
    link = lambda path:escape(os.path.relpath(root/path,output))
    page = ["<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>GLM原题复测 · Codex逐份复核</title><style>body{font:16px/1.65 system-ui;max-width:1400px;margin:25px auto;padding:20px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #d5dde5;padding:8px;text-align:left;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{border:1px solid #ddd;padding:12px;margin:10px 0}.fail{background:#fff0ed}.disputed{background:#fff6df}.pass{background:#eef8f0}</style><h1>GLM-5.3-Flash 原题复测：Codex逐份复核</h1><p>用户授权的作者关联离线复核；保留原题、原判分和旧尝试。当前判定不是独立教师审核，也不冒充论文指定judge。原连续指标与配对效应不强行转换为总体正确率。</p><pre>",escape(json.dumps(summary,ensure_ascii=False,indent=2)),"</pre><h2>最新已复核视图</h2><table><tr><th>任务</th><th>判定</th><th>依据</th><th>原分与边界</th><th>实际回答</th></tr>"]
    for row in latest_rows:
        case=row['case_id'];path=Path(row['source_run'])/'cases'/case/'result.json'
        page.append(f"<tr class='{row['verdict']}'><td>{escape(case)}<br>{escape(tasks[case]['title'])}</td><td>{LABELS[row['verdict']]}</td><td>{escape(row['reason'])}</td><td>{escape(row['native_score_interpretation'])}</td><td><a href='{link(path)}'>原回答/完整轨迹</a></td></tr>")
    page.append('</table><h2>逐条判据与全部尝试</h2>')
    for row in rows:
        page.append(f"<details><summary>{escape(row['case_id'])} · {LABELS[row['verdict']]} · {escape(row['source_run'].split('/')[-2])}</summary><pre>{escape(json.dumps(row,ensure_ascii=False,indent=2))}</pre></details>")
    page.append('</html>')
    (output/'review.html').write_text(''.join(page))
    print(json.dumps({k:v for k,v in summary.items() if k!='direction_verdict_counts'},ensure_ascii=False))
    return summary


def build(root=ROOT, allow_partial=False):
    output = Path(root)/OUTPUT
    output.mkdir(parents=True,exist_ok=True)
    control = Path(root)/'eval/source_fidelity_review_20261111'
    control.mkdir(parents=True,exist_ok=True)
    with (control/'build.lock').open('a') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        return _build_unlocked(root,allow_partial)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args()
    build(allow_partial=args.allow_partial)
