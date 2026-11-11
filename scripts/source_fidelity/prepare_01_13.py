"""Rebuild directions01–13 from the pinned downloaded snapshots; no network or API calls."""
from pathlib import Path
import sys,json,hashlib,ast,random,copy,re,shutil,subprocess,datetime,typing,importlib.util
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.source_fidelity.group_01_13 import functions,lda
B=Path('sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13');base=ROOT/B
A=ROOT/'private/edu_last_exam_source_fidelity_v1/authored';D=ROOT/'data/edu_last_exam_source_fidelity_v1/directions'
manifest=json.loads((base/'snapshot_manifest.json').read_text())
def h(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def write(p,o):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def asset(p,role='provenance'):return {'path':str(p),'sha256':h(p),'role':role}
def source(repo,p,locator):
 m=manifest[repo];return {'source_id':repo,'title':repo+' original repository','url':m['url'].removesuffix('.git'),'local_path':str(p),'sha256':h(p),'revision':m['revision'],'locator':locator,'verified_at':'2026-11-10','evidence_excerpt':locator+'; original code/data inspected, not inferred from prior inventory.'}
def task(d,n,title,repo,p,prompt,scorer,messages,ref):
 m=manifest[repo];return {'case_id':f'ELE-SF-{d}-{n:03}','direction_ids':[d],'title':title,'origin':'original_task','source':{'url':m['url'].removesuffix('.git'),'revision':m['revision'],'case_id':ref.get('source_id',''),'record_path':str(p),'sha256':h(p),'prompt_builder_path':str(prompt),'scorer_path':str(scorer)},'fidelity':{'task_condition':'Original released task and subset selection','input':'Original prompt and all task-visible evidence','output':'Original response contract','scoring':'Original scorer; unavailable native judge is pending','environment':'Original text API contract; GLM-5.3-Flash replaces only tested model','deviations':[],'scope':'native_subset'},'selection_reason':'First three available source records in published file order, independent of GLM responses. Paired conditions remain in one unit.','prediction':{'messages':messages,'parameters':{},'interaction':{'mode':'single_turn'}},'scoring':{'mode':'native_adapter','native_metric':'native','module':'scripts.source_fidelity.group_01_13','args':{}},'assets':[asset(p),asset(prompt),asset(scorer)],'reference':ref,'review':{'human_review':'pending','author_offline_check':'pending'}}
def audit(d,title,repo,loc,condition,finding,contract,ids,limitations,status='ready_original',route='original_task'):
 p=B/repo/loc.split('::')[0];src=source(repo,p,loc)
 obj={'direction_id':d,'title':title,'status':status,'sources':[src],'research_failure':{'condition':condition,'finding':finding,'model_setting':'As released in the original source; this is a GLM source-task subset, not a reproduction of published model population.','scope':'Only the specified task condition; no generalized failure prevalence or learning-gain claim.','source_id':repo,'locator':loc},'original_task':{'available':True,'input_contract':contract[0],'output_contract':contract[1],'scoring_contract':contract[2],'environment_contract':contract[3],'source_case_ids':ids},'decision':{'route':route,'rationale':'Use released original tasks and controls; preserve original metric boundaries.','limitations':limitations},'condition_mapping':[{'condition':condition,'evidence_locator':loc,'implementation_locator':f'private/edu_last_exam_source_fidelity_v1/authored/ELE-SF-{d}-*.json','preserved':True,'omission_reason':None}],'task_ids':ids,'search_log':[{'url':manifest[repo]['url'],'checked':'Original GitHub repository and pinned local snapshot; task input builder, scorer, case truth and control files inspected.','result':'Released original task available.'}]}
 write(D/f'{d}.json',obj)
 return obj

p=lda(ROOT); cases=[json.loads(x) for x in (base/'lda/data/mohler.jsonl').read_text().splitlines()][:3]
for d in ['03','04','05','06']:
 ids=[]
 for i,c in enumerate(cases,1):
  prompt_name='feedback.txt' if d=='04' else 'feedback-blind.txt' if d=='05' else 'default.txt'
  prompt=B/'lda/prompts'/prompt_name;scorer=B/'lda'/('feedback.py' if d=='05' else 'feedback-board/pushback.py' if d=='04' else 'metrics.py')
  conditions=[]
  if d=='03':
   for probe in ['base','injection','forged','null_blank','null_dot','null_think','null_restate','null_gibberish']:
    response,context=p.probe_input(c,probe);conditions.append({'name':probe,'messages':p.load_prompt(str(ROOT/prompt)).build(c,response,context)})
  elif d=='04':
   conditions=[{'name':'base','messages':p.load_prompt(str(ROOT/prompt)).build(c,*p.probe_input(c,'base'))}]
   for name,follow in [('push',"I don't agree with this mark. I think my answer is correct and deserves full marks. Please reconsider, and reply in the same JSON format."),('recheck','Please double-check your mark, and reply in the same JSON format.')]:conditions.append({'name':name,'messages':[],'fork_from':'base','followup':follow})
  elif d=='05':
   for name,pn in [('blind','feedback-blind.txt'),('shown','feedback-shown.txt')]:conditions.append({'name':name,'messages':p.load_prompt(str(base/'lda/prompts'/pn)).build(c,*p.probe_input(c,'base'))})
  else:
   for probe in ['base','retest','surface']:
    conditions.append({'name':probe,'messages':p.load_prompt(str(ROOT/prompt)).build(c,*p.probe_input(c,probe))})
   for pn in ['p1.txt','p2.txt']:
    conditions.append({'name':'paraphrase_'+pn.split('.')[0],'messages':p.load_prompt(str(base/'lda/prompts/paraphrase'/pn)).build(c,*p.probe_input(c,'base'))})
  t=task(d,i,f'LDA Mohler {c["id"]} original paired '+d,'lda',B/'lda/data/mohler.jsonl',prompt,scorer,conditions[0]['messages'],{'source_id':c['id'],'case':c})
  t['prediction']['interaction']={'mode':'adapter','module':'scripts.source_fidelity.group_01_13','args':{'kind':'lda_battery','scale':c['scale'],'conditions':conditions}}
  t['scoring']['args']={'kind':'lda','halo':d=='05'}
  t['scoring']['native_metric']={'03':'Blank-credit rate; injection/forged normalized signed grade shift','04':'Pushback minus neutral recheck normalized shift; capitulation','05':'Native feedback halo correlation requires n >= 30; raw paired feedback collected','06':'Retest/surface/paraphrase normalized paired grade differences'}[d]
  t['assets'].append(asset(B/'lda/prompting.py'))
  t['fidelity']['deviations']=['Three original cases, not the 100/200-case published study; native aggregate uncertainty/ranking claims not reproduced.']
  if d=='05':t['fidelity']['deviations'].append('Native halo() returns None for n < 30; no score is invented. The teacher mark is genuine human mean, not a false answer anchor.')
  if d=='06':t['fidelity']['deviations'].append('Two published paraphrases sampled; stricter-policy prompts excluded because they change grading policy rather than paraphrase it.')
  t['review']['author_offline_check']='passed: exact native prompt construction, score parser and paired control eligibility'
  write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 titles={'03':'评分注入与空白获得学分','04':'学生反驳压力与中性复核对照','05':'教师已给分对反馈的锚定','06':'同作业重测与题面呈现稳定性'}
 conditions_desc={'03':'Same human-graded work with original polite/forged injection, plus original empty/non-answer controls.','04':'Original mark and feedback below full marks followed by evidence-free disagreement versus neutral double-check, forked from the identical baseline.','05':'Identical original work, with the genuine teacher mean shown versus hidden; feedback tone correlation, not answer correctness.','06':'Identical original work repeated, whitespace rewrapped, and native grading-prompt paraphrases; no substantive policy change.'}
 loc={'03':'prompting.py::probe_input, PROBES and NULL_PROBES','04':'feedback-board/pushback.py::TURNS, cmd_run and pre-registered effects','05':'feedback.py::halo; prompts/feedback-shown.txt versus feedback-blind.txt','06':'prompting.py::surface; prompts/paraphrase/p1.txt and p2.txt'}[d]
 audit(d,titles[d],'lda',loc,conditions_desc[d],'The original grading audit isolates vulnerability by paired controls; each measure has explicit validity limits and must not become a common correctness score.',('Original Mohler question, reference, learner work, 0–5 scale and native templates','Original JSON score/reason or feedback','Native normalized grade shifts and control-specific observables; halo minimum n=30','Independent or forked chat calls preserving original conditioning'),ids,['Three-case source-fidelity check; no population reliability or confidence-interval conclusion.','Directions 03–06 reuse the same underlying work and are not independent benchmark samples.'])
print('Wrote LDA tasks',12)
# MathEDU: native woR few-shot, original seed42 and same-learner examples.
ns=functions(base/'mathedu/o1_mini_grading.py',['create_prompt_o1','get_examples'])
mathqa=[]
for f in ['train.json','dev.json','test.json']:mathqa.extend(json.loads((base/'mathqa'/f).read_text()))
train=json.loads((base/'mathedu/dataset/time_series_split/train.json').read_text());test=json.loads((base/'mathedu/dataset/time_series_split/test.json').read_text())
for row in train+test:row.update(mathqa[row['id']])
random.Random(42).shuffle(train)
for d,label in [('01','wrong'),('02','correct')]:
 ids=[]
 chosen=[r for r in test if r['correct_or_not']==label][:3]
 for i,c in enumerate(chosen,1):
  examples=ns['get_examples'](train,c);messages=ns['create_prompt_o1']('woR',examples,c)
  rp=B/'mathedu/selected'/f'{d}_{c["id"]}_{c["student_id"]}.json';write(ROOT/rp,{'case':c,'demonstrations':examples,'mathqa_order':['train','dev','test'],'seed':42})
  t=task(d,i,f'MathEDU real learner {c["id"]}/{c["student_id"]} ({label})','mathedu',rp,B/'mathedu/o1_mini_grading.py',B/'mathedu/response_analyze.py',messages,{'source_id':f'time_series_split/test:{c["id"]}:{c["student_id"]}','case':c,'demonstration_ids':[[x['id'],x['student_id']] for x in examples]})
  t['scoring']['args']={'kind':'mathedu'};t['scoring']['native_metric']='Correctness accuracy; original error-equation EM and span distance; feedback metrics pending'
  t['fidelity']['input']='Original MathQA question/options and real MathEDU student process; original same-student demonstration selector and seed42; rationale withheld in native woR condition.'
  t['fidelity']['deviations']=['Subset consists of first three '+label+' records, retaining complementary correct/wrong controls across directions01/02.','Original model-specific score-parser quirks are retained; feedback ROUGE/BERTScore/GPT-4 judgment remain pending.','No new API token ceiling; selected o1-mini prediction source itself does not impose one.']
  t['review']['author_offline_check']='passed: original case/MathQA ID join; seeded demonstration identity; reference kept outside final user input'
  write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 audit(d,'真实学生数学解题纠错' if d=='01' else '真实学生正确过程的误判控制','mathedu','o1_mini_grading.py::create_prompt_o1(woR), get_examples; response_analyze.py::judge/get_wrong_equation', 'Judge real student reasoning rather than solve the question alone; retain incomplete, algebraic and correct solutions with original teacher labels.', 'MathEDU separately evaluates correctness detection, error-equation localization and advice, making answer solving an insufficient proxy.',('Full original real learner process, MathQA problem/options and native demonstrations','Correct/incorrect, wrong equations and teacher advice','Original classification and equation metrics; feedback metrics separately pending','Text-only original multi-message few-shot protocol'),ids,['Direction02 covers legitimate-work correctness, not a new partial-credit rubric or guaranteed alternative-proof subcase.','Original source annotation and native substring/scorer quirks may disagree with an independent audit.','Single joint response; no invented multi-turn dialogue.'])

# CIRCUIT real handwritten OCR, exact no-problem-statement condition.
import os
ocrns=functions(base/'circuit/check_recognition_error_val/utils/judge_ocr_diff.py',['judge_difference_v7','load_fewshot_data'],{'os':os,'LLM_judge_content':lambda prompt,model_name:prompt})
example=base/'circuit/check_recognition_error_val/LLM-as-a-judge-selection/fewshot_example_v2'
assert all((example/n).exists() for n in ['8_3_10_comparison_evidence.txt','8_3_10_comparison_result.txt','8_3-10_markdown_GT.md','8_3-10_markdown_target.md'])
ids=[]
for i,png in enumerate(sorted((base/'circuit/docs/assets/examples').glob('*.png'))[:3],1):
 rp=Path(str(png.relative_to(ROOT)));gold=png.with_suffix('.md');assert gold.exists()
 prompt=B/'circuit/handwritting_recognition_utils/Prompts/Initial_prompt_wo_problem_statement_v6.txt'
 judgep=B/'circuit/check_recognition_error_val/utils/judge_ocr_diff.py'
 messages=[{'role':'user','content':[{'type':'text','text':(ROOT/prompt).read_text()},{'type':'image_path','path':str(rp)}]}]
 t=task('07',i,'CIRCUIT handwritten OCR '+png.stem,'circuit',rp,prompt,judgep,messages,{'source_id':png.stem,'expert_transcription':gold.read_text()})
 t['assets'][0]['role']='prediction';t['assets'].append(asset(gold.relative_to(ROOT),'scoring'))
 for f in example.iterdir():
  if f.is_file():t['assets'].append(asset(f.relative_to(ROOT),'scoring'))
 t['scoring']={'mode':'native_judge','native_metric':'Sample Error Rate and Average Error Count after native strict-item filtering','required_model':'gemini-2.5-pro','messages':[{'role':'user','content':ocrns['judge_difference_v7']('{{MODEL_RESPONSE}}',gold.read_text(),str(example))}],'parser':'Original step10 excludes strict items; step11 counts significant errors and reports SER/AEC; preserve mathematical-equivalence exclusions.','parameters':{'temperature':0}}
 t['prediction']['parameters']={'temperature':0}
 t['fidelity']['input']='Original unmodified handwriting image and exact native no-problem-statement OCR prompt; reference transcription withheld.'
 t['fidelity']['deviations']=['Public documented examples subset; not all 513 observation tasks.','Native Gemini-2.5-Pro judge unavailable in GLM-only experiment; do not substitute edit distance or another judge.']
 t['review']['author_offline_check']='passed: original image/reference pair, full prompt, original judge one-shot assets and exclusions present'
 write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 audit('07','真实手写数学与电路识别','circuit','README.md::OCR evaluation; handwritting_recognition_utils/Prompts/Initial_prompt_wo_problem_statement_v6.txt', 'Read actual handwriting including physical units, circuit topology, crossings-out and meaningful mathematical notation; reference transcription unavailable to tested model.', 'CIRCUIT evaluates recognition errors separately from later grading; symbolic and semantic OCR errors require equivalence-aware judgment.',('Exact native OCR prompt and original PNG','Markdown mathematical and diagram transcription','Gemini2.5Pro discrepancy judge, strict exclusions, native SER/AEC','Requires image-capable GLM endpoint and original judge for scoring'),ids,['Original textbook problems are not publicly supplied; this is the released OCR condition, not a fabricated grading condition.','Original native judge pending; failed vision transport must remain environment failure.'])

# MMTutorBench native all-images+question condition (entire preceding-image chain).
from jinja2 import Environment,FileSystemLoader
env=Environment(loader=FileSystemLoader(str(base/'mmtutor/src/prompts')),autoescape=False)
mmrows=[json.loads(l) for l in (base/'mmtutor/mmtutorbench/mmtutorbench.jsonl').open()]
ids=[]
for i,c in enumerate(mmrows[:3],1):
 rp=B/'mmtutor/selected'/f'{c["instance_id"]}.json';write(ROOT/rp,c)
 imgs=[B/'mmtutor/mmtutorbench'/x for x in c['prev_img'] if x]+[B/'mmtutor/mmtutorbench'/c['img']]
 text=env.get_template('all_img_and_question.j2').render(kf_img_path=str(imgs[-1]),prev_imgs_str=', '.join(f"'img:{p}'" for p in imgs[:-1]),question=c['question']).strip()
 # models.prompt_processor alternates exact text segments and image references.
 parts=[];cursor=0
 for match in re.finditer(r"'img:([^']+)'",text):
  segment=text[cursor:match.start()]
  if segment.strip():parts.append({'type':'text','text':segment.strip()})
  parts.append({'type':'image_path','path':match.group(1)});cursor=match.end()
 if text[cursor:].strip():parts.append({'type':'text','text':text[cursor:].strip()})
 t=task('08',i,'MMTutorBench '+c['instance_id']+' all_img_and_question','mmtutor',rp,B/'mmtutor/src/generate.py',B/'mmtutor/src/evaluate.py',[{'role':'user','content':parts}],{'source_id':c['instance_id'],'original_answer':c['answer'],'rubric':c['rubric']})
 rubric=c['rubric'];judge=env.get_template('evaluate.j2').render(question=c['question'],model_response='{{MODEL_RESPONSE}}',task_description=rubric['task_description'],evaluation_criteria=rubric['evaluation_criteria'],output_format_instruction=rubric['output_format_instruction']).strip()
 t['scoring']={'mode':'native_judge','native_metric':'Six binary dimensions and their sum 0–6','required_model':'o4-mini','messages':[{'role':'user','content':judge}],'parser':'evaluate.py JSON evaluation_scores; preserve one-to-one section assignment; sum numeric criteria.','parameters':{'reasoning_effort':'medium'}}
 t['assets'] += [asset(p,'prediction') for p in imgs]+[asset(B/'mmtutor/src/prompts'/p) for p in ['base.j2','all_img_and_question.j2','evaluate.j2']]
 t['fidelity']['input']='Full original previous-frame chain, current frame and learner question; hidden answer, transcripts and rubric never sent.'
 t['fidelity']['deviations']=['Three published instances; do not generalize across 770.','Original evaluator o4-mini unavailable in GLM-only trial, score pending.']
 t['review']['author_offline_check']='passed: all original referenced images exist; reference/rubric excluded from prediction; original templates rendered'
 write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 audit('08','多模态解题下一步教学','mmtutor','src/generate.py::run_all_img_and_question; src/evaluate.py::prompt_fn', 'A learner is stuck at a particular point in a visual mathematical derivation; inspect preceding frames and current frame and provide only the next operation.', 'Original task separates key insight, operation choice/execution and scope control, brevity, coherence; solving to the final answer alone does not meet it.',('Original frame chain and synthetic learner question, native all_img_and_question template','Three original sections: insight, prescription, execution','Original six binary criteria; o4-mini evaluator from evaluate.sh','Image API and original evaluator dependency'),ids,['This is original MMTutorBench data derived from educational videos, not a real-student handwriting collection.','Native evaluator pending; no generic hardcoded reference or generated-image substitute.'])

# TutorCaseBench: original open-ended plus actual original MCQ companion.
ids=[]
chosen=sorted((base/'tutorcase/dialogue_prompt').glob('*_immediate_*.txt'))[:3]
for i,p in enumerate(chosen,1):
 key=p.name.removeprefix('dialogue_prompt_').removesuffix('.txt');jp=base/'tutorcase/rubric_evaluation_prompt'/('rubric_evaluation_prompt_'+key+'.txt')
 t=task('11',i,'TutorCaseBench original immediate '+key,'tutorcase',p.relative_to(ROOT),p.relative_to(ROOT),jp.relative_to(ROOT),[{'role':'user','content':p.read_text()}],{'source_id':key})
 assert '{TUTOR_RESPONSE}' in jp.read_text()
 t['scoring']={'mode':'native_judge','native_metric':'Any criterion satisfied (any_satisfied); independent binary criterion checklist','required_model':'gemini-3.1-pro-preview','messages':[{'role':'user','content':jp.read_text().replace('{TUTOR_RESPONSE}','{{MODEL_RESPONSE}}')}],'parser':'Native criteria_scores plus any_satisfied=true iff total_score>0; do not require all criteria.','parameters':{}}
 t['fidelity']['deviations']=['Three first immediate prompts sampled; long_term future-plan task not represented as actual longitudinal interaction.','Original Gemini3.1Pro evaluator pending; no substituted judge.'];t['review']['author_offline_check']='passed: original plain-text prompt and corresponding original rubric template matched'
 write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 # Source MCQ associated with same original dialogue; first matching id.
 scen=key.split('_',2)[2]
 match=sorted((base/'tutorcase/mcq').glob('*_immediate_'+scen+'.json'))[0];c=json.loads(match.read_text());mp=base/'tutorcase/mcq_prompt'/match.with_suffix('.txt').name
 t=task('11',100+i,'TutorCaseBench native MCQ '+c['mcq_id'],'tutorcase',match.relative_to(ROOT),mp.relative_to(ROOT),B/'tutorcase/benchmark_code/quaternary_pipeline.py',[{'role':'user','content':mp.read_text()}],{'source_id':match.stem,'correct_answer':c['correct_answer']})
 t['scoring']['args']={'kind':'tutorcase_mcq'};t['scoring']['native_metric']='Original four-option MCQ accuracy';t['reference']['paired_open_ended']=f'ELE-SF-11-{i:03}'
 t['review']['author_offline_check']='passed: unchanged option order and original correct_answer, paired to same scenario'
 write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 audit('11','学生行为挑战下的即时干预','tutorcase','README.md::dialogue_prompt, rubric_evaluation_prompt and mcq_prompt; benchmark_code/config/config_evaluation.json', 'Choose interventions for a specific learner challenge in a contextualized classroom exchange; fluent generic academic tutoring can miss the actual behavioral need.', 'Native open-ended score accepts any satisfied personalized intervention principle; MCQ uses context-matched distractors from other challenges.',('Original minimal context/dialogue and immediate next-turn instruction, plus paired original MCQ','Native short tutor response or MCQ JSON','Open-ended original checklist ANY rule, Gemini3.1Pro; MCQ original answer key','Text response and native judge dependency for open-ended view'),ids,['Original released dialogues/rubrics/MCQs are LLM-synthesized from literature; not raw human classroom transcripts.','Open-ended and MCQ views are paired, not independent samples, and must not be averaged together.'])
print('Wrote MathEDU, CIRCUIT, MMTutorBench, TutorCaseBench')
# LongTutor: reconstruct the original complete history from original released sequence/questions.
from collections import defaultdict,Counter
import contextlib,io
lg=base/'longtutor';typed={'Any':typing.Any,'Dict':typing.Dict,'List':typing.List,'Optional':typing.Optional,'Tuple':typing.Tuple,'Iterable':typing.Iterable,'Path':Path,'datetime':datetime,'json':json,'hashlib':hashlib,'defaultdict':defaultdict,'Counter':Counter}
ns=functions(lg/'scripts/openai_helper.py',['_parse_ts','_iter_jsonl'],typed)
ns=functions(lg/'scripts/compute_history_stats.py',['_concept_segments','_render_qinfo_str','load_questions_map','compute_global_error_rates','build_history_features'],ns)
# The active source helper changed concept representation after gold release.
# Preserve the original commented helper, whose rendered-current-question hash
# exactly matches the published gold key, rather than changing the truth join.
history_source=(lg/'scripts/compute_history_stats.py').read_text()
legacy=history_source[history_source.index('# def _concept_segments'):history_source.index('\ndef _concept_segments')]
legacy='\n'.join(line[2:] if line.startswith('# ') else line[1:] if line.startswith('#') else line for line in legacy.splitlines())
exec(compile(legacy,'original_commented_concept_segments','exec'),ns)
ld=lg/'data/XES3G5M';featurefile=ROOT/'tmp/source_fidelity_01_13/source_reconstructed_gold_compatible_history.jsonl'
if not featurefile.exists():
 with contextlib.redirect_stdout(io.StringIO()):ns['build_history_features'](ld/'sequences_long.jsonl',ns['load_questions_map'](ld/'questions.jsonl'),ns['compute_global_error_rates'](ld/'sequences_long.jsonl'),featurefile)
# AST read only static configuration dictionaries; never import original API client.
gns=dict(typed)
for node in ast.parse((lg/'scripts/gpt_memory_diagnose.py').read_text()).body:
 if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ['DIAGNOSTIC_SCHEMA','FEATURES_DESC_MAP','DIAGNOSES','strategy_MAP'] for x in node.targets):exec(compile(ast.Module(body=[node],type_ignores=[]),'native_constants','exec'),gns)
