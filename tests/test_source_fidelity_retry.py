import copy
import json

import pytest

from scripts.source_fidelity.group_27_37 import parse_agent_action


def test_agent_action_extraction_preserves_code_and_accepts_prose():
    action = {'action': 'write_file', 'path': 'slides.py',
              'content': 'payload = {"nested": "value"}\nprint(payload)\n'}
    assert parse_agent_action('I will write the file.\n```json\n' + json.dumps(action) + '\n```') == action


@pytest.mark.parametrize('text', [
    '{"action":"exec","command":["true"]}\n{"action":"exec","command":["false"]}',
    '{"action":"write_file","content":"unterminated}',
    '[{"action":"exec","command":["true"]}]',
    'No action here',
    'I will write a configuration: {"action":"write_file","path":"config.json","content":{"action":"finish"}',
])
def test_ambiguous_or_incomplete_action_never_executes(text):
    with pytest.raises(ValueError):
        parse_agent_action(text)


def test_retry_does_not_change_original_system_or_retry_successes():
    from scripts.experiments.retry_edu_last_exam_source_fidelity import retry_task
    original = {'case_id': 'ELE-SF-23-001', 'prediction': {
        'messages': [{'role':'system','content':'EXACT ORIGINAL TASK'}]}}
    before = copy.deepcopy(original)
    adapted = retry_task(original, {'status':'api_error'})
    assert original == before
    assert adapted['prediction']['messages'][0] == before['prediction']['messages'][0]
    assert adapted['prediction']['messages'][1] == {'role':'user','content':'Please complete the task above.'}
    with pytest.raises(ValueError, match='successful'):
        retry_task(original, {'status':'generated'})
    with pytest.raises(ValueError, match='unavailable'):
        retry_task(original, {'status':'original_condition_unavailable_not_measured'})


def test_socratic_role_split_preserves_all_original_content():
    from scripts.experiments.retry_edu_last_exam_source_fidelity import retry_task
    text = 'Instructions\n\nProblem: example\nQuestions: example questions\n\nProblem: actual\nQuestions:\n'
    original = {'case_id':'ELE-SF-23-001','prediction':{'messages':[{'role':'system','content':text}]}}
    result = retry_task(original, {'status':'empty_response'}, 'split_roles')
    assert ''.join(m['content'] for m in result['prediction']['messages']) == text
    assert result['prediction']['messages'][1]['content'] == '\n\nProblem: actual\nQuestions:\n'


def test_original_stop_is_applied_only_to_visible_content():
    from scripts.experiments.retry_edu_last_exam_source_fidelity import retry_task, visible_stop_result
    original={'case_id':'ELE-SF-23-001','prediction':{'messages':[{'role':'system','content':'Instructions\n\nProblem: question\nQuestions:'}], 'parameters':{'stop':['Problem:','\n']}}}
    adapted=retry_task(original,{'status':'empty_response'},'split_roles_client_stop')
    assert 'stop' not in adapted['prediction']['parameters']
    assert original['prediction']['parameters']['stop']==['Problem:','\n']
    answer={'status':'generated','response':'How many? What total?\nProblem: extra','reasoning':'line one\nline two','transcript':[{'response':'How many? What total?\nProblem: extra'}]}
    processed=visible_stop_result(answer,adapted['retry_protocol']['visible_content_stop'])
    assert processed['response']=='How many? What total?'
    assert processed['reasoning']==answer['reasoning']
    assert processed['raw_response']==answer['response']
    assert visible_stop_result(processed,adapted['retry_protocol']['visible_content_stop'])==processed
