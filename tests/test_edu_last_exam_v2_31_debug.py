"""Offline mechanism, execution-isolation and submission regressions."""
import copy
import json
from pathlib import Path
import shutil

import pytest

from scripts.build.build_edu_last_exam_v2_pilot import validate_cards
from scripts.full_coverage import core
from scripts.full_coverage.workspace_execution import run_program, submission_checks

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / 'private/edu_last_exam_v2_31_debug'
PROTOCOL = json.loads((ROOT / 'data/edu_last_exam_v2_31_debug/protocol.json').read_text())
ITEMS = [json.loads(p.read_text()) for p in sorted((BATCH / 'authored').glob('*.json'))]


def oracle(item):
    return json.loads((BATCH / 'reference' / item['item_id'] / 'execution_oracle.json').read_text())


def test_prespecified_two_materials_six_conditions_and_no_required_historical_failure():
    assert len(ITEMS) == 2
    assert sum(len(item['prompts']) for item in ITEMS) == 6
    assert validate_cards(PROTOCOL, batch=BATCH)[2] == 0
    selection = json.loads((ROOT / 'data/edu_last_exam_v2_31_debug/selection.json').read_text())
    assert selection['selection_independent_of_glm_responses'] is True


def test_original_direction31_artifact_oracles_remain_compatible(tmp_path):
    examples=json.loads((ROOT/'private/edu_last_exam_full_coverage_v1/reference/31/oracle_cases.json').read_text())
    for index,example in enumerate(examples):
        result=core.artifact_check({'validator':'31'}, example['response_text'], tmp_path/str(index), example['prompt_id'])
        assert result['passed'] is example['expected_pass']


@pytest.mark.parametrize('item', ITEMS, ids=lambda i: i['item_id'])
def test_masked_error_single_error_counterfactual_and_correct_control(item):
    gold = oracle(item)
    contract = item['runtime']['v1']['execution_contract']
    # Both conditions have the same initial exception, before any latent logic.
    for variant in ('v1', 'v2'):
        result = run_program(item['runtime'][variant]['initial_files'], contract)
        errors = [r.get('program_error') for r in result['results'] if not r['passed']]
        assert errors and set(errors) == {gold['first_error']}
    for variant, should_pass in [('v1', False), ('v2', True)]:
        files = copy.deepcopy(item['runtime'][variant]['initial_files'])
        if gold['function_name'] == 'trimmed_mean':
            files['student.py'] = files['student.py'].replace('range(len(kept) + 1):', 'range(len(kept)):')
        else:
            files['student.py'] = files['student.py'].replace('best = max([])', 'best = 0')
        assert run_program(files, contract, gold['hidden_tests'])['passed'] is should_pass
    assert run_program(item['runtime']['v3']['initial_files'], contract, gold['hidden_tests'])['passed'] is True
    files = {'student.py': gold['reference_source']}
    assert run_program(files, contract, gold['hidden_tests'])['passed'] is True


@pytest.mark.parametrize('item', ITEMS, ids=lambda i: i['item_id'])
def test_trusted_authored_sources_match_cpython_on_all_prespecified_cases(item):
    """Only known author fixtures are compiled here; model output never is."""
    gold = oracle(item)
    sources = [r['initial_files']['student.py'] for r in item['runtime'].values()]
    sources += [gold['reference_source'], gold['first_repair_source']]
    for source in sources:
        scope = {}
        exec(compile(source, '<trusted author fixture>', 'exec'), scope)
        function = scope[gold['function_name']]
        result = run_program({'student.py': source}, item['runtime']['v1']['execution_contract'], gold['hidden_tests'])
        for row in result['results']:
            try:
                actual = function(list(row['input']))
            except (IndexError, ValueError, TypeError, ZeroDivisionError) as exc:
                assert row.get('program_error') == type(exc).__name__
            else:
                assert row.get('program_error') is None
                assert row['observed'] == actual


def test_public_messages_exclude_gold_roles_and_private_probes():
    for item in ITEMS:
        for prompt in item['prompts']:
            messages, _, unsupported = core.prepare_messages(BATCH, prompt)
            text = json.dumps(messages, ensure_ascii=False)
            assert not unsupported
            for private_key in ('accepted_root_causes', 'isolated_second_error_input', 'hidden_tests',
                                'single_error_counterfactual', 'reference_source'):
                assert private_key not in text
            assert '缺测' in text if item['item_id'].endswith('002') else '相同数值' in text