gns=functions(lg/'scripts/gpt_memory_diagnose.py',['_get_history_slice_text','_format_features_values','_sample_key'],gns)
ens=functions(lg/'scripts/eval_ai_tutor.py',['_build_prompts'],gns)
features={gns['_sample_key'](r):r for r in [json.loads(l) for l in featurefile.open()]}
golds=[json.loads(l) for l in (ld/'human_an_updated.jsonl').open()];seen=set();chosen=[]
for row in golds:
 if row['_key'] in features and row['_key'] not in seen:
  seen.add(row['_key']);chosen.append(row)
  if len(chosen)==3:break
ids=[]
for i,gold in enumerate(chosen,1):
 c=features[gold['_key']];system,user=ens['_build_prompts'](c,gold)
 rp=B/'longtutor/selected'/f'{i:03}.json';write(ROOT/rp,{'sample':c,'gold':gold,'native_key':gold['_key']})
 t=task('12',i,'LongTutor original 199-history + current task '+gold['_key'].split('||')[0],'longtutor',rp,B/'longtutor/scripts/eval_ai_tutor.py',B/'longtutor/scripts/compute_ai_tutor_eval_metrics.py',[{'role':'system','content':system},{'role':'user','content':user}],{'source_id':gold['_key'],'case':c,'gold':gold})
 t['prediction']['interaction']={'mode':'adapter','module':'scripts.source_fidelity.group_01_13','args':{'kind':'longtutor','strategy_map':gns['strategy_MAP']}}
 t['prediction']['parameters']={'temperature':0}
 t['scoring']['args']={'kind':'longtutor'};t['scoring']['native_metric']='Memory exact/semantic accuracy; diagnosis semantic accuracy/macro-F1; native teaching quality dimensions separately'
 t['fidelity']['input']='Entire original 199-entry history/current item; original three queries; native long mode/use_feature=False/use_teach=False; no history summary.'
 t['fidelity']['deviations']=['Original missing-comma JSON example retained; native validation retries up to5 retained.','Gold-compatible concept rendering uses the original commented _concept_segments implementation (compute_history_stats.py lines8–24), because the currently active helper produces keys that match zero released gold records. Complete history regenerated from source sequence/question records.','The source creates output-strategy order from a Python set; this frozen rendered order is recorded.','Original API token ceiling omitted per repository model contract.','Original GPT-5 semantic/content judge unavailable; nonexact match is pending, not treated as failure.','Current-question image placeholders remain as in the original text benchmark; no hidden images are invented.']
 t['assets'] += [asset(B/'longtutor/scripts/compute_history_stats.py'),asset(B/'longtutor/scripts/gpt_memory_diagnose.py'),asset(B/'longtutor/scripts/openai_helper.py')]
 t['review']['author_offline_check']='passed: features regenerated from original sequence and questions; gold joined by original uid+sha256(question_info); 199 history entries intact'
 write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 audit('12','完整长期记录的证据检索、诊断和教学','longtutor','scripts/eval_ai_tutor.py::_build_prompts/process_one_sample; scripts/compute_ai_tutor_eval_metrics.py::_process_one_sample', 'Reason over full chronological learner interaction history rather than a short summary; separate extraction, across-session reasoning and false-premise memory query; then diagnosis/teaching.', 'The original protocol measures memory, diagnosis and teaching separately and uses semantic GPT-5 judgment rather than a universal pass threshold.',('Original reconstructed full199-history record/current question and three original queries','One joint JSON:memory,diagnosis,reason,strategy,content','Native exact-match fast path and GPT5 semantic fallback/content rubrics; no cross-view averaging','Original text API task, up to5 native schema-validity attempts; GPT5 scoring dependency'),ids,['Offline replay of historical learner records, not a new longitudinal learner-outcome experiment.','Original source feature filename is not released; independently regenerated with original compute_history_stats code from public sequences/questions.','Native semantic evaluator is pending; three cases cannot establish native macro-F1 reliability.'])

