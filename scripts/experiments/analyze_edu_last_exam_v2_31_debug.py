#!/usr/bin/env python3
"""Generate bounded direction31 execution evidence, separate from author review."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage.core import digest, write_json
from scripts.full_coverage.workspace_execution import run_program
from scripts.build.build_edu_last_exam_scenario_v1 import html_document


def text_values(value):
    """Validate quotes against decoded field text, preserving literal quotes."""
    if isinstance(value,str):
        yield value
    elif isinstance(value,dict):
        for child in value.values():
            yield from text_values(child)
    elif isinstance(value,list):
        for child in value:
            yield from text_values(child)


def analyze(run, output, reviews=None):
    run = Path(run).resolve()
    output = Path(output).resolve()
    batch = run.parent / 'source_snapshot/private/edu_last_exam_v2_31_debug'
    engine_paths=['scripts/full_coverage/core.py', 'scripts/full_coverage/workspace_execution.py',
                  'scripts/full_coverage/directions/d31.py']
    engine_hashes={path:digest((ROOT/path).read_bytes()) for path in engine_paths}
    if any(not (run.parent/'source_snapshot'/path).is_file()
           or digest((run.parent/'source_snapshot'/path).read_bytes())!=sha for path,sha in engine_hashes.items()):
        raise ValueError('Execution engine differs from the frozen prediction runtime')
    items = {item['item_id']: item for item in
             (json.loads(line) for line in (batch / 'items.jsonl').read_text().splitlines())}
    author = {}
    if reviews:
        author = {row['case_id']: row for row in json.loads(Path(reviews).read_text())['cases']}
    rows = []
    for item_id, item in items.items():
        gold = json.loads((batch / 'reference' / item_id / 'execution_oracle.json').read_text())
        for prompt in item['prompts']:
            variant = prompt['prompt_id']
            case_id = item_id + '__' + variant
            directory = run / 'cases' / case_id
            path = directory / 'result.json'
            row = dict(case_id=case_id, item_id=item_id, prompt_id=variant, role=gold['roles'][variant],
                       prediction_status='missing', verdict='not_evaluable')
            if not path.exists():
                rows.append(row)
                continue
            result = json.loads(path.read_text())
            row.update(prediction_status=result['status'], prediction_sha256=digest(path.read_bytes()),
                       model_turns=result.get('model_turns'), environment_completed=result.get('environment_completed',False))
            if result['status'] not in ('generated','episode_incomplete'):
                rows.append(row)
                continue
            runtime = item['runtime'][variant]
            source_path = directory / 'workspace/student.py'
            report_path = directory / 'workspace/report.json'
            if not source_path.exists():
                row.update(verdict='failed_delivery', reason='No workspace program was preserved')
                rows.append(row)
                continue
            source = source_path.read_text()
            execution = run_program({'student.py':source}, runtime['execution_contract'], gold['hidden_tests'])
            public = run_program({'student.py':source}, runtime['execution_contract'])
            events = result.get('events',[])
            runs = [event['observation'] for event in events if event.get('command',{}).get('action')=='run']
            verified = any(obs.get('source_sha256')==execution['source_sha256'] and obs.get('passed') is True for obs in runs)
            unchanged = source == runtime['initial_files']['student.py']
            failures = [r for r in execution.get('results',[]) if not r['passed']]
            row.update(final_source_sha256=execution['source_sha256'], functional_contract_pass=execution['passed'],
                       public_tests_pass=public['passed'], private_test_count=len(gold['hidden_tests']),
                       private_failed_count=len(failures), private_failure_examples=failures[:5],
                       program_error=execution.get('program_error'),
                       recorded_run_count=len(runs), submitted_source_actually_verified=verified,
                       recovered_invalid_action_count=sum(event.get('error')=='invalid_json_action' for event in events),
                       source_unchanged=unchanged, correct_control_preserved=unchanged if variant=='v3' else None,
                       submission_checks_pass=bool(result.get('artifact_checks')) and all(c.get('passed') is True for c in result['artifact_checks']))
            if report_path.exists():
                try:
                    report=json.loads(report_path.read_text())
                    valid=(isinstance(report,dict) and isinstance(report.get('diagnosis'),list)
                           and isinstance(report.get('feedback'),str) and isinstance(report.get('verification'),str))
                except (json.JSONDecodeError,UnicodeError):
                    report=None
                    valid=False
            else:
                report=None
                valid=False
            row.update(report_valid=valid, submitted_report=report,
                       report_sha256=digest(report_path.read_bytes()) if report_path.exists() else None)
            reviewer=author.get(case_id)
            if reviewer:
                if reviewer.get('prediction_sha256') != row['prediction_sha256']:
                    raise ValueError('Author review prediction identity mismatch: '+case_id)
                if reviewer.get('report_sha256') != row['report_sha256']:
                    raise ValueError('Author review report identity mismatch: '+case_id)
                evidence_text = '\n'.join(text_values(report)) + '\n' + '\n'.join(t['response'] for t in result.get('transcript',[]))
                for evidence in reviewer.get('evidence',[]):
                    if not evidence.get('quote') or evidence['quote'] not in evidence_text:
                        raise ValueError('Unverified author evidence quote: '+case_id)
                row['author_review']=reviewer
            checks=[result['status']=='generated',row['environment_completed'],execution['passed'],verified,
                    row['submission_checks_pass'],valid,unchanged if variant=='v3' else True]
            if not all(checks):
                row['verdict']='fail_observable_criterion'
            elif reviewer is None:
                row['verdict']='semantic_review_pending'
            elif all(reviewer.get(key) is True for key in ('diagnosis_pass','counterexamples_pass','feedback_pass','student_approach_preserved')):
                row['verdict']='pass_author_reviewed'
            else:
                row['verdict']='fail_author_reviewed'
            rows.append(row)
    summary=dict(status='exploratory_author_review_not_frozen',run=str(run),material_count=len(items),dependent_condition_count=len(rows),
                 prediction_status_counts=dict(Counter(r['prediction_status'] for r in rows)),
                 verdict_counts=dict(Counter(r['verdict'] for r in rows)),
                 review_type='author_related_offline_review',independent_teacher_review='pending',
                 same_model_judge_used=False,all_subclaims_directly_measured=False,
                 provenance=dict(batch_manifest_sha256=digest((batch/'manifest.json').read_bytes()),
                                 runtime_engine='restricted_python_ast_v1',expected_model='GLM-5.3-Flash',
                                 scoring_code_sha256=digest(Path(__file__).read_bytes()),
                                 execution_engine_sha256=engine_hashes,
                                 author_reviews_sha256=digest(Path(reviews).read_bytes()) if reviews else None,
                                 reference_oracles_sha256={str(path.relative_to(batch)):digest(path.read_bytes())
                                                          for path in sorted((batch/'reference').glob('*/execution_oracle.json'))},
                                 scoring_rule='All observable delivery/execution checks and all four author-reviewed semantic criteria must pass; source identity and evidence quotes verified.'),
                 no_population_failure_rate=True)
    requests = [json.loads(path.read_text()) for path in sorted(run.glob('cases/*/calls/cases/*/request.json'))]
    calls = [json.loads(path.read_text()) for path in sorted(run.glob('cases/*/calls/cases/*/result.json'))]
    token_fields = {'max_tokens', 'max_completion_tokens', 'max_output_tokens'}
    snapshot_manifest = run.parent / 'source_snapshot_manifest.json'
    snapshot_hashes = json.loads(snapshot_manifest.read_text()) if snapshot_manifest.exists() else {}
    snapshot = run.parent / 'source_snapshot'
    snapshot_valid = bool(snapshot_hashes) and all((snapshot/path).is_file() and digest((snapshot/path).read_bytes())==sha
                                                for path,sha in snapshot_hashes.items())
    manifest_path = run / 'run_manifest.json'
    run_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    summary['completion_audit'] = dict(
        source_snapshot_hashes_valid=snapshot_valid, recorded_requests=len(requests), recorded_call_results=len(calls),
        token_ceiling_omitted=bool(requests) and all(not token_fields.intersection(r['payload']) for r in requests),
        coding_plan_endpoint=run_manifest.get('endpoint')=='https://open.bigmodel.cn/api/coding/paas/v4/chat/completions',
        all_calls_verified=bool(calls) and len(calls)==len(requests) and all(
            r.get('status')=='generated' and r.get('finish_reason')=='stop' and r.get('stream_done_seen') is True
            and {m.casefold() for m in r.get('returned_models',[])}=={'glm-5.3-flash'} for r in calls),
        returned_models=sorted({m for r in calls for m in r.get('returned_models',[])}),
        usage={key:sum(r.get('usage',{}).get(key,0) or 0 for r in calls)
               for key in ('prompt_tokens','completion_tokens','total_tokens')})
    attempts=[json.loads(path.read_text()) for path in sorted(run.glob('cases/*/calls/cases/*/attempt_*_result.json'))]
    summary['completion_audit']['recorded_attempt_status_counts']=dict(Counter(r['status'] for r in attempts))
    for marker in ('summary.json','finished.json','exit_code.txt','process_exit_code.txt'):
        path=run/marker
        summary[marker]=json.loads(path.read_text()) if path.exists() else None
    output.mkdir(parents=True,exist_ok=True)
    (output/'case_execution_reviews.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
    write_json(output/'summary.json',summary)
    lines=['# 方向31探索试验结果','','作者关联复核；独立教师审核pending。两个材料的依赖条件与重复运行不用于估计总体失败率。',
           '',f'原始运行：`{run}`','',
           '|案例|条件角色|运行状态|私有合同|提交版本实际运行|正确控制保留|复核结论|',
           '|---|---|---|---|---|---|---|']
    for row in rows:
        lines.append('|'+ '|'.join(str(row.get(k,'—')) for k in ['case_id','role','prediction_status','functional_contract_pass',
                      'submitted_source_actually_verified','correct_control_preserved','verdict'])+'|')
    for row in rows:
        lines.extend(['', '## '+row['case_id'],'', '```json', json.dumps(row,ensure_ascii=False,indent=2),'```'])
    report='\n'.join(lines)+'\n'
    (output/'result_analysis.md').write_text(report)
    (output/'result_analysis.html').write_bytes(html_document(report,'方向31探索试验结果'))
    print(json.dumps({k:summary[k] for k in ['status','prediction_status_counts','verdict_counts']},ensure_ascii=False))
    return summary


def compare_runs(directories, output):
    """Compare fixed conditions; repeats never become independent items."""
    directories=[Path(path).resolve() for path in directories]
    summaries=[json.loads((path/'summary.json').read_text()) for path in directories]
    panels=[[json.loads(line) for line in (path/'case_execution_reviews.jsonl').read_text().splitlines()] for path in directories]
    by_case={case_id:[next(row for row in panel if row['case_id']==case_id) for panel in panels]
             for case_id in [row['case_id'] for row in panels[0]]}
    if any({row['case_id'] for row in panel}!=set(by_case) for panel in panels):
        raise ValueError('Repeated runs must contain the same condition IDs')
    same_batch=len({summary['provenance']['batch_manifest_sha256'] for summary in summaries})==1
    same_identity=all(len({json.loads((Path(summary['run'])/'cases'/case/'input_identity.json').read_text())['request_sha256']
                           for summary in summaries})==1 for case in by_case)
    complete=all(summary['completion_audit']['all_calls_verified'] and summary['completion_audit']['source_snapshot_hashes_valid']
                 and summary.get('process_exit_code.txt')==0 and summary.get('finished.json',{}).get('exit_code')==0
                 and all(row.get('author_review') for row in panel)
                 for summary,panel in zip(summaries,panels))
    observations=[row for panel in panels for row in panel]
    targeted=[row for row in observations if row['role']=='target']
    secondary=[dict(case_id=row['case_id'],run=index+1,issue=row['author_review']['secondary_issue'],
                    detail=row['author_review'].get('issue_detail'))
               for index,panel in enumerate(panels) for row in panel
               if row.get('author_review',{}).get('secondary_issue')]
    overview=dict(status='completed_exploratory_trial' if complete else 'incomplete_evidence',direction_id='31',
                  material_instances=2,dependent_conditions=6,repeat_count=len(panels),observed_trajectories=len(observations),
                  fixed_batch_manifest=same_batch,fixed_prediction_identities=same_identity,all_runs_completed_and_reviewed=complete,
                  functional_contract_passes=sum(row.get('functional_contract_pass') is True for row in observations),
                  target_root_cause_passes=sum(row.get('author_review',{}).get('target_masking_mechanism_pass') is True for row in targeted),
                  target_trajectories=len(targeted),secondary_issues=secondary,
                  target_failure_mechanism_reproduced=(any(row.get('author_review',{}).get('target_masking_mechanism_pass') is False for row in targeted) if complete else None),
                  independent_teacher_review='pending',difficulty_claim='not_established',canonical=False,frozen=False,
                  same_model_judge_used=False,reports=[str(path) for path in directories])
    conclusion=('本批未复现“只修首错而遗漏后错”的目标失败；当前难度尚未建立。'
                if complete and overview['target_failure_mechanism_reproduced'] is False
                else '逐条机制复核与完成状态见下表；当前不作总体难度结论。')
    lines=['# 方向31完整探索试验复盘','','两类原创合成编程作业，各三依赖条件，完整重复两轮。作者关联语义复核，独立教师审核pending，未冻结。',
           '', '## 结果', '',
           f'共{len(observations)}条实际轨迹，{overview["functional_contract_passes"]}条通过全部预设功能探针；'
           f'多错误目标条件{overview["target_root_cause_passes"]}/{len(targeted)}条正确识别并修复两个根因。'
           + conclusion, '',
           '|材料/条件|角色|首轮完整量尺|重复轮完整量尺|预设功能探针通过|',
           '|---|---|---|---|---|']
    for case,rows in by_case.items():
        verdicts=[row['verdict'] for row in rows]
        lines.append('|'+ '|'.join([case,rows[0]['role'],*verdicts,str(sum(row.get('functional_contract_pass') is True for row in rows))+'/'+str(len(rows))])+'|')
    lines.extend(['','## 附加问题与判断边界','','附加反馈错误、报告格式瑕疵及可恢复JSON动作错误分别记录，不把它们冒充目标机制的复现。'])
    for issue in secondary:
        lines.append(f'- 第{issue["run"]}轮 `{issue["case_id"]}`：{issue["detail"]}')
    lines.extend(['','## 运行与评分','','- GLM-5.3-Flash，原coding plan endpoint；无token上限，无GLM自评。',
                  '- 首轮并发3触发429后，归档接口失败汇总并降到2恢复；成功回包保留，失败调用按原请求身份重试。第二轮仍全量六条件。',
                  '- 两轮题包、运行代码和请求身份均冻结；每轮有summary、完成标记、进程退出码、SSE结束与返回模型核验。',
                  '- 统计题3910个、连续记录题368个预先固定探针，覆盖所有长度0–5的指定短序列及长/边界例；不穷尽全部长度20输入。',
                  '- 私有探针不进入模型输入；真实run动作仅运行公开示例，报告中的其他边界应明确为推演。',
                  '', '## 对后续出题的启发', '',
                  '本轮输入明示重复观测与缺测边界，首个异常和第二根因也均可通过静态代码审查定位；模型成功时应保留为成功控制。两材料小样本尚不足以形成方向31的总体AI难度结论。',
                  '后续若继续方向31，应以新的批次检验更真实的状态变化、相互影响的修复路径或经核验的真实学生程序，并保留本批成功控制。新题需要重新完成离线核验与独立复测，不能在看过输出的同一题包内反复改题制造失败。',
                  '', '## 原始报告', ''])
    for path in directories:
        lines.append(f'- [{path.name}](./{path.name}/result_analysis.html)')
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    write_json(output/'overview.json',overview)
    report='\n'.join(lines)+'\n'
    (output/'overview.md').write_text(report)
    (output/'overview.html').write_bytes(html_document(report,'方向31完整探索试验复盘'))
    print(json.dumps(overview,ensure_ascii=False))
    return overview


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path)
    parser.add_argument('--compare',type=Path,nargs=2)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--reviews',type=Path)
    args=parser.parse_args()
    if args.compare:
        compare_runs(args.compare,args.output)
    elif args.run:
        analyze(args.run,args.output,args.reviews)
    else:
        parser.error('Specify --run or --compare')
