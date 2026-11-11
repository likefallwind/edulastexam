"""Offline regression for preserving source metrics, without API or model output."""
import json
from pathlib import Path
import pytest
from scripts.source_fidelity import group_14_26 as adapter

ROOT=Path(__file__).resolve().parents[1]

def task(n,i=1):
    return json.loads((ROOT/f'private/edu_last_exam_source_fidelity_v1/authored/ELE-SF-{n:02}-{i:03}.json').read_text())

def record(n,metrics,i=1):
    return {'case_id':f'ELE-SF-{n:02}-{i:03}','status':'scored_native','metrics':metrics}

def test_qwk_uses_full_rating_scale_and_undefined_is_null():
    rows=[record(22,{'rating':p,'qwk_pair':[g,p]},i) for i,(g,p) in enumerate([(1,1),(2,2),(4,2),(5,4),(6,5)],1)]
    result=adapter.aggregate(rows,ROOT)['22']
    assert result['scale']==[1,6]
    assert result['qwk']==pytest.approx(21/26)
    perfect=adapter.aggregate([record(22,{'rating':1,'qwk_pair':[1,1]})],ROOT)['22']
    assert perfect['qwk'] is None

def test_calibration_native_90_threshold_and_tied_auroc():
    rows=[record(26,{'confidence':c,'calibration_pair':[c,y]},i) for i,(c,y) in enumerate([(90,True),(90,False),(80,False)],1)]
    result=adapter.aggregate(rows,ROOT)['26']
    assert result['cwr_at_90']==0.5
    assert result['auroc']==0.75
    assert result['brier']==pytest.approx((.01+.81+.64)/3)
    assert result['ece_10bin']==pytest.approx((2*.4+.8)/3)
    result=adapter.aggregate([record(26,{'confidence':80,'calibration_pair':[80,True]})],ROOT)['26']
    assert result['cwr_at_90'] is None
    assert result['auroc'] is None

def test_selfcheck_does_not_invent_fix_denominator():
    result=adapter.aggregate([record(25,{'r1_correct':True,'r2_correct':False})],ROOT)['25']
    assert result['fix_rate'] is None
    assert result['break_rate']==1

def test_original_socratic_reference_and_metric():
    t=task(23);refs=[x.split(' ** ')[0] for x in t['reference']['answer'].split('\n') if ' ** ' in x]
    result=adapter.score(t,{'response':refs[0]},None,ROOT,ROOT)
    assert result['metrics']['bleu']==pytest.approx(1)
    assert 'correct' not in result['metrics']

def test_lda_scores_all_independent_contexts_and_original_scale(tmp_path):
    t=task(21);values=iter([2,2,1,4]);calls=[]
    def call(messages,**kwargs):
        calls.append(messages)
        return {'status':'generated','response':json.dumps({'score':next(values),'reason':'fixture'})}
    pred=adapter.run(t,call,tmp_path,ROOT);result=adapter.score(t,pred,None,tmp_path,ROOT)
    assert len(calls)==4
    assert result['metrics']['high_minus_low']==3
    assert result['metrics']['neutral_minus_base']==0
    assert result['metrics']['scale']==[0,5]
    assert all(len(x)==2 for x in calls)

def test_mooccube_rejects_extra_concept():
    t=task(24,2);names=[x['name'] for x in t['reference']['concepts']]
    r=adapter.score(t,{'response':'答案：'+' -> '.join([*names,'未提供的概念'])},None,ROOT,ROOT)
    assert r['metrics']['unparsed']
    assert not r['metrics']['correct']

def test_calibration_uses_last_explicit_answer_line():
    t=task(26);gold=t['reference']['answer'];wrong=next(k for k in 'ABCD' if k!=gold)
    r=adapter.score(t,{'response':f'答案：{wrong}\n答案：{gold}\n置信度: 89'},None,ROOT,ROOT)
    assert r['metrics']['correct']
    assert r['metrics']['confidence']==89
    assert r['metrics']['high_confidence_threshold']==90

def test_native_artifact_input_and_runtime_identity():
    for n in (19,20):
        assert adapter.validate(task(n),ROOT)['passed']