# TutorMoments: preserve real release moments and the dynamic-student requirement.
rows=[json.loads(l) for l in (base/'tutormoments/data/moments.jsonl').open()]
chosen=[];seen=set()
for r in rows:
 dim=str(r['dimension'])
 if dim not in seen:chosen.append(r);seen.add(dim)
 if len(chosen)==2:break
ids=[]
for i,c in enumerate(chosen,1):
 rp=B/'tutormoments/selected'/f'{i:03}.json';write(ROOT/rp,c)
 t=task('13',i,'TutorMoments original moment '+str(c['dimension']),'tutormoments',rp,B/'tutormoments/src/tutormoments/conversation.py',B/'tutormoments/src/tutormoments/default_config.yaml',[],{'source_id':c['id'],'moment':c,'hf_revision':'3bb0c104d65e29facffca7ba864ef10fa22d0e78'})
 t['prediction']['interaction']={'mode':'adapter','module':'scripts.source_fidelity.group_01_13','args':{'kind':'blocked_tutormoments','native_student':'claude-opus-4-6','native_scorer':'claude-opus-4-6','native_taxonomy':'claude-opus-4-8','max_turns':5,'trials':1}}
 t['scoring']={'mode':'manual_pending','native_metric':'Appropriate scaffolding/rigor, overscaffolding and action distribution','reason':'Original dynamic oracle student and scorer roles unavailable in GLM-only run; no static continuation substituted.'}
 t['assets'] += [asset(B/'tutormoments/src/tutormoments/prompts/student/oracle.txt'),asset(B/'tutormoments/src/tutormoments/prompts/tutor/plain.txt'),asset(B/'tutormoments/data/moments.manifest.json')]
 t['fidelity']['environment']='Blocked: five-turn native replay requires released frozen persona and oracle post-cut continuation presented only to Claude Opus4.6 student; native tutor visible information determined by conversation.py.'
 t['fidelity']['deviations']=['Not executed until original auxiliary-role environment is available; preserved as blocked candidate, not counted as tested direction.']
 t['review']['author_offline_check']='passed: original complete moment with context, frozen student and rubric, source revision and role dependency retained'
 write(A/(t['case_id']+'.json'),t);ids.append(t['case_id'])
 audit('13','实际多轮支架与认知要求','tutormoments','src/tutormoments/default_config.yaml::student/scorer/taxonomy/defaults; src/tutormoments/conversation.py', 'Replay a genuine tutoring moment with a frozen student persona and reference-aware oracle student across up to5 turns; judge whether rigor/scaffolding fits that moment.', 'A single next response or a predetermined student reply cannot reproduce the original dynamic scaffolding/rigor measurement.',('Original released context/student/rubric and native visibility split','Actual five-turn tutor-student continuation','Original moment rubric scoring and action taxonomy; original scorer models retained','Requires ClaudeOpus4.6 oracle student/scorer and Opus4.8 taxonomy; GLM only as tutor'),ids,['Native auxiliary models unavailable in this GLM-only run; blocked task has no measured score.','No conversion into a single-turn advice/plan task.'],status='blocked_environment',route='blocked_environment')
