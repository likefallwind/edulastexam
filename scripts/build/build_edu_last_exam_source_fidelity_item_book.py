#!/usr/bin/env python3
"""Export complete frozen questions and evidence into a local human review book."""
from __future__ import annotations

import base64
import copy
from collections import Counter
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.build.build_edu_last_exam_source_fidelity_review import ORIGINAL, OUTPUT as REVIEW_OUTPUT, LABELS
from scripts.source_fidelity.core import write_json

OUTPUT = Path('reports/source_fidelity_v1/human_review_book_20261111')
FOCUS = {'disputed','descriptive_only','mixed'}
ESC = lambda value: html.escape(str(value))

def is_focus(review):
    # Keep user-corrected items in the review queue so the revision is visible.
    return review['verdict'] in FOCUS or bool(review.get('review_revision'))


class Book:
    def __init__(self, root):
        self.root=Path(root);self.output=self.root/OUTPUT
        (self.output/'items').mkdir(parents=True,exist_ok=True)
        (self.output/'assets').mkdir(exist_ok=True)
        self.media={}

    def link(self,path):
        path=Path(path)
        if not path.is_absolute():path=self.root/path
        return os.path.relpath(path,self.output)

    def copy_media(self,data,suffix):
        digest=hashlib.sha256(data).hexdigest()
        name=digest[:24]+suffix
        dest=self.output/'assets'/name
        if not dest.exists():dest.write_bytes(data)
        self.media[name]={'sha256':digest,'bytes':len(data)}
        return 'assets/'+name

    def media_path(self,path):
        path=Path(path)
        if path.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.mp4','.pdf'}:
            return self.copy_media(path.read_bytes(),path.suffix.lower())
        return self.link(path)

    def media_url(self,url):
        if not url.startswith('data:'):return None
        header,data=url.split(',',1)
        suffix={'image/png':'.png','image/jpeg':'.jpg','image/webp':'.webp','video/mp4':'.mp4'}.get(header[5:].split(';')[0])
        if suffix is None:return None
        return self.copy_media(base64.b64decode(data),suffix)

    def media_html(self,link,label):
        ext=Path(link).suffix.lower()
        if ext=='.mp4':return f'<figure><video controls preload="none" src="{ESC(link)}"></video><figcaption>{ESC(label)}</figcaption></figure>'
        if ext in {'.png','.jpg','.jpeg','.webp'}:return f'<figure><a href="{ESC(link)}" target="_blank"><img loading="lazy" src="{ESC(link)}" alt="{ESC(label)}"></a><figcaption>{ESC(label)}</figcaption></figure>'
        return f'<p><a href="{ESC(link)}" target="_blank">{ESC(label)}</a></p>'

    def messages(self,messages,snapshot):
        rendered=[];markdown=[]
        for index,message in enumerate(messages):
            role=message['role'];content=message['content']
            label=f'{index+1}. {role}（此处assistant若出现在输入中，是原示例或前轮回答）' if role=='assistant' else f'{index+1}. {role}'
            rendered.append(f'<div class="message"><b>{ESC(label)}</b>');markdown.append(f'#### {label}\n')
            parts=[{'type':'text','text':content}] if isinstance(content,str) else content
            for part in parts:
                kind=part.get('type')
                if kind=='text':
                    text=part.get('text','')
                    rendered.append('<pre>'+ESC(text if text else '【空字符串】')+'</pre>')
                    markdown.append(text if text else '【空字符串】')
                elif kind in {'image_path','video_path'}:
                    link=self.media_path(snapshot/part['path']);caption=part['path']
                    rendered.append(self.media_html(link,caption));markdown.append(f'![{caption}]({link})' if kind=='image_path' else f'[视频材料]({link})')
                elif kind in {'image_url','video_url'}:
                    obj=part[kind];url=obj['url'] if isinstance(obj,dict) else obj
                    link=self.media_url(url)
                    if link:
                        rendered.append(self.media_html(link,'实际请求中的媒体'));markdown.append(f'![实际请求图像]({link})' if kind=='image_url' else f'[实际请求视频]({link})')
                    else:
                        rendered.append('<pre>'+ESC('未内嵌的媒体地址：'+url)+'</pre>');markdown.append('媒体地址：'+url)
                else:
                    rendered.append('<pre>'+ESC(json.dumps(part,ensure_ascii=False,indent=2))+'</pre>')
                    markdown.append(json.dumps(part,ensure_ascii=False,indent=2))
            rendered.append('</div>')
        return ''.join(rendered),'\n\n'.join(markdown)

    def question(self,task,snapshot):
        sections=[];md=[];view_count=0
        h,m=self.messages(task['prediction']['messages'],snapshot)
        sections.append(h);md.append(m)
        interaction=task['prediction']['interaction'];args=interaction.get('args',{})
        moment=task.get('reference',{}).get('moment',{})
        if not task['prediction']['messages'] and moment.get('context'):
            context=[{'role':turn['role'],'content':f"[原轮次 {turn.get('turn_number','?')}]\n"+turn['text']} for turn in moment['context']]
            h,m=self.messages(context,snapshot)
            sections.append('<p class="notice">原任务会话前缀：原协议拟提供给被测导师的上下文。本轮因缺少原动态学生角色而未实际执行；下列不是本轮GLM生成轨迹。</p>'+h)
            md.append('### 原任务会话前缀（拟用于导师输入；本轮未执行）\n\n'+m)
        for key in ('conditions','variants','probes'):
            for condition in args.get(key,[]):
                view_count+=1
                label=condition.get('name',condition.get('probe',str(view_count)))
                h,m=self.messages(condition.get('messages',[]),snapshot)
                if condition.get('fork_from'):
                    note=f"从 {condition['fork_from']} 基线独立分叉；实际先前回答见交互记录。追问：{condition.get('followup','')}"
                    h='<pre>'+ESC(note)+'</pre>'+h;m=note+'\n\n'+m
                sections.append(f'<details><summary>条件 {ESC(label)}</summary>{h}</details>');md.append(f'### 条件 {label}\n\n{m}')
        for n,followup in enumerate(interaction.get('followups',[]),1):
            message=followup if isinstance(followup,dict) else {'role':'user','content':followup}
            h,m=self.messages([message],snapshot)
            sections.append(f'<details><summary>预设学生跟进 {n}</summary>{h}</details>');md.append(f'### 预设学生跟进 {n}\n\n{m}')
        input_assets=[]
        for asset in task['assets']:
            if asset['role']!='prediction':continue
            path=snapshot/asset['path'];link=self.media_path(path)
            input_assets.append({'path':asset['path'],'sha256':asset['sha256'],'book_path':link})
            if path.suffix.lower() in {'.md','.txt'}:
                text=path.read_text();sections.append('<details><summary>输入材料全文：'+ESC(path.name)+'</summary><pre>'+ESC(text)+'</pre></details>');md.append(f'### 输入材料 {path.name}\n\n{text}')
            else:
                sections.append(self.media_html(link,'输入材料：'+path.name));md.append(f'[输入材料：{path.name}]({link})')
        if task.get('execution',{}).get('eligible') is False:
            reason=task['execution']['reason'];sections.append('<p class="notice">未执行：'+ESC(reason)+'</p>');md.append('未执行：'+reason)
        return ''.join(sections),'\n\n'.join(md),view_count,input_assets

    def item(self,task,review):
        case=task['case_id'];run=self.root/review['source_run'];snapshot=run.parent/'source_snapshot';directory=run/'cases'/case
        result_path=directory/'result.json';result=json.loads(result_path.read_text())
        if hashlib.sha256(result_path.read_bytes()).hexdigest()!=review['prediction_sha256']:raise ValueError('Review identity changed: '+case)
        question,question_md,view_count,input_assets=self.question(task,self.root/ORIGINAL.parent/'source_snapshot')
        response='<p>本次状态：'+ESC(result['status'])+'</p><pre>'+ESC(result.get('response') or result.get('reason') or result.get('error') or '无有效回答')+'</pre>'
        response_md=result.get('response') or result.get('reason') or result.get('error') or '无有效回答'
        call_count=0
        for request_path in sorted((directory/'calls/cases').glob('*/request.json')):
            call_count+=1;request=json.loads(request_path.read_text());ident=request_path.parent.name
            h,m=self.messages(request['payload']['messages'],snapshot)
            answer_path=request_path.parent/'result.json'
            answer=json.loads(answer_path.read_text()) if answer_path.exists() else {'status':'未完成','response':''}
            title=f"实际调用 {ident} · {answer['status']}"
            body=h+'<h5>该次可见回答</h5><pre>'+ESC(answer.get('response',''))+'</pre>'
            response+=f'<details><summary>{ESC(title)}</summary>{body}</details>'
            response_md+=f'\n\n### {title}\n\n{m}\n\n#### 该次可见回答\n\n'+answer.get('response','')
        # This includes skipped eligibility, validation attempts, tool feedback and real turns, but never hidden API reasoning.
        trajectory=[]
        for turn in result.get('transcript',[]):
            trajectory.append({k:v for k,v in turn.items() if k not in {'messages','payload','reasoning','reasoning_content'}})
        if trajectory:
            packed=json.dumps(trajectory,ensure_ascii=False,indent=2)
            response+='<details><summary>完整可见轨迹 / 原格式校验尝试 / 工具反馈 / 未触发分支</summary><pre>'+ESC(packed)+'</pre></details>'
            response_md+='\n\n### 完整可见轨迹\n\n```json\n'+packed+'\n```'
        artifact_files=[]
        for pattern in ('eduillustrate/scene*.png','scoring/interactscience/screenshots/**/*.png','workspace/slides.pdf'):
            artifact_files.extend(directory.glob(pattern))
        if case.startswith('ELE-SF-20-'):
            artifact_files.extend((directory/'scoring/interactscience').rglob('*.png'))
        for path in sorted(set(artifact_files)):
            link=self.media_path(path);response+=self.media_html(link,'实际产物：'+str(path.relative_to(directory)));response_md+=f'\n\n[实际产物：{path.name}]({link})'
        scoring=json.loads((directory/'scoring/score.json').read_text()) if (directory/'scoring/score.json').exists() else {}
        ref=copy.deepcopy(task['reference'])
        source_appendix={}
        if isinstance(ref.get('gold'),dict) and '_draft' in ref['gold']:
            source_appendix['old_gold_draft_not_current_reference']=ref['gold'].pop('_draft')
        if isinstance(ref.get('moment'),dict) and 'context' in ref['moment']:
            ref['moment'].pop('context')
            ref['moment']['context_location']='原任务会话前缀已单列在题面区；本轮未执行。以下student oracle续篇/trait/rubric是辅助角色或评审材料。'
        reference= {'reference':ref,'scoring':task['scoring']}
        reference_html='<p class="notice">本区为评审材料，其中可能重复题面已有信息。模型是否见过某段内容，以题面和实际请求为准；不要把金标、旧草稿、历史子集或评审私有背景误当作模型已见提示。</p><pre>'+ESC(json.dumps(reference,ensure_ascii=False,indent=2))+'</pre>'
        for asset in task['assets']:
            if asset['role']!='scoring':continue
            path=self.root/ORIGINAL.parent/'source_snapshot'/asset['path'];link=self.media_path(path)
            reference_html+=f'<p><a href="{ESC(link)}">原评分材料：{ESC(path.name)}</a></p>'
            if path.suffix in {'.txt','.md'}:reference_html+='<details><summary>展开材料全文</summary><pre>'+ESC(path.read_text())+'</pre></details>'
        reference_html+='<h4>原程序评分（保留原状）</h4><pre>'+ESC(json.dumps(scoring,ensure_ascii=False,indent=2))+'</pre>'
        if source_appendix:
            reference_html+='<details><summary>来源附录：旧参考草稿（不作为当前正式金标）</summary><pre>'+ESC(json.dumps(source_appendix,ensure_ascii=False,indent=2))+'</pre></details>'
        review_html='<p><b>'+ESC(LABELS[review['verdict']])+'</b> · '+ESC(review['reason'])+'</p><pre>'+ESC(json.dumps(review,ensure_ascii=False,indent=2))+'</pre>'
        provenance={'source':task['source'],'fidelity':task['fidelity'],'selection_reason':task['selection_reason'],'prediction_parameters':task['prediction'].get('parameters',{}),'interaction':task['prediction']['interaction'],'run':review['source_run'],'prediction_sha256':review['prediction_sha256']}
        run_manifest_path=run/'run_manifest.json'
        if run_manifest_path.exists():
            provenance['declared_run_protocol_changes']=json.loads(run_manifest_path.read_text()).get('changes',{})
        adapted_path=run/'adapted_tasks.json'
        if adapted_path.exists():
            adapted=next((t for t in json.loads(adapted_path.read_text()) if t['case_id']==case),{})
            provenance['retry_protocol']=adapted.get('retry_protocol',{})
        # Planned messages already appear above. Keep the protocol appendix small without dropping original source links.
        provenance['interaction']={k:v for k,v in provenance['interaction'].items() if k!='args'} | {'args':{k:v for k,v in task['prediction']['interaction'].get('args',{}).items() if k not in {'conditions','variants','probes'}}}
        focus=is_focus(review)
        article=f'<article id="{case}" data-case="{case}" data-verdict="{review["verdict"]}" data-focus="{str(focus).lower()}" data-search="{ESC(case+" "+task["title"])}"><h2>{case} · {ESC(task["title"])}</h2><p class="meta">方向 {ESC("、".join(task["direction_ids"]))} · {"外部原任务/公开示例" if task["origin"]=="original_task" else "机制自建或本地历史题"} · {ESC(LABELS[review["verdict"]])}</p><details class="question" open><summary>1. 完整原题与输入材料</summary>{question}</details><details><summary>2. GLM实际回答、完整交互与产物</summary>{response}</details><details><summary>3. 原参考答案、评分规则与补充背景</summary>{reference_html}</details><details><summary>4. Codex判定与具体依据</summary>{review_html}</details><details><summary>5. 来源、协议、参数与可见性边界</summary><pre>{ESC(json.dumps(provenance,ensure_ascii=False,indent=2))}</pre><a href="{ESC(self.link(directory/"result.json"))}">原始结果JSON</a></details><section class="notes"><h3>我的审核意见</h3><label>审核结论 <select class="decision"><option value="">尚未审核</option><option>认可当前判定</option><option>应判通过</option><option>应判未通过</option><option>题目或金标需修改</option><option>材料不足</option><option>保留连续/配对结果</option></select></label><textarea class="note" placeholder="写具体意见，例如：题面缺少哪些信息、哪个金标有误、应接受什么答案……"></textarea></section></article>'
        complete_md=f'# {case} · {task["title"]}\n\n方向：{", ".join(task["direction_ids"])}；当前判定：{LABELS[review["verdict"]]}\n\n## 完整原题与材料\n\n{question_md}\n\n## GLM实际回答与交互\n\n{response_md}\n\n## 参考答案与原评分（评审材料，可见性以实际请求为准）\n\n```json\n{json.dumps(reference,ensure_ascii=False,indent=2)}\n```\n\n## 原程序评分\n\n```json\n{json.dumps(scoring,ensure_ascii=False,indent=2)}\n```\n\n## Codex复核\n\n```json\n{json.dumps(review,ensure_ascii=False,indent=2)}\n```\n\n## 我的审核意见\n\n- 审核结论：\n- 题面/金标问题：\n- 对模型回答的判断：\n- 建议修改：\n'
        # Per-item Markdown lives one directory lower than the combined book.
        (self.output/'items'/f'{case}.md').write_text(complete_md.replace('](assets/','](../assets/'))
        entry={'case_id':case,'title':task['title'],'verdict':review['verdict'],'focus':focus,'direction_ids':task['direction_ids'],'planned_condition_count':view_count,'actual_calls':call_count,'input_assets':input_assets,'prediction_sha256':review['prediction_sha256'],'source_run':review['source_run'],'markdown':f'items/{case}.md'}
        return article,complete_md,entry


