"""Deterministic source-faithful subset selection; never consumes model responses."""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'sources/datasets/edu_last_exam_source_fidelity_v1/group_14_26'
OLD = Path('/home/likefallwind/code/edubenchmark')
OUT = ROOT / 'private/edu_last_exam_source_fidelity_v1/authored'
AUDIT = ROOT / 'data/edu_last_exam_source_fidelity_v1/directions'
MODULE = 'scripts.source_fidelity.group_14_26'

def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(Path(path).relative_to(ROOT))
def rows(path):
    with Path(path).open() as f:
        return [json.loads(x) for x in f if x.strip()]

def trusted_functions(path, names):
    tree = ast.parse(Path(path).read_text())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.Assign, ast.AnnAssign)) and (getattr(n, 'name', '') in names or (isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)))]
    ns = {'re':__import__('re'), 'unicodedata':__import__('unicodedata'), 'Any':object}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),ns)
    return ns

def source(sid,title,url,path,locator,revision=None,excerpt=None):
    return dict(source_id=sid,title=title,url=url,local_path=rel(path) if path else None,sha256=sha(path) if path else None,revision=revision,locator=locator,verified_at='2026-11-10',evidence_excerpt=excerpt)

def audit(n,title,srcs,condition,finding,original,ids,limitations=(),status=None,route=None,search=None):
    dump(AUDIT/f'{n:02}.json',dict(direction_id=f'{n:02}',title=title,status=status or ('ready_original' if original else 'ready_mechanism'),sources=srcs,
        research_failure=dict(condition=condition,finding=finding,model_setting='见原来源定位；不外推为 GLM-5.3 Flash 已失败',scope='原研究或历史实验的观测边界；本次为预先选定小样本',source_id=srcs[0]['source_id'],locator=srcs[0]['locator']),
        original_task=dict(available=original,input_contract='见每个 task 的 prediction.messages 与 source 原记录；金标留在 reference',output_contract='保留原任务输出，不追加统一教学格式',scoring_contract='见 task.scoring；原生统计不换算统一正确率',environment_contract='见 task.fidelity.environment；未公开运行工具明确列为缺口',source_case_ids=ids),
        decision=dict(route=route or ('original_task' if original else 'historical_protocol_replay'),rationale=condition,limitations=list(limitations)),
        condition_mapping=[dict(condition=condition,evidence_locator=srcs[0]['locator'],implementation_locator='; '.join(ids) if ids else 'no runnable task',preserved=bool(ids),omission_reason=None if ids else '; '.join(limitations))],task_ids=ids,
        search_log=search or [dict(url=s['url'],checked=s['locator'],result='直接读取原文/原源码并记录快照哈希') for s in srcs]))

def task(n,i,title,record,path,url,messages,metric,args,origin='original_task',revision=None,deviations=(),interaction=None,parameters=None):
    ident=f'ELE-SF-{n:02}-{i:03}'
    t=dict(case_id=ident,direction_ids=[f'{n:02}'],title=title,origin=origin,
        source=dict(url=url,revision=revision,case_id=record.get('id',record.get('item_id',str(i))),record_path=rel(path),sha256=sha(path),prompt_builder_path=__file__.replace(str(ROOT)+'/', ''),scorer_path='scripts/source_fidelity/group_14_26.py'),
        fidelity=dict(task_condition=title,input='原记录中的完整模型可见信息；评分真值不进入 prompt',output=metric,scoring=metric,environment='原文本任务，无额外工具',deviations=list(deviations),scope='native_subset' if origin=='original_task' else 'historical_protocol_subset'),
        selection_reason='固定来源顺序中首个满足预先指定场景条件的实例；选题未读取本轮模型回答',
        prediction=dict(messages=messages,parameters=parameters or {},interaction=interaction or {'mode':'single_turn'}),
        scoring=dict(mode='native_adapter',native_metric=metric,module=MODULE,args=args),
        assets=[dict(path=rel(path),sha256=sha(path),role='provenance')],reference=record,
        review=dict(human_review='pending',author_offline_check='pending'))
    dump(OUT/f'{ident}.json',t)
    return ident