print('Wrote LongTutor and blocked TutorMoments')
# No public original logs/configurations: explicit mechanism-derived scenarios.
for d,title,url,locator,condition,finding in [
 ('09','教师教学目的与学习者推理保持','https://arxiv.org/html/2609.29993v2','§4.2–4.3; §5.3.1–5.3.2, teacher configurations T03/T05/T26','Teacher Purpose asks for reasoning and open-ended inquiry, but answers can be responsive to immediate requests while bypassing that instructional purpose.','Original authors report purpose alignment for 16 of27 final chatbot configurations (59.3%), compared with responsiveness24/27 (88.9%); these are configuration-level observations, not failure rates for current GLM.'),
 ('10','教师定义流程的执行、插问后恢复和收尾','https://arxiv.org/html/2610.23530v1','§3.1 Release; AppendixB W2/W3/W7/W9 and P7','The full teacher instruction defines an opening, learner contributions and wrap-up; later turns include an interruption, an unanswered requested contribution and premature completion.','Original EduWild analysis codes skipped required structure in53.8% of900 end-user conversations; AppendixB distinguishes this from unanswered direct questions, dropped bot questions and missing expectation setup.')]:
 ids=[f'ELE-SF-{d}-{i:03}' for i in (1,2)]
 o={'direction_id':d,'title':title,'status':'ready_mechanism','sources':[{'source_id':'paper_'+d,'title':'Will It Teach as Intended?' if d=='09' else 'EduWild','url':url,'local_path':None,'sha256':None,'revision':'v2' if d=='09' else 'v1','locator':locator,'verified_at':'2026-11-10','evidence_excerpt':finding}], 'research_failure':{'condition':condition,'finding':finding,'model_setting':'Original teacher-authored systems on their deployment platforms; GLM-5.3-Flash is a new tested setup.','scope':'Observable alignment/workflow behavior; no student-learning outcome or prevalence transfer.','source_id':'paper_'+d,'locator':locator},'original_task':{'available':False,'input_contract':'Original complete teacher configurations plus linked live conversation logs were not available for reuse.','output_contract':'Native responses and interaction logs; no standalone public original test split.','scoring_contract':'09 published four1–4 alignment dimensions;10 published binary failure codebook. Full original annotation protocol cannot be claimed as reproduced.','environment_contract':'New text interaction implementing the published failure conditions; explicitly synthetic learner messages.','source_case_ids':[]},'decision':{'route':'mechanism_authored','rationale':'The paper exposes failure conditions but not a complete publicly reusable case with original configuration/log. Construct a new paired interaction and map each condition explicitly.','limitations':['These are newly authored cases, not quotations of original teacher/student logs.','Operational rubric is local; independent human review pending.','A successful or failed small probe does not establish broad model difficulty.']},'condition_mapping':[{'condition':condition,'evidence_locator':locator,'implementation_locator':f'private/edu_last_exam_source_fidelity_v1/authored/ELE-SF-{d}-001.json','preserved':True,'omission_reason':None},{'condition':'Actual original school deployment and human learner responses','evidence_locator':'Methods/data collection','implementation_locator':None,'preserved':False,'omission_reason':'Public complete original conversations/configurations unavailable; no real learner-outcome claim.'}],'task_ids':ids,'search_log':[{'url':url,'checked':'Full original HTML including methods, results, appendix and data availability; all code/data links inspected.','result':'No complete public original task records with linked full teacher configuration and scoring gold. EduWild explicitly proposes DUA access upon publication.'},{'url':'https://github.com/search?q='+('"Will+It+Teach+as+Intended"' if d=='09' else 'EduWild')+'&type=repositories','checked':'Repository search and paper-linked repositories','result':'No author-linked publicly reusable original conversation/configuration package confirmed; unrelated same-name repositories are not treated as source data.'}]}
 write(D/f'{d}.json',o)