STYLE='''body{font:16px/1.65 system-ui;color:#223042;background:#f3f6fa;margin:0}header{background:#fff;padding:24px max(24px,calc((100vw - 1280px)/2));border-bottom:1px solid #d7e0e9}h1{margin:0;font-size:27px}header p{margin:8px 0}main{max-width:1280px;margin:20px auto;padding:0 20px}.toolbar{position:sticky;top:0;z-index:2;background:#f3f6faf5;padding:12px 0;display:flex;gap:8px;align-items:center;flex-wrap:wrap}button,select,input{font:inherit;padding:8px;border:1px solid #b7c5d4;border-radius:6px;background:white}button{cursor:pointer}button:disabled{opacity:.4;cursor:default}#jump{max-width:480px}#search{width:230px}article{display:none;background:#fff;padding:28px;border:1px solid #dae1e9;border-radius:10px}article.active{display:block}h2{font-size:22px;margin:0 0 10px}.meta{color:#657587}details{margin:14px 0;border:1px solid #d4dfe8;border-radius:6px;padding:12px}summary{font-weight:600;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.75 ui-monospace,monospace;background:#f7f9fc;padding:14px;border-radius:5px;max-height:none}.message{border-left:3px solid #a6bed7;padding-left:14px;margin:16px 0}img,video{max-width:100%;max-height:700px;object-fit:contain}figure{margin:14px 0}figcaption{color:#657587;font-size:13px;overflow-wrap:anywhere}.notice{background:#fff6df;padding:12px;border-radius:5px}a{color:#215ca0}textarea{display:block;width:100%;min-height:150px;box-sizing:border-box;padding:12px;margin-top:12px;font:inherit;border:1px solid #aebed0;border-radius:5px}.notes{border-top:2px solid #d7e0e9;margin-top:24px;padding-top:14px}#empty{display:none}.small{font-size:14px;color:#657587}@media(max-width:700px){article{padding:14px}#jump{max-width:100%}header{padding:16px}h1{font-size:23px}}@media print{header,.toolbar,.notes{display:none}article{display:block;break-after:page}details{display:block}}'''