def build_text_tasks():
    # 22: Original human essay-rating task. ASAP provides no canonical LLM prompt.
    d=BASE/'asap_2'; source_texts=json.loads((d/'source_texts.json').read_text()); rubric=(d/'rubric.txt').read_text().strip()
    chosen=[r for r in rows(OLD/'sources/datasets/asap_2/data/essays.jsonl') if r['split']=='test' and r['prompt_name']=='Driverless cars'][:3]
    selected=d/'selected_original_essays.json';dump(selected,chosen)
    constants=trusted_functions(d/'asap_2.py',{'SCORING_PROMPT','SOURCE_BLOCK'})
    ids=[]
    for i,r in enumerate(chosen,1):
        prompt=constants['SCORING_PROMPT'].format(assignment=r['assignment'].strip(),source_block=constants['SOURCE_BLOCK'].format(sources='\n\n---\n\n'.join(source_texts[r['prompt_name']])),rubric=rubric,essay=r['full_text'].strip(),min_score=1,max_score=6)
        ids.append(task(22,i,'ASAP 2.0 原作文整体评分（完整材料、原 1–6 rubric）',r,selected,'https://github.com/scrosseye/ASAP_2.0',[dict(role='user',content=prompt)],'QWK rating pairs (1–6); exact agreement is diagnostic',{'kind':'asap'},deviations=['数据集只提供人工任务、文章与 rubric，没有官方 LLM prompt；使用明确署名本地 rubric wrapper，非原论文 prompt。','仅三篇，不是 7,421 篇 QWK 复现；与此前省略材料/rubric 的 colleague 协议不直接比较。']))
    audit(22,'作文整体评分',[source('ASAP2','ASAP 2.0','https://github.com/scrosseye/ASAP_2.0',d/'data_manifest.json','official holistic rubric; test split; Driverless cars')], '完整作文需按整体质量而非局部语言漂亮程度评分，保留原文章、写作任务、人工总分与量尺。','原始语料支持人工评分任务；本地历史模型 QWK 受省略 rubric/材料等协议差异影响，不据此断言新版失败。',True,ids,['无官方 LLM prompt；三例仅展示误差，不能稳定估计人群 QWK。'])
    # 23: Original MathTutorBench one-shot Socratic question generation.
    import pyarrow.parquet as pq
    import yaml
    d=BASE/'mathtutorbench'; chosen=pq.read_table(OLD/'sources/datasets/gsm8k/socratic/test-00000-of-00001.parquet').slice(0,3).to_pylist();selected=d/'selected_socratic_test.json';dump(selected,chosen)
    c=yaml.safe_load((d/'socratic_questioning.yaml').read_text());ids=[]
    for i,r in enumerate(chosen,1):
        prompt=c['system_prompt'].replace('{{ shots }}',c['few_shot_samples']).replace('{{question}}',r['question'])
        ids.append(task(23,i,'MathTutorBench 原 Socratic question generation',r,selected,'https://github.com/eth-lre/mathtutorbench',[dict(role='system',content=prompt)],'mean best-match sentence SacreBLEU (0–1)',{'kind':'socratic'},revision='54b62137c7170a32f596876db48b088870fc5fb4',parameters={'stop':c['stop']},deviations=['保留原 system-only 调用及换行 stop；本任务不测实际多轮教学效果。']))
    audit(23,'苏格拉底提问',[source('MTB','MathTutorBench','https://aclanthology.org/2025.emnlp-main.11/',d/'socratic_questioning.py','configs/socratic_questioning.yaml; tasks/socratic_questioning.py::compute_metrics','54b62137c7170a32f596876db48b088870fc5fb4')], '从完整数学问题生成分步问题，原提示只允许一行问题列表，参考来自 GSM8K Socratic。','该视图原评分是最佳句级 BLEU；低分只代表与参考问句词面相似度低，不是教学失败率。',True,ids,['单轮原任务，不冒充学生参与的持续苏格拉底辅导；BLEU 不覆盖提问教育质量。'])
    # 24: Original dataset is a graph; replay actual historical inference protocol.
    d=BASE/'mooccube';allrows=rows(d/'items_v1.jsonl'); chosen=[next(r for r in allrows if r['task']=='mcq' and r['n_reverse_distractors']>0)]+[r for r in allrows if r['task']=='order'][:2];selected=d/'selected_historical_tasks.json';dump(selected,chosen)
    fn=trusted_functions(d/'mooccube_prereq.py',{'_option_block','_mcq_prompt','_order_prompt'})
    ids=[]
    for i,r in enumerate(chosen,1):
        ids.append(task(24,i,'MOOCCube 先修推断：隐藏真值边、保留同领域反向干扰',r,selected,'https://github.com/thukg/MOOCCube',[dict(role='user',content=fn['_mcq_prompt' if r['task']=='mcq' else '_order_prompt'](r))],'MCQ accuracy / any valid topological order / satisfied constraints',{'kind':'mooccube'},origin='mechanism_authored',deviations=['MOOCCube 原材料是专家先修图，不含这些问句；原样复用本地历史固定协议和题目。','金标依赖该知识图谱，未宣称是唯一可能的课程先修安排。']))
    audit(24,'先修关系与学习顺序推断',[source('MOOC','MOOCCube expert prerequisites','https://aclanthology.org/2020.acl-main.285/',d/'prerequisite-dependency.json','expert prerequisite edges; local builder creates MCQ/order probes'),source('MOOC-local','Historical inference adapter','https://github.com/thukg/MOOCCube',d/'mooccube_prereq.py','_mcq_prompt; _order_prompt; score')], '不给模型依赖边；从概念名/定义辨别前置与后继，或给出满足隐藏专家边的任意拓扑序。','原数据是图而非官方 LLM benchmark；保留此前真实实验协议，避免旧全覆盖题把依赖边直接给出造成任务降格。',False,ids,['属于知识结构推断，不测针对某学生状态的长期学习路径。'])
    # 25/26: Replay pinned local protocols, exact original C-Eval records.
    d=BASE/'selfcheck_calibration'; selected_ids=(d/'item_list_v1.txt').read_text().splitlines()[:3];pool={r['item_id']:r for r in rows(OLD/'sources/datasets/ceval/data/val.jsonl')};chosen=[pool[x.split('::',1)[1]] for x in selected_ids];selected=d/'selected_ceval_original.json';dump(selected,chosen)
    p07=trusted_functions(d/'p07_selfcheck.py',{'_CHECK_ZH'});p08=trusted_functions(d/'p08_calibration.py',{'_SUFFIX_ZH'})
    for n in (25,26):
        ids=[]
        for i,r in enumerate(chosen,1):
            q=r['question']+''.join('\n'+k+'. '+r[k] for k in 'ABCD')
            prompt=f"以下是中国关于{r.get('subject_zh') or ''}考试的单项选择题，请选出其中的正确答案。\n\n{q}\n\n请先给出正确选项字母（A/B/C/D）。"
            inter=None
            if n==25: inter=dict(mode='scripted',followups=[dict(role='user',content=p07['_CHECK_ZH'])])
            else: prompt+=p08['_SUFFIX_ZH']
            ids.append(task(n,i,'历史固定自查协议' if n==25 else '历史固定置信度协议',r,selected,'https://github.com/hkust-nlp/ceval',[dict(role='user',content=prompt)],'r1/r2 correctness; fix and break transitions' if n==25 else 'confidence/correctness pairs; Brier/CWR/ECE/AUROC',{'kind':'selfcheck' if n==25 else 'calibration'},origin='mechanism_authored',interaction=inter,deviations=['原 C-Eval 题目和答案不改；自查/置信度流程是本地历史协议，不是 C-Eval 官方 5-shot 排行榜协议。','从历史冻结抽样清单取前三题，不按本轮模型错题筛选。']))
        audit(n,'自查与改错' if n==25 else '置信度校准',[source('P07P08','Historical local protocol with original C-Eval','https://github.com/hkust-nlp/ceval',d/('p07_selfcheck.py' if n==25 else 'p08_calibration.py'),'fixed item_list_v1; intrinsic recheck' if n==25 else 'fixed item_list_v1; verbalized confidence; native calibration metrics')], '不提供外部错误提示，在实际解答后要求自检并保留错改对/对改错分母。' if n==25 else '让模型先答未给金标的真实试题并报告自身置信度，评分后配对正确性。','原证据是本地旧模型实验；不能把自评置信或两轮改分直接当课堂学习效果。',False,ids,['三例统计不稳定；无错题时 fix rate 未定义，只有一种正确性时 AUROC 未定义；不得用 0 代替。'])