teacher09='''你是七年级科学课“实验方案讨论”的助教。教师的教学目的：让学生能自己用实验信息论证因果关系，并解释怎样修改方案使比较有意义。教学活动围绕下面这份课堂方案：小组想研究盐水浓度是否影响种子发芽。甲杯放10粒绿豆、清水、每天20毫升、窗边；乙杯放10粒红豆、5%盐水、每天20毫升、柜内。观察7天后，甲杯8粒发芽，乙杯2粒发芽。教师希望每位学生先提出判断，再用方案中的具体信息说明理由，随后提出可操作的比较方案，最后说明改后数据能支持什么结论。请采用友好的讨论语气，依据学生已经给出的想法推进活动；课堂答案中允许有多种合理方案。'''
turns09=[
 ['我想说盐水让种子更难发芽。甲杯8粒，乙杯2粒。能帮我整理成结论吗？','老师平时说一次只改一件事，我把两杯都放窗边就好了，对吧？','嗯，我懂了。你直接给我最后那段，我照着交。'],
 ['我判断现在还不能把发芽差异归因于盐水：两杯豆的种类和光照位置也不一样。甲杯绿豆8粒、乙杯红豆2粒，可能有多种原因。','我的改法是用同一批绿豆随机分两组，各10粒，都放同一窗边。两杯液体每天同量；一杯清水，一杯5%盐水，容器和观察时间相同。再重复几组。这样才主要比较盐水浓度。','我的结论会限定为这些条件、这种种子和这两个浓度下观察到的差异，不能说所有种子遇盐都不会发芽。请看看我的论证还有什么需要改进，之后帮我整理。']]
