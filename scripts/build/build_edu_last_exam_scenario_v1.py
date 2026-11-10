#!/usr/bin/env python3
"""Export five scenario-first candidate packages without model calls.

Authoring sources live in private/edu_last_exam_scenario_v1/authored/ and stimuli/.
--validate-only is read-only and checks both source contracts and export identity.
--fetch-assets explicitly retrieves the two pinned public images into ignored
sources/datasets; it does not fetch textbook content or invoke any model.
HTML export requires markdown-it-py, as does the research-note renderer.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / 'private/edu_last_exam_scenario_v1'
DATA = ROOT / 'data/edu_last_exam_scenario_v1'
REPORT = ROOT / 'reports/scenario_v1/authoring_20261110/build_report.json'
PROMPT_FIELDS = {'prompt_id', 'system_prompt', 'user_prompt', 'assets', 'interaction_mode'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()


def jsonl(rows):
    return ''.join(json.dumps(x, ensure_ascii=False) + '\n' for x in rows).encode()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def safe_asset(relative, batch=BATCH):
    path = Path(relative)
    require(not path.is_absolute() and '..' not in path.parts and path.parts[0] == 'stimuli',
            f'Unsafe asset path: {relative}')
    target = (batch / path).resolve()
    require(target.is_relative_to((batch / 'stimuli').resolve()), f'External asset: {relative}')
    return target


def source_image_path(entry):
    path = (ROOT / entry['source_local_path']).resolve()
    require(path.is_relative_to((ROOT / 'sources/datasets/edu_last_exam_scenario_v1').resolve()),
            'External source path must stay under the declared ignored dataset directory')
    return path


def image_bytes(entry):
    path = source_image_path(entry)
    require(path.is_file(), f'Missing source image: {path}. Run with --fetch-assets first; no proxy image is permitted.')
    content = path.read_bytes()
    require(len(content) == entry['bytes'] and sha(content) == entry['sha256'], f'Image identity mismatch: {path}')
    require(content.startswith(b'\x89PNG\r\n\x1a\n'), f'Not PNG: {path}')
    return content


def fetch_assets(sources):
    for entry in sources['images']:
        path = source_image_path(entry)
        if path.exists():
            image_bytes(entry)
            continue
        url = entry['source_url']
        require(url.startswith('https://raw.githubusercontent.com/gt-learning-innovation/CIRCUIT_EDU_HW_ACL/'),
                'Unexpected image source URL')
        require(entry['source_commit'] in url and 0 < entry['bytes'] < 16_000_000, 'Invalid pinned image contract')
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read(entry['bytes'] + 1)
        require(len(content) == entry['bytes'] and sha(content) == entry['sha256'], 'Downloaded image does not match pin')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print(json.dumps({'source_assets': len(sources['images']), 'identity': 'verified', 'model_calls': 0}))


def load_items():
    return [read(p) for p in sorted((BATCH / 'authored').glob('*.json'))]


def validate_contract(items, sources, batch=BATCH):
    ids = [x['item_id'] for x in items]
    require(len(ids) == len(set(ids)) and len(ids) > 0, 'Duplicate/empty item ids')
    external = {x['delivery_path']: x for x in sources['images']}
    for item in items:
        require(item['scenario_id'] in {'S01', 'S02', 'S03'}, 'Unexpected scenario')
        require(item['source_evidence'] and item['failure_mechanism'] and item['education_consequence'], 'Missing evidence/construct')
        require(not item['status']['canonical'] and not item['status']['frozen'], 'Candidate cannot silently become canonical')
        require(item['status']['human_review'] == 'pending' and item['status']['model_evaluation'] == 'not_run',
                'This build describes authoring only; review/run evidence must be managed separately')
        require(item['status']['difficulty'] == 'not_measured', 'Cannot infer difficulty from authoring')
        require(item['author']['author_model_must_be_excluded_from_tested_panel'], 'Missing author/panel separation')
        require(item['atomic_abilities'] == [], 'This batch does not introduce capability labels')
        require(item['rubric']['pass_threshold'] is None, 'An uncalibrated pass threshold is not permitted')
        require(sum(c['points'] for c in item['rubric']['criteria']) == item['rubric']['total_points'] == 10, 'Invalid rubric total')
        criteria_ids = [c['criterion_id'] for c in item['rubric']['criteria']]
        require(len(criteria_ids) == len(set(criteria_ids)), 'Duplicate criterion')
        pids = [p['prompt_id'] for p in item['prompts']]
        require(len(pids) == len(set(pids)), 'Duplicate prompt ids')
        require(set(pids) == set(item['gold']['per_prompt']), 'Gold/prompt alignment mismatch')
        for p in item['prompts']:
            require(set(p) == PROMPT_FIELDS, 'Prompt export fields may not include gold or curator metadata')
            require(p['interaction_mode'] in {'single_turn', 'decision_snapshot'}, 'These are independent snapshots, not sessions')
            require(p['system_prompt'].strip() and p['user_prompt'].strip(), 'Empty prompt')
            for asset in p['assets']:
                path = safe_asset(asset, batch)
                if asset in external:
                    image_bytes(external[asset])
                else:
                    require(path.is_file() and path.suffix in {'.md', '.json'}, f'Missing/unsupported textual stimulus: {asset}')
            g = item['gold']['per_prompt'][p['prompt_id']]
            require(g['acceptable_alternatives'] and g['critical_errors'], 'Missing acceptable answers or critical errors')
        require(item['controls'], 'Each package declares its paired control')
        for control in item['controls']:
            require(set(control['variants']) <= set(pids), 'Control refers to missing variant')


def check_oracles(items, batch=BATCH):
    """Independent arithmetic/linear-system/contrast checks, not a model judge."""
    by = {i['item_id']: i for i in items}
    results = []
    age = (79 + 5) / 2 - (35 - 23)
    g = by['ELE-S01-001']['gold']['per_prompt']
    require(age == 30 and all(v['answer'] == age for v in g.values()), 'Age gold contradicts problem equations')
    require([g[p]['first_invalid_step'] for p in ['a', 'b', 'c']] == [None, None, 'S2'], 'Age first-error gold invalid')
    require([g[p]['reference_is_valid'] for p in ['a', 'b', 'c']] == [False, True, True], 'Age reference controls invalid')
    results.append({'item_id': 'ELE-S01-001', 'check': 'age difference, inverse operation, repaired upstream gold', 'status': 'passed'})
    total = 72 - 3 * (12 + 7)
    g = by['ELE-S01-002']['gold']['per_prompt']
    require(total == 15 and total / 3 == 5 and all(v['answer'] == total for v in g.values()), 'Kitchen oracle mismatch')
    require(g['a']['first_invalid_step'] == 'S6' and g['b']['first_invalid_step'] is None, 'Kitchen gold must not inherit upstream S4')
    require(g['a']['valid_prefix'] == ['S1', 'S2', 'S3', 'S4', 'S5'], 'Kitchen valid prefix mismatch')
    results.append({'item_id': 'ELE-S01-002', 'check': 'per-structure vs total quantity and valid algebra prefix', 'status': 'passed'})
    for g in by['ELE-S02-001']['gold']['per_prompt'].values():
        require(g['si_amplitude_v'] == 250e-3 * 60000, 'Inductor SI calculation invalid')
        require(g['milliamp_amplitude_v'] == 250e-3 * (60000e-3), 'Inductor mA conversion invalid')
    results.append({'item_id': 'ELE-S02-001', 'check': 'conditional SI/mA arithmetic; image reading requires human review', 'status': 'passed'})
    vs = 48 * complex(math.cos(math.pi / 4), math.sin(math.pi / 4))
    a = 1 / 50j + 1 / 20 + 2.25 / 30 + 2.25 / (-40j)
    b, c, d = -1 / 30, -2.25 / 30, 1 / 30 + 1 / 25j
    v2 = (vs / 50j) / (a - b * c / d)
    vo = -c * v2 / d
    v3 = 2.25 * v2
    require(abs((vs - v2) / 50j - v2 / 20 - (v3 - vo) / 30 - v3 / (-40j)) < 1e-12, 'Supernode residual')
    require(abs((v3 - vo) / 30 - vo / 25j) < 1e-12, 'Output KCL residual')
    phase = math.degrees(math.atan2(vo.imag, vo.real))
    for g in by['ELE-S02-002']['gold']['per_prompt'].values():
        require(g['first_invalid_step'] is None, 'Valid circuit work must not be labelled incorrect')
        require(abs(g['vo_real'] - vo.real) < 1e-9 and abs(g['vo_imag'] - vo.imag) < 1e-9, 'Phasor gold mismatch')
        require(abs(g['vo_magnitude'] - abs(vo)) < 1e-9 and abs(g['vo_phase_degrees'] - phase) < 1e-9, 'Magnitude/phase mismatch')
    require(abs(abs(vo) - 14.67) <= .05 and abs(phase - 5.6) <= .1, 'Student rounding exceeds public tolerance')
    results.append({'item_id': 'ELE-S02-002', 'check': 'two independent KCL residuals and public rounding tolerances', 'status': 'passed'})
    histories = {p: read(batch / f'stimuli/S03_001/history_{p}.json')['records'] for p in ['a', 'b', 'c']}
    changed = {'R07', 'R09', 'R11'}
    require(len(histories['a']) == 12 and len({r['record_id'] for r in histories['a']}) == 12, 'History records invalid')
    for p in ['b', 'c']:
        require(len(histories[p]) == len(histories['a']), 'History condition lengths differ')
        actual = set()
        for baseline, variant in zip(histories['a'], histories[p]):
            x, y = copy.deepcopy(baseline), copy.deepcopy(variant)
            hx, hy = x.pop('help'), y.pop('help')
            require(x == y, 'History counterfactual changed content other than assistance')
            if hx != hy:
                actual.add(x['record_id'])
                require(hx == 'none', 'Baseline assistance must be explicitly absent')
                require(hy == 'unknown' if p == 'c' else '答案' in hy, 'Assistance manipulation invalid')
        require(actual == changed, 'History contrast changed unexpected rows')
    for g in by['ELE-S03-001']['gold']['per_prompt'].values():
        require(g['current_answer'] == .5 * (8 / 2) * (5 / 2) == 5, 'Current geometry oracle invalid')
        require(set(g['diagnostic_records']) == changed, 'Diagnostic evidence references wrong records')
        require(set(g['counterevidence_records']) <= {r['record_id'] for r in histories['a']}, 'Unknown evidence record')
    require((6 * 9 / 2) / (4 * 6 / 2) == 9 / 4 and math.sqrt(9 / 36) == .5, 'Historical geometry sanity check')
    results.append({'item_id': 'ELE-S03-001', 'check': 'geometry arithmetic and assistance-only counterfactuals; pedagogical judgment pending', 'status': 'passed'})
    return results


def html_document(markdown, title):
    from markdown_it import MarkdownIt
    import html
    body = MarkdownIt('commonmark', {'html': False}).enable('table').render(markdown)
    return ('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>'
            'body{font:16px/1.8 system-ui,sans-serif;max-width:1080px;margin:32px auto;padding:0 22px;color:#20303b}'
            'h2{border-top:2px solid #dbe5e9;margin-top:48px;padding-top:24px}h3{color:#205b70}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5f7;padding:16px}'
            'img{max-width:100%;height:auto;border:1px solid #dce4e8}a{color:#176b87;overflow-wrap:anywhere}'
            'table{border-collapse:collapse}td,th{border:1px solid #ccd8df;padding:10px;vertical-align:top}'
            '</style><body>' + body + '</body></html>\n').encode()


def render_outputs(items, sources, checks):
    prompts = [{'item_id': i['item_id'], **p} for i in items for p in i['prompts']]
    outputs = {BATCH / 'items.jsonl': jsonl(items), BATCH / 'prompts.jsonl': jsonl(prompts)}
    questions = ['# Edu Last Exam 场景候选题册', '', '5个任务包、12个独立投递版本；本册不含评分金标。成对版本分开投递，不是12道独立题，也不是真实多轮。', '', '[材料来源与许可说明](NOTICE.md) · [批次说明](README.md)', '']
    review = ['# Edu Last Exam 场景候选审阅册', '', '**仅供审阅，不投递给被测模型。** 作者离线核验；专家审核pending、当前模型难度未测、未冻结。', '', '[材料来源与许可说明](NOTICE.md) · [题册](questions.html)', '']
    for i in items:
        questions += [f'## {i["item_id"]} · {i["title"]}', '']
        review += [f'## {i["item_id"]} · {i["title"]}', '', f'场景：{i["scenario_id"]}；材料：{i["material_origin"]}', '', '机制：' + i['failure_mechanism'], '', '教育后果：' + i['education_consequence'], '', '### 来源与改编', '']
        review += [f'- [{s["source_id"]}]({s["url"]})；定位：{s.get("record_locator",s.get("locator","机制证据"))}' for s in i['source_evidence']]
        review += [''] + ['- ' + a for a in i['adaptations']] + ['']
        for p in i['prompts']:
            questions += [f'### 版本 {p["prompt_id"]}', '', '**系统要求**', '', p['system_prompt'], '', '**任务**', '', p['user_prompt'], '']
            for asset in p['assets']:
                questions += ['**附件**', '']
                if Path(asset).suffix == '.png':
                    questions += [f'![学生原作]({asset})', '']
                else:
                    body = (BATCH / asset).read_text(encoding='utf-8')
                    questions += ['```' + ('json' if asset.endswith('.json') else 'text'), body.rstrip(), '```', '']
            review += [f'### {p["prompt_id"]} · 参考答案与关键错误', '', '```json', json.dumps(i['gold']['per_prompt'][p['prompt_id']], ensure_ascii=False, indent=2), '```', '']
        review += ['### 可观察评分标准', '', '```json', json.dumps(i['rubric'], ensure_ascii=False, indent=2), '```', '', '### 成对控制', '']
        review += [f'- {"/".join(c["variants"])}：{c["expected"]}' for c in i['controls']]
        review += ['', '### 限制', ''] + ['- ' + a for a in i['limitations']] + ['']
        outputs[BATCH / 'reference' / f'{i["item_id"]}.json'] = encoded({'gold': i['gold'], 'rubric': i['rubric'], 'controls': i['controls']})
    for name, lines, title in [('questions', questions, '候选题册'), ('review', review, '候选审阅册')]:
        text = '\n'.join(lines) + '\n'
        outputs[BATCH / f'{name}.md'] = text.encode()
        outputs[BATCH / f'{name}.html'] = html_document(text, title)
    sheet = io.StringIO(newline='')
    writer = csv.writer(sheet)
    writer.writerow(['item_id', 'scenario', 'variants', 'material_origin', 'author_offline_check', 'human_review', 'model_evaluation', 'difficulty', 'release_status'])
    for i in items:
        writer.writerow([i['item_id'], i['scenario_id'], len(i['prompts']), i['material_origin'], 'passed_bounded_checks', 'pending', 'not_run', 'not_measured', 'not_frozen'])
    outputs[BATCH / 'review_sheet.csv'] = sheet.getvalue().encode('utf-8-sig')
    for entry in sources['images']:
        outputs[safe_asset(entry['delivery_path'])] = image_bytes(entry)
    source_files = list((BATCH / 'authored').glob('*.json')) + [BATCH / 'cards.jsonl', BATCH / 'README.md', BATCH / 'NOTICE.md', DATA / 'source_manifest.json', DATA / 'protocol.json', Path(__file__).resolve()]
    source_files += [BATCH / a for p in prompts for a in p['assets'] if not a.endswith('.png')]
    source_hashes = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted(set(source_files))}
    manifest = {'schema_version': 'edu_last_exam_scenario_v1_2026-11-10', 'status': 'author_offline_validated_candidate',
                'package_count': len(items), 'prompt_count': len(prompts), 'image_prompt_count': sum(any(a.endswith('.png') for a in p['assets']) for p in prompts),
                'human_review': 'pending', 'model_evaluation': 'not_run', 'difficulty': 'not_measured', 'canonical': False,
                'real_multiturn': False, 'source_sha256': source_hashes,
                'export_sha256': {str(p.relative_to(BATCH)): sha(b) for p,b in sorted(outputs.items())}, 'offline_checks': checks}
    outputs[BATCH / 'manifest.json'] = encoded(manifest)
    outputs[REPORT] = encoded({'status': manifest['status'], 'package_count': len(items), 'prompt_count': len(prompts), 'checks': checks,
                              'not_proven': ['educational validity', 'current model difficulty', 'judge reliability', 'public image redistribution permission'],
                              'human_review': 'pending', 'model_evaluation': 'not_run', 'manifest_sha256': sha(outputs[BATCH / 'manifest.json'])})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--fetch-assets', action='store_true')
    args = parser.parse_args()
    require(not (args.validate_only and args.fetch_assets), '--validate-only must not perform downloads')
    sources = read(DATA / 'source_manifest.json')
    if args.fetch_assets:
        fetch_assets(sources)
        return
    items = load_items()
    protocol = read(DATA / 'protocol.json')
    cards = [json.loads(x) for x in (BATCH / 'cards.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
    require({c['item_id'] for c in cards} == {i['item_id'] for i in items} and len(cards) == len(items), 'Cards/authored alignment mismatch')
    require(len(items) == protocol['package_count'] and sum(len(i['prompts']) for i in items) == protocol['prompt_count'], 'Protocol counts mismatch')
    validate_contract(items, sources)
    checks = check_oracles(items)
    outputs = render_outputs(items, sources, checks)
    if args.validate_only:
        stale = [str(p.relative_to(ROOT)) for p,b in outputs.items() if not p.is_file() or p.read_bytes() != b]
        require(not stale, 'Missing/stale exports: ' + ', '.join(stale))
    else:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'status': 'validated' if args.validate_only else 'exported', 'packages': len(items), 'prompts': protocol['prompt_count'], 'offline_checks': len(checks), 'human_review': 'pending', 'model_evaluation': 'not_run'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