def build_teacha():
    d=ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/teacha'
    revision='cbd99fcca76b076352388d01be10056a5ee47eb4';url='https://huggingface.co/datasets/CinderD/TeachArena'
    for n,ident,title,condition in [(14,'MM-04','诊断落实为补救材料','从原学生记录计算 KC 掌握情况，在指定已有课件中实改至少两页，并产生相关图示/检查题与指定通知。'),(15,'EXAM-REV-03','构念保持的试题修订','修改指定五道微积分题的参数，保留知识点，重算全部答案并保存到指定文档后公告。'),(16,'EI-C04','题目构念与区分度判断','分析近均匀选择分布、低点二列相关和 A/B/C 多个可辩护答案，不把选项均匀误作优质区分。')]:
        path=d/'tasks'/('stage1_pedagogical_judgment.json' if n==16 else 'stage2_teaching_workflows.json'); record=next(x for x in json.loads(path.read_text()) if x['id']==ident)
        src=source('TEACHA', 'TeachArena',url,path,ident,revision)
        ids=[]
        if n==16:
            msg=record['user_scenario']['instructions']['task_instructions'];ids=[task(n,1,title,record,path,url,[dict(role='system',content=(d/'policy.md').read_text()),dict(role='user',content=msg)],'TeachArena NL_ASSERTION + RESPONSE_CHECK',{'kind':'teacha'},revision=revision,deviations=['原 NL assertion judge 身份/调用未复现；保留完整原 assertion 和 response check，原评分待评，不替换为 GLM 自评。','原 README 指定 S1 无工具但使用 policy.md；其中工具优先/写入要求与 S1 no-tools 存在张力，完整保留源政策，不自行删改。'])]
        audit(n,title,[src,source('TEACHA-paper','Are Agents Ready to Teach?','https://arxiv.org/html/2605.14322v4',None,'case study '+ident)],condition,'原论文个案对比显示 plausibility 不保证指定任务/构念与产物完成；强模型存在成功反例。',True,ids,[] if n==16 else ['发布快照含 task/db/policies/evaluator，但未包含原 LMS action server/tool schema；仅发一个写计划 prompt 不能复现实际工具操作。'],status='ready_original' if n==16 else 'blocked_environment',route='original_task' if n==16 else 'preserve_original_await_native_environment')