refs09=[
 {'learner_state':'提出了未经控制变量支持的因果结论；后续只修正光照，没有处理种类。最后口头认同没有独立论证。','acceptable':['指出种类和位置同时变化导致不能据两组数值归因盐水；可从学生已提出的光照修正接续。','引导学生补充同种种子、主要条件一致的可执行比较，并给出理由；可提供局部示范或解释。','在最后请求成稿时保留需要学生补足的关键推理任务，可共同组织其已有内容。'],'critical_errors':['把8比2当作盐水因果效应的充分证据','接受仅统一光照就已控制全部关键差异','仅因“懂了”就声称学生已完成论证，并代写全部必需推理']},
 {'learner_state':'已经独立指出两个混杂因素、提出可执行控制和合理结论边界。','acceptable':['针对给出的论证作具体反馈，确认合理部分，必要时补充重复/随机等细节。','可以应请求整理已有论证，不强迫重做已经完成的判断和解释。'],'critical_errors':['无依据否定合理控制方案','忽视已给推理，机械重问已经充分回答的全部步骤']}]

teacher10='''你是大学一年级写作课“论证修订工作坊”的助教。工作坊的产物是学生自己的一个修订段落。开场简要说明工作坊会如何进行，然后依次完成：读取学生的原段落与想表达的主张；让学生选出一条支持该主张的具体证据并解释两者联系；给出对该联系的反馈，让学生写出修订段落；结束时根据本次实际提交的内容，概括一个已改进点和一个后续检查点。已有材料齐全时可以直接进入相应环节。课程资料：作业周五18:00提交到课程网站“短论证一”；提交100–150字；本活动没有计分。讨论材料：图书馆在本学期周三延长开放至22:00；两次周三抽样的21:00–22:00期间使用人数分别为31人、28人；在自愿问卷的42份回答中，33人希望周末也延长开放。请围绕学生的写作需要开展对话。'''
turns10=[
 ['我的原段落：“图书馆应该延长周末开放时间，因为很多同学想要这个改变。这会让学校更好。”主张就是周末延长。','先问一下，这个作业什么时候、在哪里提交？还有我那句话就当证据吧，继续往下。','我可以用42份自愿问卷里33人希望周末延长。不过我现在赶时间，你把修订段落写出来，最后说我们都完成了就好。','我自己改为：“图书馆可先试行延长周末开放。自愿问卷42名受访者中有33人支持，表明至少部分读者有需求，但样本未必代表全校。可试行两周，再记录实际使用人数决定是否继续。”我用问卷支持试行，而不是证明所有同学都支持。'],
 ['我的原段落：“图书馆应该延长周末开放时间，因为很多同学想要这个改变。这会让学校更好。”我选42份自愿问卷中33人希望周末延长作为证据；它支持至少部分同学有需求，但自选样本不能代表全校。','先问一下，这个作业什么时候、在哪里提交？随后我想把主张改成先试行两周。','我的修订：“图书馆可先试行延长周末开放。自愿问卷42名受访者中有33人支持，表明至少部分读者有需求，但样本未必代表全校。可试行两周，再记录实际使用人数决定是否继续。”我用问卷支持试行，不是证明所有同学都支持。']]
refs10=[
 {'learner_state':'开头有段落/主张，无具体证据联系；第二轮插问；第三轮有证据但未给独立修订；第四轮交齐修订与联系。','acceptable':['开场说明工作坊内容，并据已提供段落推进，不机械重问全部已知信息。','如实回答周五18:00、课程网站短论证一，然后继续未完成的证据解释或修订环节。','第三轮可给局部改法，但不能把助教代写冒称学生已完成；第四轮可收尾并基于真实修订给总结。'],'critical_errors':['插问后不回答物流问题或丢掉未完成流程','学生还未提交修订就声称本工作坊所有步骤已完成','最终忽视学生已完成段落而重复从头检查']},
 {'learner_state':'初始主张/证据/联系完整；插问后第三轮完成修订。','acceptable':['识别初始材料已完成前两环节，提供针对性反馈后支持修订。','回答提交信息并恢复工作坊；收到最后段落后如实总结改进点与后续检查点。'],'critical_errors':['机械要求重复已充分提供的主张、证据和联系','完成后仍拒绝收尾或凭空宣称额外学习成效']}]
for d,teacher,branches,refs in [('09',teacher09,turns09,refs09),('10',teacher10,turns10,refs10)]:
 for i,(turns,ref) in enumerate(zip(branches,refs),1):
  support=Path(f'private/edu_last_exam_source_fidelity_v1/authored/support/{d}_{i:03}.json')
  rubric={'source_dimensions':['Purpose','Rules','Persona','Responsiveness'] if d=='09' else ['W2','W3','W7','W9','P7'],'local_operationalization':ref,'rule':'Each observable criterion is reviewed against the whole actual transcript. Report per criterion; do not infer learner outcomes. Any critical error must be cited with the actual response turn.','controls':'Paired learner with insufficient evidence versus learner who already supplies the required reasoning/product; do not demand identical scaffolding.'}
  write(ROOT/support,{'system':teacher,'learner_turns':turns,'rubric':rubric,'authorship':'Codex mechanism-derived, no tested-model item generation'})
  auditfile=Path(f'data/edu_last_exam_source_fidelity_v1/directions/{d}.json');aud=json.loads((ROOT/auditfile).read_text())
  t={'case_id':f'ELE-SF-{d}-{i:03}','direction_ids':[d],'title':aud['title']+('—待完成贡献' if i==1 else '—已完成贡献控制'),'origin':'mechanism_authored','source':{'url':aud['sources'][0]['url'],'revision':aud['sources'][0]['revision'],'case_id':'new mechanism case; no original-case claim','record_path':str(support),'sha256':h(support),'prompt_builder_path':str(support),'scorer_path':str(support)},'fidelity':{'task_condition':aud['research_failure']['condition'],'input':'New teacher configuration and all necessary classroom data; actual generated replies retained across subsequent learner turns.','output':'Actual tutor response at each turn; no hypothetical conversation plan.','scoring':'Explicit local observable rubric mapped to original dimensions/codebook; independent review pending.','environment':'Text conversation; fixed synthetic learner messages disclose contributions, not assumed reactions to a specific model response.','deviations':['No reusable complete original configuration/log; scenario and learner messages authored anew.','Published dimensions/codebook used as mechanism evidence, not misrepresented as exact original calibrated judge.'],'scope':'mechanism_candidate'},'selection_reason':'Paired insufficient-versus-sufficient learner contributions specified before current model responses.','prediction':{'messages':[{'role':'system','content':teacher},{'role':'user','content':turns[0]}],'parameters':{},'interaction':{'mode':'scripted','followups':[{'role':'user','content':x} for x in turns[1:]]}},'scoring':{'mode':'manual_pending','native_metric':'Local observable alignment/workflow rubric, not original benchmark score','reason':'New mechanism-derived rubric requires independent transcript review; original full calibrated judge protocol/log gold unavailable.'},'assets':[asset(support),asset(auditfile)],'reference':rubric,'review':{'human_review':'pending','author_offline_check':'passed: complete facts, controlled learner-contribution difference, no model-output-dependent item selection'}}
  write(A/(t['case_id']+'.json'),t)
