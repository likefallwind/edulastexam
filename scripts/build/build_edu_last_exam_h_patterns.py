#!/usr/bin/env python3
"""Export the H-pattern candidate batch with deterministic content/runtime checks.

This checks bounded mathematics and environment contracts, not semantic teaching quality.
No API calls and no claim of independent human review.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction
import json
from pathlib import Path
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage import core
from scripts.build.build_edu_last_exam_v2_pilot import validate_cards
from scripts.build.build_edu_last_exam_full_coverage import build

PROTOCOL = ROOT / 'data/edu_last_exam_h_patterns_v1/protocol.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def oracle_check(oracle):
    """Independently recompute numerical reference records using exact arithmetic."""
    kind = oracle['kind']
    if kind == 'ratio':
        require(Fraction(oracle['numerator'], oracle['denominator']) * oracle['scale'] == oracle['result'], 'ratio gold')
    elif kind == 'polynomial_roots':
        a, b, c = oracle['coefficients']
        # These candidates have x(x-3); validate the full factorization, not sampled roots only.
        require((a,b,c) == (1,-3,0), 'unexpected polynomial')
        require(sorted(set([0,3]) - set(oracle['excluded'])) == oracle['result'], 'root set gold')
    elif kind == 'root_identity':
        points = [-5, 0, Fraction(3,2)] if oracle['domain'] == 'lt2' else [Fraction(5,2),3,8]
        for a in points:
            expected = abs(a-2)
            actual = 2-a if oracle['result'] == '2-a' else a-2
            require(actual == expected, 'absolute value gold')
    elif kind == 'fraction_bars':
        shades = [Fraction(*f)*oracle['whole'] for f in oracle['fractions']]
        require(shades == oracle['shades'], 'bar geometry gold')
        fractions = [Fraction(*f) for f in oracle['transfer']]
        require(fractions[0] < fractions[1], 'transfer comparison gold')
        require([f*oracle['denominator'] for f in fractions] == oracle['numerators'], 'transfer numerator gold')
    elif kind == 'density':
        require(all(Fraction(*r)==oracle['density'] for r in oracle['rows']), 'density demonstration gold')
        require(Fraction(*oracle['transfer'])==oracle['transfer_density'], 'density transfer gold')
    elif kind == 'linear':
        require(all(oracle['slope']*x+oracle['intercept']==y for x,y in oracle['points']), 'graph gold')
        require(oracle['transfer_slope']*oracle['transfer_x']+oracle['transfer_intercept']==oracle['transfer_y'], 'linear transfer gold')
    else:
        raise ValueError(f'Unknown oracle {kind}')


def recorded_episode(item, prompt, directory, commands):
    messages, _, unsupported = core.prepare_messages(Path('.'), prompt)
    require(not unsupported, 'unsupported input')
    answers = iter(commands)
    calls = []
    def call(messages, index):
        calls.append(messages)
        return {'status':'generated', 'response':json.dumps(next(answers), ensure_ascii=False)}
    task={'item_id':item['item_id'],'prompt_id':prompt['prompt_id'], 'runtime':item['runtime'][prompt['prompt_id']], 'messages':messages}
    return core.execute_episode(task, call, directory), calls


def validate_content(items, batch):
    results=[]
    for item in items:
        direction=item['direction_id']
        prompts=item['prompts']
        refs={pid:g['reference_answer'] for pid,g in item['gold']['per_prompt'].items()}
        require(item['status']['model_evaluation']=='not_run' and not item['status']['frozen'], 'unearned evidence status')
        for p in prompts:
            public=p['system_prompt']+p['user_prompt']
            require(not any(marker in public for marker in ['reference_answer','critical_errors','preferred_actions','offline_oracle','正确控制','双缺陷']), 'private role or gold in prompt')
            ref=refs[p['prompt_id']]
            if 'offline_oracle' in ref:
                oracle_check(ref['offline_oracle'])
        if direction=='02':
            for p in prompts:
                ref=refs[p['prompt_id']];o=ref['offline_oracle'];public=p['user_prompt']
                if o['kind']=='ratio':
                    counts=[tuple(map(int,x)) for x in re.findall(r'实际参测(\d+)人，答对(\d+)人',public)]
                    require(len(counts)==2, 'missing public sample counts')
                    total=sum(x[0] for x in counts);right=sum(x[1] for x in counts)
                    require((o['numerator'],o['denominator'])==(right,total),'public/oracle counts drift')
                    require(Fraction(right,total)*100==ref['correct_result'],'public ratio/reference drift')
                elif o['kind']=='polynomial_roots':
                    excluded=[0] if '另有条件x≠0' in public else []
                    require(o['excluded']==excluded and ref['correct_result']==o['result'],'public roots/reference drift')
                else:
                    require(('已知实数a<2' in public)==(o['domain']=='lt2'),'public domain drift')
                    require(ref['correct_result']==o['result'],'absolute-value reference drift')
            require([refs[p['prompt_id']]['score'] for p in prompts]==[4,0,4],'method/score controls')
        if direction=='12':
            normalized=[re.sub(r'作答条件记录：[^\n]*','作答条件记录：MASK',p['user_prompt']) for p in prompts]
            require(len(set(normalized))==1,'help counterfactual changes other content')
            require([refs[p['prompt_id']]['latest_evidence'] for p in prompts]==['independent_observed','supported_observed','help_unknown'],'assistance states')
        if direction=='05':
            normalized=[re.sub(r'外部评分记录：[^\n]*','外部评分记录：MASK',p['user_prompt']) for p in prompts]
            require(len(set(normalized))==1,'mark counterfactual changes other content')
            require(len({refs[p['prompt_id']]['score'] for p in prompts})==1,'anchor changed gold')
            expected=2 if item['item_id'].endswith('102') else 4
            require(refs['v1']['score']==expected,'partial/full anchor gold')
        if direction=='23':
            require([refs[p['prompt_id']]['targets_actual_error'] for p in prompts]==[True,False,False,True],'2x2 targeting gold')
            require(all(refs[p['prompt_id']]['check_initiated'] for p in prompts),'implicit check behavior')
            works=[p['user_prompt'].split('学生完整作品：\n')[1].split('\n老师最新回复：')[0] for p in prompts]
            questions=[p['user_prompt'].split('老师最新回复：')[1].split('\n请分别判断')[0] for p in prompts]
            require(works[0]==works[1] and works[2]==works[3] and works[0]!=works[2],'student cross')
            require(questions[0]==questions[2] and questions[1]==questions[3] and questions[0]!=questions[1],'question cross')
        if direction=='10':
            initial_menus=[core.action_menu(item['runtime'][p['prompt_id']],'s0') for p in prompts]
            require(len(set(initial_menus))==1,'menu reveals condition')
            normalized=[re.sub(r'最近G2记录：[^\n]*','最近G2记录：MASK',p['user_prompt']) for p in prompts]
            require(len(set(normalized))==1,'flow counterfactual changes other content')
            for p in prompts:
                with tempfile.TemporaryDirectory() as tmp:
                    commands=[{'action':a,'message':'离线接口测试占位文字，不作为语义合格样本。'} for a in refs[p['prompt_id']]['preferred_actions']]
                    result,calls=recorded_episode(item,p,Path(tmp),commands)
                    require(result['environment_completed'] and result['status']=='generated','reference action path incomplete')
                    require([e['action'] for e in result['events']]==refs[p['prompt_id']]['preferred_actions'],'action path drift')
                    require('preferred_actions' not in json.dumps(calls),'private action path leaked')
                    early,_=recorded_episode(item,p,Path(tmp)/'early',[{'action':'finish','message':'提前结束。'}])
                    require(early['environment_completed'] and not early['artifact_checks'],'termination must not be a teaching pass')
        if direction=='14':
            for p in prompts:
                pid=p['prompt_id'];rt=item['runtime'][pid];ref=refs[pid]
                files=copy.deepcopy(rt['initial_files'])
                for path,content in files.items():
                    require((batch/'stimuli'/item['item_id']/pid/path).read_text()==content,'workspace review copy drift')
                student=ref['final_student'];teacher=ref['final_teacher'];o=ref['offline_oracle']
                if o['kind']=='fraction_bars':
                    require([x['shaded_length'] for x in student['page1']['bars']]==o['shades'],'bar file/oracle drift')
                    require(all(x['whole_length']==o['whole'] for x in student['page1']['bars']),'unequal wholes')
                    require(teacher['page2']['numerators']==o['numerators'],'transfer file/oracle drift')
                elif o['kind']=='density':
                    require(student['page1']['rows']==o['rows'],'density file/oracle drift')
                    require(teacher['page2']['density_g_per_cm3']==o['transfer_density'],'density key drift')
                else:
                    require(student['page1']['points']==o['points'],'graph file/oracle drift')
                    require(teacher['page2']['y_at_4']==o['transfer_y'],'graph transfer key drift')
                require(student['page2']['answer'] is None and student['page2']['hint'] is None,'student transfer leakage')
                commands=[]
                for path,expected in [('student/current.json',student),('teacher/current.json',teacher)]:
                    if json.loads(files[path])!=expected:
                        files[path]=json.dumps(expected,ensure_ascii=False)
                        commands.append({'action':'write','path':path,'content':files[path]})
                delivery=dict(state='draft',artifact='student/current.json',teacher_reference='teacher/current.json',changed_ids=ref['changed_ids'],feedback='离线文件合同正例；教学解释仍待语义审核。')
                files['delivery.json']=json.dumps(delivery,ensure_ascii=False)
                require(core.validate_workspace(files,rt)['passed'],'reference files rejected')
                # Negative fixtures: no real repair, invented change log, and answer leakage.
                uncorrected={**rt['initial_files'],'delivery.json':files['delivery.json']}
                require(core.validate_workspace(uncorrected,rt)['passed']==(pid=='v3'),'initial defects not distinguished')
                missing={k:v for k,v in files.items() if k!='delivery.json'}
                require(not core.validate_workspace(missing,rt)['passed'],'missing delivery accepted')
                leaked=copy.deepcopy(files);badstudent=copy.deepcopy(student);badstudent['page2']['answer']='教师答案'
                leaked['student/current.json']=json.dumps(badstudent,ensure_ascii=False)
                require(not core.validate_workspace(leaked,rt)['passed'],'answer leakage accepted')
                wrong=copy.deepcopy(files);baddelivery=copy.deepcopy(delivery);baddelivery['changed_ids']=['invented']
                wrong['delivery.json']=json.dumps(baddelivery)
                require(not core.validate_workspace(wrong,rt)['passed'],'invented change log accepted')
                commands += [{'action':'write','path':'delivery.json','content':files['delivery.json']},{'action':'read','path':'delivery.json'},{'action':'submit','message':'离线接口正例。'}]
                with tempfile.TemporaryDirectory() as tmp:
                    result,calls=recorded_episode(item,p,Path(tmp),commands)
                    require(result['environment_completed'] and result['artifact_checks'][0]['passed'],'workspace episode failed')
                    require('submit_checks' not in json.dumps(calls),'private workspace checks leaked')
        results.append({'item_id':item['item_id'],'status':'passed','scope':'deterministic_content_and_runtime_only'})
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    protocol=json.loads(PROTOCOL.read_text());batch=ROOT/protocol['batch']
    _,evidence_hashes,_=validate_cards(protocol,batch)
    items=core.load_items(batch,item_glob=protocol['item_glob'],item_id_pattern=protocol['item_id_pattern'],expected_item_ids=protocol['expected_item_ids'])
    results=validate_content(items,batch)
    protocol['validation_extra']['deterministic_content_checks']=results
    protocol['manifest_extra']['source_evidence_sha256']=evidence_hashes
    build(batch,validate_only=args.validate_only,check=args.validate_only,protocol=protocol)

if __name__=='__main__':
    main()