def build_lda():
    d=ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13/lda'
    spec=importlib.util.spec_from_file_location('native_lda_prompting',d/'prompting.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    chosen=rows(d/'data/mohler.jsonl')[:3];selected=BASE/'lda_selected_mohler.json';dump(selected,chosen)
    prompt=mod.load_prompt(str(d/'prompts/default.txt'));ids=[]
    for i,r in enumerate(chosen,1):
        variants=[]
        for probe in ('base','ctx_neutral','ctx_low','ctx_high'):
            response,context=mod.probe_input(r,probe)
            variants.append(dict(probe=probe,messages=prompt.build(r,response,context)))
        ids.append(task(21,i,'LDA 同作品能力标签配对：base/neutral/low/high',r,selected,'https://github.com/Learning-Design-Alliance/ai-grading-benchmark',variants[0]['messages'],'paired score shift high-low; neutral-base; original 0–5 scale',{'kind':'lda','prompting_path':rel(d/'prompting.py')},revision='0c78a10db8a0b1fb735fda5e0a51a8bb89ce7c1e',interaction={'mode':'adapter','module':MODULE,'args':{'kind':'lda','variants':variants}},deviations=['独立四次评分，保留原短答案及上下文长度匹配；三个作品不足以断言群体公平。']))
    audit(21,'同作品能力标签与评分公平',[source('LDA','AI Grading Benchmark','https://github.com/Learning-Design-Alliance/ai-grading-benchmark',d/'prompting.py','CONTEXT; probe_input; prompts/default.txt; ctx_low/ctx_high','0c78a10db8a0b1fb735fda5e0a51a8bb89ce7c1e')], '完全相同作品在低/高既往成绩标签下独立打分；加 neutral 和无 context 基线区分文本存在与标签效应。','原 probe 测标签导致的相对评分偏移，不能据单篇评分变化判断统计公平或真实人群歧视。',True,ids,['native paired metric，不设人为二元通过阈值；原评分单位0–5。'])

def build_distractor():
    d=BASE/'distractor';path=d/'sciq_first3.json';data=json.loads(path.read_text());ids=[]
    fn=trusted_functions(d/'src/models/impl/naive_cot.py',{'prompt_joint_naive'})
    revision='9b533643741c619f08e2889dd1fcc600a7ba68f8'
    for i,raw in enumerate(data['rows'],1):
        r=raw['row'];r=dict(r,id='sciq_train_'+str(raw['row_idx']))
        p=fn['prompt_joint_naive']({'Problem':{'Question':r['question']}},3,'science')
        ids.append(task(18,i,'SciQ 原 distractor generation：naive CoT',r,path,'https://github.com/eth-lre/llm-student-modeling-strategies',[dict(role=k,content=v) for k,v in p.items()],'native proportional/exact/partial match; correct-option leakage and repetitions',{'kind':'distractor'},revision=revision,deviations=['选 SciQ 原 train 顺序首3例；原文随机500例缓存未发布，不能宣称重现其抽样总体。','只重放公开 naive_cot 策略，不代表原论文全部生成策略。','GPT-4.1-mini 原语义等价判官未获本轮调用配置；完整语义指标待评。']))
    audit(18,'科学题干扰项生成',[source('DIST','Can LLMs Model Incorrect Student Reasoning?','https://arxiv.org/html/2603.15547v2',d/'src/models/impl/naive_cot.py','§4–5; Appendix A.2; native naive_cot prompt',revision),source('SCIQ','SciQ original train records','https://huggingface.co/datasets/allenai/sciq',path,'train rows 0–2','2c94ad3e1aafab77146f384e23536f97a4849815'),source('DIST-SCORE','Original semantic equivalence and metrics','https://github.com/eth-lre/llm-student-modeling-strategies',d/'src/equality.py','ScienceSemanticEqualityChecker; src/evaluation.py',revision)], '不给人类干扰项，要求从原题生成三个错误选项；科学题会依赖近义联想，可能误给正确选项、重复或丢弃合理候选。','原研究以教师干扰项语义匹配与错误类型测量；并未验证每个选项对应真实学生误概念。',True,ids,['原语义 judge 待评；匹配教师选项不等于真实诊断效度。'])

def build_difficulty_blocker():
    d=BASE/'difficulty_alignment'
    src=[source('DIFF','Human–AI Difficulty Alignment','https://arxiv.org/html/2512.18880v2',d/'paper.html','§2.1 difficulty perception; Appendix D Figures 7–11'),source('DIFF-REPO','Difficulty Alignment public release','https://github.com/MingLiiii/Difficulty_Alignment',d/'Cambridge_gpt35_results.jsonl','README advertises data/Cambridge; public root lacks data; downloaded result rows contain only model_response'),source('CMCQRD','Cambridge original access','https://researchdatasets.cambridge.org/datasets/cambridge-multiple-choice-questions-reading-dataset',None,'registration form and dataset terms; not a public direct-download corpus')]
    audit(17,'既有试题对学生群体的难度预测',src,'在不给真实难度的条件下，从完整考试题及正确答案估计学生困难；低/中/高 proficiency 条件独立预测，和真实人类难度算 Spearman。','原研究讨论解题能力与人类困难估计分离；旧全覆盖题给出响应统计后计算比例没有测到这个行为。',False,[],['原作者公开树缺 README 声称的 formatted data；已读取两个 Cambridge 结果文件但仅有 model_response，没有原题或真实 difficulty。','CMCQRD 官方页需个人/机构注册和许可；未填写身份、未对外发信。','没有真实学生难度真值时，新编题不能赋予虚构难度金标；故保留测量缺口，不以 LongTutor CTT 比例推理替代。'],status='blocked_source',route='await_original_items_and_human_difficulty',search=[{'url':'https://github.com/MingLiiii/Difficulty_Alignment','checked':'repo root + model_results/diff/Cambridge; utils.py + README + response JSONL','result':'找到原 prompt 与 Spearman 评分，未获得带 processed_text/difficulty 的原记录'},{'url':'https://arxiv.org/html/2602.06631','checked':'ENEM paper datasets/methods and links','result':'未在文中定位配套公开原题-IRT真值及英文/图像转写发布'},{'url':src[2]['url'],'checked':'official download/registration page','result':'需要注册身份；当前材料不足'}])

def build_artifacts():
    for n,sub,url,revision,metric in [(19,'eduillustrate','https://github.com/ECNU-innoSpark/EduIllustrate','6ce312e95f42e7cf3ebf5703c16ac4bd100af571','original eight-dimensional document rubric; geometric mean'),(20,'interactscience','https://github.com/open-compass/InteractScience','c21ea8dffad175a43d810fa027a152113956e6ff','PFT pass rate / VQT action success / original visual checklist')]:
        d=BASE/sub;path=d/'selected_original.json';chosen=json.loads(path.read_text());ids=[]
        for i,r in enumerate(chosen,1):
            if n==19:
                image=d/'images'/f"{r['index']}.png";description=r['question']+'\n(Note: The attached image is the original diagram illustrating the problem setup.)'
                spec=importlib.util.spec_from_file_location('native_edui_prompts',d/'task_generator/__init__.py'); prompts=importlib.util.module_from_spec(spec);sys.modules[spec.name]=prompts;spec.loader.exec_module(prompts)
                prompt=prompts.get_prompt_scene_plan('',description)
                messages=[{'role':'user','content':[{'type':'text','text':prompt},{'type':'image_path','path':rel(image)}]}]
                interaction={'mode':'adapter','module':MODULE,'args':{'kind':sub,'description':description,'topic':f"problem_{r['index']}_{r['subject'].replace('-','_')}",'image_path':rel(image),'max_code_fixes':2}}
                deviations=['使用公开默认无 reference solution / 无RAG / 无visual-fix设置；保留原图。','代码只在无网络无凭证 bubblewrap 内运行；场景串行调度但 Scene1 anchor 与各原 prompt 不变。','本地源码在原commit上有27行运行修复：拒绝空代码、验证实际PNG存在；原commit文件与diff一并保存，避免把Manim退出0误报为有效图。','原 Gemini 3.0 Pro Preview 文档判官未配置；渲染成功不等于八维评分通过。']
                title='EduIllustrate 原高年级题：完整图文解释生成流水线'
            else:
                messages=[{'role':'user','content':[{'type':'text','text':r['lm_system_prompt']+r['question']}]}];interaction=None
                deviations=['使用原 lm/text-only 任务视图；原参考截图仅用于评分，不进入预测。','原 Playwright 1.53.0 测试文件不改；公开CDN依赖离线按固定哈希缓存，无法解析的依赖记环境缺口。','原 Gemini-2.5-Pro VQT 判官和 CLIP 尚未运行；PFT 不代替科学语义质量。']
                title='InteractScience 原交互科学演示：'+r['id']
            ident=task(n,i,title,r,path,url,messages,metric,{'kind':sub},revision=revision,interaction=interaction,parameters={'temperature':0.7 if n==19 else 0},deviations=deviations)
            t=json.loads((OUT/f'{ident}.json').read_text());t['fidelity']['environment']='完整代码产物；bubblewrap 隔离 Manim 渲染' if n==19 else '完整 HTML 产物；原 Playwright PFT/VQT 在隔离 Chromium 中执行'
            if n==19:t['assets'].append(dict(path=rel(image),sha256=sha(image),role='prediction'))
            else:
                for im in r['image_path']:
                    f=d/im;t['assets'].append(dict(path=rel(f),sha256=sha(f),role='scoring'))
            # Pin all trusted original prompt/test/scoring sources, not just case data.
            for f in sorted(d.rglob('*')):
                if f.is_file() and '__pycache__' not in f.parts and f.suffix in {'.py','.txt','.js','.json','.md','.patch'} and f!=path:
                    t['assets'].append(dict(path=rel(f),sha256=sha(f),role='runtime' if f.suffix in {'.py','.js'} else 'provenance'))
            dump(OUT/f'{ident}.json',t);ids.append(ident)
        if n==19:
            audit(n,'图文与连续图解释一致性',[source('EDUI','EduIllustrate','https://arxiv.org/html/2604.05005v2',d/'generate_explanation.py','§3 sequential anchoring; Appendix C geometry/physics failures; generate_markdown_diagrams',revision),source('EDUI-RUBRIC','Original eight dimensions',url,d/'eval_suite/doc_evaluation_rubric.json','eight native dimensions and score levels',revision)],'原高中物理/几何完整题和原图经过 outline→Scene1实现→Scene1代码/渲染→后续Scene锚定→图文文档；验证图示与题意、跨图样式及解释协调。','原研究发现逻辑、几何物理标注、文本图示协调可能失败；渲染完成只是运行信号，不是教学正确。',True,ids,['两例不能复现230题总体；原八维 judge 待评。'])
        else:
            audit(n,'交互科学演示的语义正确性',[source('INTERACT','InteractScience','https://arxiv.org/html/2510.09724v2',d/'test_llm.py','§4; Appendix E failure analysis; Appendix F Fields of Magnet Array',revision),source('INTERACT-TEST','Original executable test suites',url,d/'cal_metrics.py','PFT_tests, VQT_tests, native rate aggregation',revision)],'模型按原科学实现计划自由生成完整 HTML；对原指定参数、按钮和动态可视化执行原测试，不能仅检查JSON参数或静态样图。','原研究的功能通过与视觉科学质量相关较弱，科学逻辑/数值错误可与可用交互同时存在。',True,ids,['PFT 原测试自身有已知误报/漏报，保留原结果另列审阅；原 VLM judge 和CLIP待评。'])

def finalize_dependencies():
    deps={16:[ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/teacha/evaluator/evaluator_response_content.py',ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/teacha/evaluator/evaluator_nl_assertions.py',ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_27_37/teacha/policy.md'],
          20:[ROOT/'data/edu_last_exam_source_fidelity_v1/runtime_environment.json'],
          18:list((BASE/'distractor/src').rglob('*.py')),
          21:[ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13/lda/prompting.py',ROOT/'sources/datasets/edu_last_exam_source_fidelity_v1/group_01_13/lda/prompts/default.txt'],
          22:[p for p in (BASE/'asap_2').iterdir() if p.is_file()],
          23:[p for p in (BASE/'mathtutorbench').iterdir() if p.is_file()],
          24:[p for p in (BASE/'mooccube').iterdir() if p.is_file()],
          25:[p for p in (BASE/'selfcheck_calibration').iterdir() if p.is_file()],
          26:[p for p in (BASE/'selfcheck_calibration').iterdir() if p.is_file()]}
    for n in range(14,27):
        ap=AUDIT/f'{n:02}.json';a=json.loads(ap.read_text())
        if n in (14,15):a['original_task']['source_case_ids']=['MM-04' if n==14 else 'EXAM-REV-03']
        elif n==16:a['original_task']['source_case_ids']=['EI-C04']
        for ident in a['task_ids']:
            path=OUT/f'{ident}.json';t=json.loads(path.read_text());known={x['path'] for x in t['assets']}
            for f in deps.get(n,[]):
                if rel(f) not in known:t['assets'].append(dict(path=rel(f),sha256=sha(f),role='runtime' if f.suffix=='.py' else 'provenance'));known.add(rel(f))
            if n==18:t['prediction']['parameters']['temperature']=0.0
            if n==22:
                t['fidelity']['deviations'].append('来源文章为本地已保存 Kaggle mirror 文本转录；官方扫描 PDF 同时保留用于复核，尚未逐字对齐。')
            t['review']['author_offline_check']='passed deterministic source/schema/parser checks; semantic human review pending'
            dump(path,t)
        a['snapshot_dependencies']=[dict(path=rel(p),sha256=sha(p)) for p in deps.get(n,[])]
        if n in (24,25,26):
            bench={24:'mooccube_prereq',25:'p07_selfcheck',26:'p08_calibration'}[n]
            evidence=[]
            for model in ('minimax3','MiniMax-M3.1-Flash-Preview'):
                old=OLD/'reports/eval'/bench/model/'summary.json';dest=BASE/'historical_evidence'/bench/(model+'.json');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old,dest)
                value=json.loads(dest.read_text());evidence.append(value['extra_metrics'])
                a['sources'].append(source('HISTORY-'+model,'Observed historical '+bench+' / '+model,str(old),dest,'extra_metrics; fixed evaluation protocol'))
                a['snapshot_dependencies'].append(dict(path=rel(dest),sha256=sha(dest)))
            a['research_failure']['source_id']='HISTORY-minimax3'
            a['research_failure']['locator']='extra_metrics'
            a['research_failure']['model_setting']='MiniMax-M3 and MiniMax-M3.1-Flash-Preview; frozen local original protocols'
            a['research_failure']['observed_metrics']=evidence
            a['research_failure']['finding']={24:'200 MCQ / 100 order: M3 MCQ=.725, order-all-constraints=.28; M3.1 MCQ=.745, order=.33.',25:'M3 wrong→right 8/232 and right→wrong 5/318; M3.1 12/218 and 10/331, 1 missing second round.',26:'550 items/model: confidence>=90 wrong proportions .3262/.4004; means87.04/98.0 versus accuracy .5873/.5909.'}[n]
        if n==24:
            a['decision']['limitations'].append('原论文§2.3将先修定义为帮助理解；历史MCQ使用必须先掌握措辞更强，评分仅表述为与专家图一致，不解释成必要性因果结论。')
        dump(ap,a)

if __name__=='__main__':
    build_text_tasks()
    build_teacha()
    build_lda()
    build_distractor()
    build_difficulty_blocker()
    build_artifacts()
    finalize_dependencies()