SCRIPT='''const articles=[...document.querySelectorAll('article')];const filter=document.querySelector('#filter'),search=document.querySelector('#search'),jump=document.querySelector('#jump');const storageKey='edu-source-review-book-20261111';let notes={};try{notes=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(e){}let selected=location.hash.slice(1),visible=[];function save(){try{localStorage.setItem(storageKey,JSON.stringify(notes));document.querySelector('#saved').textContent='批注已保存在当前浏览器；请导出备份。'}catch(e){document.querySelector('#saved').textContent='浏览器不能保存，请及时导出批注。'}}function show(id){if(!visible.some(a=>a.dataset.case===id))id=visible[0]?.dataset.case||'';selected=id;articles.forEach(a=>a.classList.toggle('active',a.dataset.case===id));jump.value=id;const i=visible.findIndex(a=>a.dataset.case===id);document.querySelector('#position').textContent=visible.length?`${i+1} / ${visible.length}`:'0 / 0';document.querySelector('#prev').disabled=i<=0;document.querySelector('#next').disabled=i<0||i>=visible.length-1;document.querySelector('#empty').style.display=visible.length?'none':'block';if(id)history.replaceState(null,'','#'+id)}function refresh(){const q=search.value.toLowerCase();visible=articles.filter(a=>(filter.value==='all'||filter.value==='focus'&&a.dataset.focus==='true'||a.dataset.verdict===filter.value)&&a.dataset.search.toLowerCase().includes(q));jump.replaceChildren(...visible.map(a=>{let o=document.createElement('option');o.value=a.dataset.case;o.textContent=a.querySelector('h2').textContent;return o}));show(selected)}articles.forEach(a=>{const id=a.dataset.case,decision=a.querySelector('.decision'),note=a.querySelector('.note');decision.value=notes[id]?.decision||'';note.value=notes[id]?.note||'';function record(){notes[id]={case_id:id,title:a.querySelector('h2').textContent,decision:decision.value,note:note.value,updated_at:new Date().toISOString()};save()}decision.addEventListener('change',record);note.addEventListener('input',record)});filter.addEventListener('change',refresh);search.addEventListener('input',refresh);jump.addEventListener('change',()=>show(jump.value));function move(delta){let i=visible.findIndex(a=>a.dataset.case===selected);if(visible[i+delta]){show(visible[i+delta].dataset.case);window.scrollTo(0,0)}}document.querySelector('#prev').onclick=()=>move(-1);document.querySelector('#next').onclick=()=>move(1);function download(text,name,type){let url=URL.createObjectURL(new Blob([text],{type}));let a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}document.querySelector('#export-json').onclick=()=>download(JSON.stringify({book:'edu_source_20261111',exported_at:new Date().toISOString(),reviews:Object.values(notes)},null,2),'我的逐题审核意见.json','application/json');document.querySelector('#export-md').onclick=()=>download('# 我的逐题审核意见\\n\\n'+Object.values(notes).map(r=>'## '+r.title+'\\n\\n结论：'+(r.decision||'未定')+'\\n\\n'+r.note+'\\n').join('\\n'),'我的逐题审核意见.md','text/markdown');if(selected&&articles.some(a=>a.dataset.case===selected&&a.dataset.focus!=='true'))filter.value='all';refresh();'''


