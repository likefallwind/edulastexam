#!/usr/bin/env python3
"""Render the recorded author review; never alter original predictions or scores."""
import json
import hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'private/edu_last_exam_h_patterns_v1/reviews/20261117_glm53flash_c3_author_review.json'
REPORT=ROOT/'reports/edu_last_exam_h_patterns_v1/20261117_glm53flash_c3_author_review'

def main():
    data=json.loads(SOURCE.read_text());rows=data['cases']
    predictions=[json.loads(l) for l in (ROOT/data['run']/'predictions.jsonl').read_text().splitlines()]
    assert len(rows)==len({r['case_id'] for r in rows})==57
    assert {r['case_id'] for r in rows}=={p['case_id'] for p in predictions}
    for r in rows:
        assert hashlib.sha256((ROOT/r['source_result']).read_bytes()).hexdigest()==r['prediction_sha256']
    summary={'review_scope':'author_related_offline_review','independent_teacher_review':False,'frozen':False,'run':data['run'],'reviewed_cases':len(rows),'base_items':len({r['item_id'] for r in rows}),'classification_counts':dict(Counter(r['classification'] for r in rows)),'target_error_cases':[r['case_id'] for r in rows if r['classification']=='target_error'],'target_error_base_items':len({r['item_id'] for r in rows if r['classification']=='target_error'}),'format_issue_cases':sum(bool(r['format_notes']) for r in rows),'no_cross_construct_accuracy':True}
    labels={'target_error':'明确目标错误','collateral_error':'附带实质错误','disputed':'争议待审','no_target_error_observed':'未见目标错误'}
    lines=['# GLM-5.3-Flash 错误机制候选作者复核','','57个版本全部完成，逐份读取回答、执行事件、最终文件及运行前量尺。本报告是作者关联离线复核，不是独立教师审核或冻结结论。','','明确目标错误2条（2个基础题族）；附带实质错误3条；争议2条；其余50条未见目标错误。分类不构成跨构念准确率。目标错误2/57版本、涉及2/18材料，仅作本次描述，不是模型总体失败率。','','|方向|明确目标错误|附带错误|争议|未见目标错误|','|---|---:|---:|---:|---:|']
    for d in ['02','05','10','12','14','23']:
        counts=Counter(r['classification'] for r in rows if r['direction_id']==d)
        lines.append('|'+d+'|'+ '|'.join(str(counts[k]) for k in labels)+'|')
    lines+=['','## 需要保留和复查的案例','']
    for r in rows:
        if r['classification']=='no_target_error_observed':continue
        lines += [f"### {r['case_id']} · {labels[r['classification']]}",'',r['reason'],'','证据：'+r['evidence_quote'],'',f"[原始结果]({(ROOT/r['source_result']).as_posix()})",'']
    lines+=['## 判读边界','','12-101-v1的教师答案仍位于公开合同指定的学生next_prompt字符串内，标注“不呈现给学生”不构成实际隔离；这是交付问题，不是已经观测到真实学生读到答案。若后续产品另有经验证的拆分器，应另设协议控制。','','10-102-v1已完成的G1引文无需再次逐字给出，G2在第一次check后得到有效区分；重复引文门槛是目标错误，但固定学生脚本可能放大循环长度。不得用这7轮推断自然学生对话必然持续7轮。','','23-103-v2的return问句可以被解释为检查是否仍有漏处理元素，原gold排除这一解读不够稳；其算例返回5是确定错误，但不证明标签判断失败。此题族应先审题，不能因gold不同即判真难。','','方向14的9份实际文件均通过合同；103-v1/v2新增错因与核验说明错误单列，不冒充文件修复失败。方向02所有评分和当前条件判断正确，但两条反馈将等权平均适用条件过度概括为只能人数相等。','','10个案例含格式问题或恢复过的无效JSON动作；按原量尺不将其算作目标机制失败。所有援助状态初始标签9/9正确，不能把12-101-v1交付泄漏泛化成模型不会识别提示。所有已完成流程控制3/3正常结束。','','## 全部逐例记录','',f'[机器可读作者复核]({SOURCE.as_posix()})','']
    for r in rows:
        lines += [f"- {r['case_id']}：{labels[r['classification']]}。{r['reason']}"+(' 附注：'+r['minor_note'] if r['minor_note'] else '')]
    REPORT.mkdir(parents=True,exist_ok=True)
    (REPORT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    (REPORT/'review.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