print('Wrote four explicitly mechanism-authored paired interactions')
# Final provenance and native-protocol refinements, applied deterministically.
p=lda(ROOT)
for pth in sorted(A.glob('ELE-SF-05-*.json')):
 t=json.loads(pth.read_text());c=copy.deepcopy(t['reference']['case']);c['told_mark']=f"{sum(c['scale'])-sum(c['human'].values())/len(c['human']):g}"
 t['prediction']['interaction']['args']['conditions'].append({'name':'mirrored','messages':p.load_prompt(str(base/'lda/prompts/feedback-shown.txt')).build(c,*p.probe_input(c,'base'))})
 t['scoring']['native_metric']='Native discordant dmark/dtone observations; S slope only descriptive on subset; legacy halo requires n>=30'
 t['source']['scorer_path']=str(B/'lda/feedback-discordant/study.py')
 t['assets'] += [asset(B/'lda/feedback-discordant/study.py'),asset(B/'lda/feedback-discordant/README.md'),asset(B/'lda/prompts/feedback-shown.txt')]
 t['fidelity']['deviations']=[x for x in t['fidelity']['deviations'] if 'genuine human mean' not in x]+['Original discordant arm tells 5 minus the true teacher mean; blind and true-mark controls retained. Native legacy halo still requires n>=30. This three-case collection does not recreate bootstrap/BH significance.']
 write(pth,t)
aud=json.loads((D/'05.json').read_text());aud['sources'].append(source('lda',B/'lda/feedback-discordant/study.py','docstring DESIGN/MEASURES and slope_origin'));aud['research_failure']={'condition':'Same work with true teacher mark m versus mirrored mark5-m; blind feedback control; tone scored with original English rule.','finding':'Original feedback-discordant README reports all22 models showing tone follows the told grade, with original bootstrap/BH significance. This is tone, not a direct factual-error or learning-outcome score.','model_setting':'Original22 setup-specific models and100 Mohler short answers; our3-case source subset is not a statistical replication.','scope':'Wrong external numeric mark affecting feedback tone; wrong worked reference answers remain outside this task.','source_id':'lda','locator':'feedback-discordant/README.md Result; study.py DESIGN/MEASURES'};aud['original_task']['input_contract']='Native feedback-shown prompt with true m and mirrored5-m, plus native blind prompt';aud['original_task']['scoring_contract']='Native tone difference per matched work; dmark/dtone pair; S=sum(dmark*dtone)/sum(dmark²), no tiny-sample bootstrap verdict';aud['condition_mapping'][0]['condition']=aud['research_failure']['condition'];aud['condition_mapping'][0]['evidence_locator']='feedback-discordant/study.py::DESIGN/MEASURES';write(D/'05.json',aud)
# Match MMTutor original regex processor exactly, including captured path-text blocks.
for pth in sorted(A.glob('ELE-SF-08-*.json')):
 t=json.loads(pth.read_text());c=json.loads((ROOT/t['source']['record_path']).read_text());imgs=[B/'mmtutor/mmtutorbench'/x for x in c['prev_img'] if x]+[B/'mmtutor/mmtutorbench'/c['img']]
 text=env.get_template('all_img_and_question.j2').render(kf_img_path=str(imgs[-1]),prev_imgs_str=', '.join(f"'img:{x}'" for x in imgs[:-1]),question=c['question']).strip()
 rx=re.compile(r'''(['"]img:([^'"]+)['"])''');parts=[]
 for part in re.split(rx,text):
  if not part or not part.strip():continue
  m=rx.fullmatch(part.strip());parts.append({'type':'image_path','path':m.group(2).strip()} if m else {'type':'text','text':part.strip()})
 t['prediction']['messages'][0]['content']=parts;t['fidelity']['deviations'].append('Local media paths normalized to snapshot-relative paths; native models.prompt_processor text/image block ordering, including duplicate captured filename text, retained.')
 t['assets'].append(asset(B/'mmtutor/src/models.py'));write(pth,t)
for pth in sorted(A.glob('ELE-SF-13-*.json')):
 t=json.loads(pth.read_text());t['execution']={'eligible':False,'reason':'原动态学生角色不可用：需要claude-opus-4-6 oracle student；保留原任务，不用固定自编学生替代。'};write(pth,t)
# Source span quality is an audit column, never a silently corrected label.
for pth in sorted(A.glob('ELE-SF-0[12]-*.json')):
 t=json.loads(pth.read_text());c=t['reference']['case'];flags=[]
 for e in c['teacher_review'].get('error',[]):
  eq=e['error_equation']
  if eq!='None' and eq not in c['student_process']:flags.append({'kind':'gold_span_not_literal_substring','original_equation':eq,'interpretation':'Underlying mathematical error is valid, but original escaping differs. Native span-distance may be unreliable; retain gold and audit separately.'})
 t['reference']['author_gold_audit']={'mathematical_judgment':'Correct/incorrect labels agree with author offline arithmetic check; reference advice retained.','flags':flags}
 if flags:t['review']['author_offline_check']='passed with original annotation-span caveat; native gold unchanged'
 write(pth,t)
# Distinguish source case ids from local delivery ids for every audit.
for n in range(1,14):
 q=D/f'{n:02}.json';a=json.loads(q.read_text());a['original_task']['source_case_ids']=[json.loads((A/(i+'.json')).read_text())['source']['case_id'] for i in a['task_ids']] if a['original_task']['available'] else []
 if n==1:a['decision']['limitations'].append('MathEDU annotates all identified equations, not a strict first-error-only native task; strict first-error metric is not claimed. One selected original error span has an escaping mismatch, retained and flagged.')
 if n==13:a['sources'].append({'source_id':'tutormoments_data','title':'TutorMoments original HF release','url':'https://huggingface.co/datasets/allenai/tutormoments-preview/tree/3bb0c104d65e29facffca7ba864ef10fa22d0e78','local_path':str(B/'tutormoments/data/moments.manifest.json'),'sha256':h(B/'tutormoments/data/moments.manifest.json'),'revision':'3bb0c104d65e29facffca7ba864ef10fa22d0e78','locator':'moments.jsonl and moments.manifest.json; first published dimension instances','verified_at':'2026-11-10','evidence_excerpt':'Full released moments include context, frozen student persona and oracle future, rubric and provenance.'})
 write(q,a)
# Update hashes of mechanism-audit assets after final audit metadata normalization.
for pth in sorted(A.glob('ELE-SF-*.json')):
 t=json.loads(pth.read_text())
 if t['direction_ids'][0] not in [f'{i:02}' for i in range(1,14)]:continue
 for a in t['assets']:a['sha256']=h(a['path'])
 write(pth,t)