def build(root=ROOT):
    book=Book(root);root=Path(root)
    source=root/ORIGINAL.parent/'source_snapshot'
    tasks=[json.loads(line) for line in (source/'private/edu_last_exam_source_fidelity_v1/items.jsonl').read_text().splitlines()]
    reviews={r['case_id']:r for r in map(json.loads,(root/REVIEW_OUTPUT/'latest_case_reviews.jsonl').read_text().splitlines())}
    if set(reviews)!={t['case_id'] for t in tasks}:raise ValueError('All 81 task units must be represented')
    tasks.sort(key=lambda t:(not is_focus(reviews[t['case_id']]),t['case_id']))
    articles=[];entries=[];full=[];focus=[]
    for task in tasks:
        article,markdown,entry=book.item(task,reviews[task['case_id']]);articles.append(article);entries.append(entry);full.append(markdown)
        expected_messages=list(task['prediction']['messages'])
        for key in ('conditions','variants','probes'):
            for condition in task['prediction']['interaction'].get('args',{}).get(key,[]):
                expected_messages.extend(condition.get('messages',[]))
        case_directory=root/reviews[task['case_id']]['source_run']/'cases'/task['case_id']
        for path in (case_directory/'calls/cases').glob('*/request.json'):
            expected_messages.extend(json.loads(path.read_text())['payload']['messages'])
        for message in expected_messages:
            content=message['content']
            texts=[content] if isinstance(content,str) else [part['text'] for part in content if part.get('type')=='text']
            for text in texts:
                if text and ESC(text) not in article:raise ValueError('Input text was omitted: '+task['case_id'])
        if entry['focus']:focus.append(markdown)
    prefix='# 逐题审核册\n\n保留原题文字、完整可见交互、原参考与Codex判定；包括长历史全文。判定为作者关联复核，供用户逐项审核，不是已冻结benchmark。原始材料不足的单元仍明确未测。\n\n'
    (book.output/'all_81.md').write_text(prefix+'\n\n---\n\n'.join(full))
    focus_counts=Counter(e['verdict'] for e in entries if e['focus'])
    focus_name=f'focus_{len(focus)}.md'
    focus_text=prefix+'重点审核（含已修正条目）：'+ '；'.join(f'{LABELS[k]} {v}项' for k,v in focus_counts.items())+'。\n\n'+'\n\n---\n\n'.join(focus)
    (book.output/focus_name).write_text(focus_text)
    (book.output/'focus.md').write_text(focus_text)
    manifest={'built_at':datetime.now(timezone.utc).isoformat(),'cases':len(entries),'focus_cases':len(focus),'verdict_counts':dict(Counter(e['verdict'] for e in entries)),'entries':entries,'media':book.media,'hidden_api_reasoning_exported':False,'original_run_modified':False,'source_review_sha256':hashlib.sha256((root/REVIEW_OUTPUT/'latest_case_reviews.jsonl').read_bytes()).hexdigest()}
    write_json(book.output/'manifest.json',manifest)
    write_json(book.output/'validation.json',{'passed':True,'cases':len(entries),'focus_cases':len(focus),
        'planned_and_actual_input_texts_verified':True,'review_prediction_hashes_verified':True,
        'media_sha256':book.media,'original_inputs_and_results_untouched':True})
    controls='''<div class="toolbar"><select id="filter" aria-label="题目范围"><option value="focus">优先审核：争议 / 连续 / 配对（32）</option><option value="all">全部81个测试单元</option><option value="disputed">争议</option><option value="descriptive_only">描述性结果</option><option value="mixed">配对混合</option><option value="fail">未通过</option><option value="pass">通过</option><option value="not_evaluable">未测</option><option value="pending_rerun">待补跑复核</option></select><input id="search" placeholder="搜索编号或题目" aria-label="搜索题目"><select id="jump" aria-label="跳转题目"></select><button id="prev">上一题</button><span id="position"></span><button id="next">下一题</button></div>'''
    page='<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Edu Last Exam · 逐题审核册</title><style>'+STYLE+'</style></head><body><header><h1>Edu Last Exam · 逐题审核册</h1><p>81个测试单元；默认先看32项争议、连续或配对结果。多个单元可能复用同一基础题，完整题面与各条件均保留。</p><p>先看题面，再按需展开模型回答、参考答案与Codex判断。评审材料与实际输入分区显示，可见性以每次原请求为准。</p><button id="export-json">导出审核意见 JSON</button> <button id="export-md">导出审核意见 Markdown</button><p id="saved" class="small">批注仅保存在当前浏览器，不会自动写回仓库；请导出备份。此册是生成时的审阅快照，后续补跑状态见运行报告。</p></header><main>'+controls+'<p id="empty">当前筛选没有题目。</p>'+''.join(articles)+'</main><script>'+SCRIPT+'</script></body></html>'
    page=page.replace('优先审核：争议 / 连续 / 配对（32）',f'重点审核（含已修正条目）· {len(focus)}项')
    page=page.replace('默认先看32项争议、连续或配对结果。',f'默认先看{len(focus)}项重点材料，包含争议、连续/配对结果及已修正条目。')
    (book.output/'review_book.html').write_text(page)
    index=prefix+'- [交互审核册](review_book.html)\n- [重点32项全文](focus_32.md)\n- [全部81项全文](all_81.md)\n\n|编号|题目|当前判定|\n|---|---|---|\n'
    for e in entries:index+=f'|[{e["case_id"]}]({e["markdown"]})|{e["title"].replace("|","/")}|{LABELS[e["verdict"]]}|\n'
    index=index.replace('[重点32项全文](focus_32.md)',f'[重点{len(focus)}项全文（含已修正条目）]({focus_name})')
    (book.output/'index.md').write_text(index)
    print(json.dumps({'output':str(book.output),'cases':len(entries),'focus_cases':len(focus),'media_files':len(book.media),'html_bytes':len(page.encode())},ensure_ascii=False))
    return manifest


if __name__=='__main__':build()