def test_workspace_run_uses_current_source_and_requires_verification_after_last_edit(tmp_path):
    item = ITEMS[0]
    gold = oracle(item)
    runtime = item['runtime']['v1']
    commands = [dict(action='run'),
                dict(action='write', path='student.py', content=gold['reference_source']),
                dict(action='run'),
                dict(action='write', path='report.json', content='{"diagnosis":[],"feedback":"fixture","verification":"actual run"}'),
                dict(action='submit')]
    iterator = iter(commands)
    recorded = []
    def call(messages, index):
        recorded.append(copy.deepcopy(messages))
        return dict(status='generated', response=json.dumps(next(iterator)))
    result = core.execute_episode(dict(runtime=runtime, prompt_id='v1', messages=[dict(role='user',content='公开任务')]), call, tmp_path)
    runs = [e['observation'] for e in result['events'] if e['command']['action']=='run']
    assert runs[0]['passed'] is False and runs[1]['passed'] is True
    assert runs[0]['source_sha256'] != runs[1]['source_sha256']
    assert all(check['passed'] for check in result['artifact_checks'])
    assert 'IndexError' in json.dumps(recorded[1],ensure_ascii=False)
    files = copy.deepcopy(runtime['initial_files'])
    files['student.py'] = gold['reference_source'] + '\n'
    assert submission_checks(files, runtime, result['events'])['passed'] is False


def test_unsafe_program_and_unconfigured_execution_are_rejected():
    runtime = ITEMS[0]['runtime']['v1']
    for source in ['import os\ndef trimmed_mean(values):\n    return 0\n',
                   'def trimmed_mean(values):\n    return values.__class__\n']:
        result = run_program({'student.py': source}, runtime['execution_contract'])
        assert result['passed'] is False and result['program_error'] == 'Unsupported'
    observation, done = core.workspace_action({'action':'run'}, {}, {'initial_files':{}, 'writable_paths':[]})
    assert observation['error'] == 'unknown_action' and not done


def test_execution_contract_cannot_select_external_source_or_engine():
    for patch in [{'source_path':'/etc/passwd'}, {'engine':'arbitrary_python_exec'}]:
        runtime = copy.deepcopy(ITEMS[0]['runtime']['v1'])
        runtime['execution_contract'].update(patch)
        with pytest.raises(ValueError):
            core.validate_runtime(runtime)


def test_analysis_does_not_promote_functional_success_to_semantic_pass(tmp_path):
    from scripts.experiments.analyze_edu_last_exam_v2_31_debug import analyze

    run = tmp_path / 'trial/GLM-5.3-Flash'
    snapshot = run.parent / 'source_snapshot/private/edu_last_exam_v2_31_debug'
    shutil.copytree(BATCH, snapshot)
    for relative in ['scripts/full_coverage/core.py', 'scripts/full_coverage/workspace_execution.py',
                     'scripts/full_coverage/directions/d31.py']:
        target=run.parent/'source_snapshot'/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/relative,target)
    for item in ITEMS:
        gold = oracle(item)
        for prompt in item['prompts']:
            variant = prompt['prompt_id']
            directory = run / 'cases' / (item['item_id'] + '__' + variant)
            workspace = directory / 'workspace'
            workspace.mkdir(parents=True)
            source = item['runtime'][variant]['initial_files']['student.py'] if variant=='v3' else gold['reference_source']
            (workspace / 'student.py').write_text(source)
            # Deliberately incomplete diagnosis: execution alone cannot clear it.
            report = {'diagnosis': [], 'feedback': 'mock', 'verification': 'mock'}
            (workspace / 'report.json').write_text(json.dumps(report))
            observation = run_program({'student.py': source}, item['runtime'][variant]['execution_contract'])
            result = dict(status='generated', model_turns=3, environment_completed=True,
                          events=[dict(command=dict(action='run'), observation=observation)],
                          artifact_checks=[dict(passed=True)], transcript=[dict(response='mock')])
            core.write_json(directory / 'result.json', result)
    summary = analyze(run, tmp_path/'analysis')
    assert summary['verdict_counts'] == {'semantic_review_pending': 6}
    rows = [json.loads(line) for line in (tmp_path/'analysis/case_execution_reviews.jsonl').read_text().splitlines()]
    first = rows[0]
    review = dict(case_id=first['case_id'], prediction_sha256=first['prediction_sha256'],
                  report_sha256=first['report_sha256'], evidence=[dict(quote='INVENTED_QUOTE')])
    core.write_json(tmp_path/'reviews.json', {'cases':[review]})
    with pytest.raises(ValueError, match='Unverified author evidence'):
        analyze(run, tmp_path/'analysis_invalid', tmp_path/'reviews.json')
    engine=run.parent/'source_snapshot/scripts/full_coverage/directions/d31.py'
    engine.write_text(engine.read_text()+'\n')
    with pytest.raises(ValueError,match='Execution engine differs'):
        analyze(run,tmp_path/'analysis_wrong_engine')


def test_evidence_quotes_use_decoded_json_field_values():
    from scripts.experiments.analyze_edu_last_exam_v2_31_debug import text_values
    report=json.loads('{"diagnosis":[{"cause":"violates \\"exactly one\\" observation"}]}')
    assert 'violates "exactly one" observation' in '\n'.join(text_values(report))
