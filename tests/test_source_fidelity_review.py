import hashlib
import json

import pytest

from scripts.build.build_edu_last_exam_source_fidelity_review import latest_reviews, validate_review


def fixture_review(tmp_path,status='generated'):
    path=tmp_path/'run/cases/ELE-SF-01-001/result.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'status':status,'response':'Original answer'}))
    return {'case_id':'ELE-SF-01-001','direction_ids':['01'],'source_run':'run',
            'prediction_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'reviewer':'Codex','review_scope':'author_related_offline_review',
            'verdict':'pass','reason':'Meets explicit requirement',
            'criteria':[{'criterion':'Required answer','judgment':'pass','evidence':'Original answer'}],
            'evidence':[{'path':str(path),'quote':'Original answer'}],
            'native_score_interpretation':'Separate original metric','limitations':[]},path


def test_review_cannot_silently_follow_a_changed_prediction(tmp_path):
    row,path=fixture_review(tmp_path)
    assert validate_review(row,tmp_path)['status']=='generated'
    path.write_text(json.dumps({'status':'generated','response':'Different answer'}))
    with pytest.raises(ValueError,match='prediction changed'):
        validate_review(row,tmp_path)


def test_incomplete_prediction_is_not_a_reviewed_correct_or_wrong_answer(tmp_path):
    row,path=fixture_review(tmp_path,'api_error')
    with pytest.raises(ValueError,match='Incomplete'):
        validate_review(row,tmp_path)


def test_failed_retry_resolves_pending_without_hiding_a_completed_answer():
    rows=[{'case_id':'one','source_run':'01','verdict':'pending_rerun'},
          {'case_id':'one','source_run':'02','verdict':'not_evaluable'},
          {'case_id':'two','source_run':'01','verdict':'pass'},
          {'case_id':'two','source_run':'02','verdict':'not_evaluable'}]
    predictions={('01','one'):{'status':'api_error'},('02','one'):{'status':'empty_response'},
                 ('01','two'):{'status':'generated'},('02','two'):{'status':'api_error'}}
    latest=latest_reviews(rows,predictions)
    assert latest['one']['verdict']=='not_evaluable'
    assert latest['two']['verdict']=='pass'
