"""Offline content, leakage and counterfactual safeguards for H-pattern candidates."""
import copy
import json
from pathlib import Path

import pytest

from scripts.build import build_edu_last_exam_h_patterns as hp
from scripts.build.build_edu_last_exam_v2_pilot import validate_cards
from scripts.full_coverage import core

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=json.loads(hp.PROTOCOL.read_text())
BATCH=ROOT/PROTOCOL['batch']
ITEMS=core.load_items(BATCH,item_glob=PROTOCOL['item_glob'],item_id_pattern=PROTOCOL['item_id_pattern'],expected_item_ids=PROTOCOL['expected_item_ids'])


def test_sources_exports_and_candidate_status():
    validate_cards(PROTOCOL,BATCH)
    assert len(ITEMS)==18
    assert sum(len(i['prompts']) for i in ITEMS)==57
    assert {d:sum(i['direction_id']==d for i in ITEMS) for d in ['02','05','10','12','14','23']}==dict.fromkeys(['02','05','10','12','14','23'],3)
    assert len(hp.validate_content(ITEMS,BATCH))==18
    exported=[json.loads(line) for line in (BATCH/'prompts.jsonl').read_text().splitlines()]
    for p in exported:
        assert set(p)=={'item_id','direction_id','prompt_id','system_prompt','user_prompt','assets','interaction_mode'}
    manifest=json.loads((BATCH/'manifest.json').read_text())
    assert manifest['prediction_export_sha256']==core.digest((BATCH/'prompts.jsonl').read_bytes())
    assert manifest['runtime_sha256']==core.digest((BATCH/'runtimes.json').read_bytes())
    assert manifest['item_export_sha256']==core.digest((BATCH/'items.jsonl').read_bytes())
    assert manifest['model_evaluation']=='not_run' and manifest['human_review']=='pending'
    assert not manifest['canonical'] and not manifest['frozen']


@pytest.mark.parametrize('kind', ['ratio','polynomial_roots','root_identity','fraction_bars','density','linear'])
def test_wrong_numerical_oracle_is_rejected(kind):
    oracle=next(copy.deepcopy(g['reference_answer']['offline_oracle']) for i in ITEMS for g in i['gold']['per_prompt'].values() if g['reference_answer'].get('offline_oracle',{}).get('kind')==kind)
    if kind=='ratio': oracle['result']+=1
    elif kind=='polynomial_roots': oracle['result']=[999]
    elif kind=='root_identity': oracle['result']='a-2'
    elif kind=='fraction_bars': oracle['numerators'][1]-=1
    elif kind=='density': oracle['transfer_density']=0.4
    else: oracle['transfer_y']+=4
    with pytest.raises(ValueError): hp.oracle_check(oracle)


def test_changes_outside_mark_and_help_conditions_are_rejected():
    for direction,match in [('05','mark counterfactual'),('12','help counterfactual'),('10','flow counterfactual')]:
        item=copy.deepcopy(next(i for i in ITEMS if i['direction_id']==direction))
        item['prompts'][1]['user_prompt']+='\n额外改变的背景条件。'
        with pytest.raises(ValueError,match=match):hp.validate_content([item],BATCH)


def test_gold_that_drifts_from_visible_counts_is_rejected():
    item=copy.deepcopy(next(i for i in ITEMS if i['item_id']=='ELE-V2-02-101'))
    item['prompts'][0]['user_prompt']=item['prompts'][0]['user_prompt'].replace('答对16人','答对15人')
    with pytest.raises(ValueError,match='public/oracle counts drift'): hp.validate_content([item],BATCH)


def test_crossed_questions_require_target_flip():
    item=copy.deepcopy(next(i for i in ITEMS if i['direction_id']=='23'))
    item['gold']['per_prompt']['v2']['reference_answer']['targets_actual_error']=True
    with pytest.raises(ValueError,match='2x2 targeting'):hp.validate_content([item],BATCH)


def test_premature_finish_is_not_an_automatic_semantic_pass(tmp_path):
    item=next(i for i in ITEMS if i['direction_id']=='10')
    result,_=hp.recorded_episode(item,item['prompts'][0],tmp_path,[{'action':'finish','message':'全部已经掌握。'}])
    assert result['environment_completed'] is True
    assert result['artifact_checks']==[]
    assert [e['action'] for e in result['events']]==['finish']
    # This transcript must fail semantic review; the environment only records termination.
    assert '未回应插问就关闭会话。' in item['gold']['per_prompt']['v1']['critical_errors']


def test_workspace_claim_without_writes_fails_and_gold_is_not_disclosed(tmp_path):
    item=next(i for i in ITEMS if i['direction_id']=='14')
    result,calls=hp.recorded_episode(item,item['prompts'][0],tmp_path,[{'action':'submit','message':'已修复并写delivery。'}])
    assert result['environment_completed']
    assert not result['artifact_checks'][0]['passed']
    assert 'submit_checks' not in json.dumps(calls)
    assert not (tmp_path/'workspace/delivery.json').exists()


def test_author_model_evaluation_cannot_be_silently_claimed():
    item=copy.deepcopy(ITEMS[0]);item['status']['model_evaluation']='passed'
    with pytest.raises(ValueError,match='unearned evidence status'):hp.validate_content([item],BATCH)
