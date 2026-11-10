"""Continuous scoring of held-out response predictions; passed means schema only."""
import json, math, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]

def parse(text):
    try:return json.loads(text)
    except (ValueError,TypeError):pass
    for match in re.finditer(r'```(?:json)?\s*([\s\S]*?)```',text):
        try:return json.loads(match.group(1))
        except ValueError:pass
    raise ValueError('Expected one JSON object.')

def validate_artifact(response_text, output_dir, prompt_id):
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    try:
        obj=parse(response_text);assert isinstance(obj,dict),'Top-level JSON object required.';pred=obj['predictions'];assert isinstance(pred,dict),'predictions must be an object keyed by question_id.'
        ref=json.loads((ROOT/'private/edu_last_exam_full_coverage_v1/reference/17/heldout_rates.json').read_text())
        assert set(pred)==set(ref['targets']), 'Target question ids must match the task.'
        for x in pred.values():
            assert isinstance(x,dict), 'Each prediction must be an object.'
            assert all(isinstance(x[k],(int,float)) and not isinstance(x[k],bool) and math.isfinite(x[k]) for k in ['p','lower','upper']), 'Probabilities must be finite numbers.'
            assert 0<=x['lower']<=x['p']<=x['upper']<=1, 'Require 0 <= lower <= p <= upper <= 1.'
        targets=ref['targets'];ids=list(targets)
        mae=sum(abs(pred[q]['p']-targets[q]['rate']) for q in ids)/len(ids)
        pairs=[(a,b) for i,a in enumerate(ids) for b in ids[i+1:]]
        pair_acc=sum(1 if (pred[a]['p']-pred[b]['p'])*(targets[a]['rate']-targets[b]['rate'])>0 else .5 if pred[a]['p']==pred[b]['p'] else 0 for a,b in pairs)/len(pairs)
        baseline=sum(abs(ref['pooled_calibration_baseline']-targets[q]['rate']) for q in ids)/len(ids)
        metrics={'heldout_MAE':mae,'pairwise_order_accuracy':pair_acc,'pooled_calibration_baseline_MAE':baseline,'descriptive_interval_coverage':sum(pred[q]['lower']<=targets[q]['rate']<=pred[q]['upper'] for q in ids)/len(ids),'mean_interval_width':sum(pred[q]['upper']-pred[q]['lower'] for q in ids)/len(ids)}
        (output_dir/'predictions.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
        return {'passed':True,'pass_meaning':'schema_validity_only_not_prediction_correctness','evaluation_type':'continuous','checks':[{'id':'prediction_schema','passed':True}],'metrics':metrics,'public_feedback':'JSON结构和概率范围有效。隐藏目标比例与误差只在完成评测后统计，不用于修复提示。'}
    except (ValueError,TypeError,KeyError,AssertionError,OverflowError) as exc:
        return {'passed':False,'pass_meaning':'schema_validity_only_not_prediction_correctness','evaluation_type':'continuous','checks':[{'id':'prediction_schema','passed':False,'detail':str(exc)}],'public_feedback':str(exc)}