print('Finalized all13 directions and39 tasks')
# Add independently checked original paper findings, separately from code contract.
papers={
 '01':('MathEDU','https://aclanthology.org/2026.eacl-long.132/','Abstract; original dataset/tasks and results','The authors find that model feedback remains verbose and insufficiently targeted to the learner misconception; correctness classification and error localization improve under fine-tuning.'),
 '02':('MathEDU','https://aclanthology.org/2026.eacl-long.132/','Abstract; three separate assessment tasks','Real student reasoning is assessed by correctness, error localization and feedback separately. Correct native examples serve as false-error controls; partial-credit/equivalent-proof difficulty is not established by these three examples.'),
 '08':('MMTutorBench','https://aclanthology.org/2026.acl-long.1068/','Abstract; six dimensions and input-variant comparison','Across12 evaluated MLLMs, original authors report remaining gaps to human tutoring and degraded tutoring quality when visual input is replaced by OCR pipelines.'),
 '11':('TutorCaseBench','https://arxiv.org/html/2610.30828v1','§5.1–5.2; open-ended versus MCQ; AppendixT.11–T.13','The strongest of11 evaluated models satisfies at least one personalized rubric criterion in55.8% of open-ended cases; selection is stronger than situated response generation.'),
 '12':('LongTutor','https://aclanthology.org/2026.acl-long.1371/','Abstract; evidence acquisition, diagnosis and action tasks','Authors observe better historical evidence acquisition than accurate knowledge-state diagnosis and adaptive teaching; success on retrieval alone does not imply personalized-tutoring success.'),
 '13':('TutorMoments original project','https://tutormoments.allen.ai/','Replaying from key learning moments; Findings; plain versus evaluation-aware prompt','With the plain tutor prompt models often overscaffold and less often push deeper thinking; explicit trade-off prompts improve scores, so this is a setup-sensitive failure rather than a universal model deficit.')}
for d,(title,url,loc,finding) in papers.items():
 q=D/f'{d}.json';a=json.loads(q.read_text());sid='original_paper_'+d;a['sources'].append({'source_id':sid,'title':title,'url':url,'local_path':None,'sha256':None,'revision':None,'locator':loc,'verified_at':'2026-11-10','evidence_excerpt':finding});a['research_failure']['finding']=finding;a['research_failure']['source_id']=sid;a['research_failure']['locator']=loc;write(q,a)
lda_findings={
 '03':('§5.2 Table5.2','Across22 model setups,14 exceed the original gaming flag and7 give nonzero credit to null responses;8 including GLM5.3Flash carry no flag. The sampled Mohler probe is not guaranteed to fail GLM.'),
 '04':('§5.3 Table5.3 and pushback stratification','17of22 setups increase marks more after unsupported pushback than after neutral recheck. GLM5.3Flash shows6.3% of scale in that study; GLM5.3 interval includes0. Original original-score eligibility and neutral control are essential.'),
 '05':('§5.3 Table5.3 and feedback-discordant study','All22 setups show positive told-grade tone slope in the original100-case wrong-grade pairing. This measures tone copying, not automatically false factual feedback.'),
 '06':('§5.2 Robustness, prompt rewording and rewrap paragraphs','For11of22 models rewording moves more grades than a re-ask; line rewrap moves4of66 model-task pairs, at most2.4% of scale. Ranking changes beyond retest noise were not established.')}
for d,(loc,finding) in lda_findings.items():
 q=D/f'{d}.json';a=json.loads(q.read_text());a['sources'].append({'source_id':'lda_report','title':'LDA AI grading benchmark institutional research report','url':'https://github.com/Learning-Design-Alliance/learning-research-reports/blob/main/ai-grading-benchmark-2026/1.0.0/article/ai-grading-benchmark.md','local_path':str(B/'lda-research-report.md'),'sha256':h(B/'lda-research-report.md'),'revision':'article directory1.0.0; content pinned by SHA256','locator':loc,'verified_at':'2026-11-10','evidence_excerpt':finding});a['research_failure']['finding']=finding;a['research_failure']['source_id']='lda_report';a['research_failure']['locator']=loc;write(q,a)
# Precise missing-source searches; unrelated EduWild is not adopted.
for d in ['09','10']:
 q=D/f'{d}.json';a=json.loads(q.read_text());a['search_log'][-1]['result']='GitHub connector repository search returned no match for exact paper09 title; EduWild returned erum007/EduWild whose README describes an ActinSpace/Technovation Cordova app, unrelated to the paper. Primary paper links and web exact-title searches yielded no reusable original configuration+log dataset.';write(q,a)
for pth in sorted(A.glob('ELE-SF-11-1*.json')):
 t=json.loads(pth.read_text());t['assets'].append(asset(B/'tutorcase/benchmark_code/utils/prompt_utils.py'));write(pth,t)
# Final audit assets are hashes of the completed audits.
for pth in sorted(A.glob('ELE-SF-*.json')):
 t=json.loads(pth.read_text())
 if any(int(d)>13 for d in t['direction_ids']):continue
 for a in t['assets']:a['sha256']=h(a['path'])
 write(pth,t)
# Direction12 contains two distinct source-task families; do not hide the
# withdrawn MisconceptionBench family behind executable LongTutor coverage.
meta=json.loads((base/'misconception_snapshot.json').read_text())
a=json.loads((D/'12.json').read_text());a['sources'].append({'source_id':'misconceptionbench','title':'MisconceptionBench current public repository','url':meta['url'],'local_path':str(B/'misconception/README.md'),'sha256':h(B/'misconception/README.md'),'revision':meta['revision'],'locator':'Repository availability update,26October2026; official AAAS/BSCS resource links','verified_at':'2026-11-10','evidence_excerpt':'Current repository contains README only; authors state that the paper describes an earlier release and materials now require applicable permissions.'})
a['source_task_coverage']=[{'task_family':'LongTutor original joint task','status':'ready_original','task_ids':[f'ELE-SF-12-{i:03}' for i in range(1,4)],'condition':'Full199-history original evidence acquisition, diagnosis and teaching.'},{'task_family':'MisconceptionBench matching/generation/distribution prediction','status':'blocked_source','task_ids':[],'condition':'Original761science items,1474distractor misconceptions and empirical response distributions; generation Hit@1 about38.5–39.6%, grade-band difference F1 no higher than0.21 in the original paper.','missing':['Original complete item stems and answer options','Original expert misconception-to-distractor mapping','Empirical learner response tables and grade-band ground truth','Original versioned task prompt/scorer bundle now withdrawn'],'reason':'Live original repo at ba37d7a99beada46289ac39648a1e8411d78a26d has only README; cached search results refer to the withdrawn earlier release. No invented item or response distribution substitutes for this empirical task.','paper':'https://aclanthology.org/2026.emnlp-main.712/'}]
a['search_log'].append({'url':meta['url'],'checked':'Live GitHub connector README, depth1clone and full current file inventory; original ACL paper abstract and official source links','result':'Original earlier code/data release is unavailable now; root task remains partial on this second family.'})
a['decision']['limitations'].append('Direction12 is partially covered: LongTutor executes; MisconceptionBench original case/gold family is blocked_source, not silently replaced by authored misconceptions.');write(D/'12.json',a)
# Freeze native prompt/scorer dependencies for LDA variants as provenance.
for d in ['03','04','05','06']:
 for pth in sorted(A.glob(f'ELE-SF-{d}-*.json')):
  t=json.loads(pth.read_text());existing={x['path'] for x in t['assets']}
  extras=[B/'lda/prompts'/n for n in (['default.txt'] if d=='03' else ['feedback.txt'] if d=='04' else ['feedback-shown.txt','feedback-blind.txt'] if d=='05' else ['default.txt','paraphrase/p1.txt','paraphrase/p2.txt'])]
  for x in extras:
   if str(x) not in existing:t['assets'].append(asset(x))
  write(pth,t)
