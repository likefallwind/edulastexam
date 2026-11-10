#!/usr/bin/env python3
"""Build a pinned instruction-only control; never call a model or the network."""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'private/edu_last_exam_scenario_v1'
BATCH = ROOT / 'private/edu_last_exam_scenario_neutral_v1'
SPEC = ROOT / 'data/edu_last_exam_scenario_neutral_v1/prompt_control.json'
REPORT = ROOT / 'reports/scenario_neutral_v1/authoring_20261110/build_report.json'
module_spec = importlib.util.spec_from_file_location(
    'scenario_parent_builder', ROOT / 'scripts/build/build_edu_last_exam_scenario_v1.py')
parent = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(parent)
require, sha, encoded = parent.require, parent.sha, parent.encoded


def load_context():
    spec = parent.read(SPEC)
    require(spec['parent_batch'] == str(PARENT.relative_to(ROOT)), 'Unexpected parent batch')
    require(sha((PARENT / 'prompts.jsonl').read_bytes()) == spec['parent_prompt_sha256'], 'Parent prompt drift')
    require(sha((PARENT / 'manifest.json').read_bytes()) == spec['parent_manifest_sha256'], 'Parent manifest drift')
    items = parent.load_items()
    sources = parent.read(parent.DATA / 'source_manifest.json')
    parent.validate_contract(items, sources)
    checks = parent.check_oracles(items)
    for path, content in parent.render_outputs(items, sources, checks).items():
        require(path.is_file() and path.read_bytes() == content, f'Parent export drift: {path}')
    return spec, items, checks


def validate_intervention(original, neutral, spec):
    require(len(original) == len(neutral) == spec['package_count'], 'Package count drift')
    count = images = 0
    for before, after in zip(original, neutral):
        require(before['item_id'] == after['item_id'], 'Item identity drift')
        require({k: v for k, v in before.items() if k != 'prompts'} ==
                {k: v for k, v in after.items() if k != 'prompts'}, 'Non-prompt item data changed')
        contract = spec['packages'][before['item_id']]
        require(len(before['prompts']) == len(after['prompts']), 'Variant count drift')
        for old, new in zip(before['prompts'], after['prompts']):
            require(set(new) == parent.PROMPT_FIELDS, 'Unexpected prompt fields or metadata leak')
            require({k: v for k, v in old.items() if k not in {'system_prompt', 'user_prompt'}} ==
                    {k: v for k, v in new.items() if k not in {'system_prompt', 'user_prompt'}},
                    'Asset, identity or interaction mode changed')
            for fragment in contract['required_fragments']:
                require(fragment in new['user_prompt'], f'Missing necessary condition: {fragment}')
            for fragment in contract['removed_instruction_fragments']:
                require(fragment not in new['user_prompt'], f'Removed instruction reintroduced: {fragment}')
            require(new['system_prompt'] == spec['system_prompt'], 'Unexpected system instruction')
            require(new['user_prompt'] == contract['user_prompt'], 'Neutral prompt differs from authored control')
            require(new['system_prompt'] != old['system_prompt'], 'System intervention missing')
            count += 1
            images += any(Path(a).suffix == '.png' for a in new['assets'])
    require(count == spec['prompt_count'] and images == spec['image_prompt_count'], 'Prompt/modality count drift')


def derive(original, spec):
    neutral = copy.deepcopy(original)
    for item in neutral:
        for prompt in item['prompts']:
            prompt['system_prompt'] = spec['system_prompt']
            prompt['user_prompt'] = spec['packages'][item['item_id']]['user_prompt']
    validate_intervention(original, neutral, spec)
    return neutral


def build_outputs(spec, original, checks):
    items = derive(original, spec)
    rows = [{'item_id': item['item_id'], **p} for item in items for p in item['prompts']]
    outputs = {BATCH / 'items.jsonl': parent.jsonl(items), BATCH / 'prompts.jsonl': parent.jsonl(rows)}
    assets = sorted({a for row in rows for a in row['assets']})
    for asset in assets:
        outputs[BATCH / asset] = parent.safe_asset(asset, PARENT).read_bytes()
    for item in items:
        ident = item['item_id']
        outputs[BATCH / 'authored' / f'{ident}.json'] = encoded(item)
        outputs[BATCH / 'reference' / f'{ident}.json'] = (PARENT / 'reference' / f'{ident}.json').read_bytes()
    for filename in ['cards.jsonl', 'NOTICE.md', 'review_sheet.csv']:
        outputs[BATCH / filename] = (PARENT / filename).read_bytes()

    questions = ['# Edu Last Exam 中性题面对照', '',
                 '5个任务包、12个独立投递版本；本册无评分金标。', '',
                 '[批次说明](README.md) · [来源及许可](NOTICE.md)', '']
    comparison = ['# 原题面与中性题面对照', '',
                  '仅改变系统和任务指令；全部附件、答案和rubric沿用。此册不投递给模型。', '',
                  '[中性题册](questions.html) · [批次说明](README.md)', '',
                  '## 共用系统指令', '', '**原版**', '', original[0]['prompts'][0]['system_prompt'], '',
                  '**中性版**', '', spec['system_prompt'], '']
    for old, item in zip(original, items):
        ident = item['item_id']
        questions += [f'## {ident} · {item["title"]}', '']
        comparison += [f'## {ident} · {item["title"]}', '', spec['packages'][ident]['change_note'], '',
                       '**原版任务**', '', old['prompts'][0]['user_prompt'], '',
                       '**中性版任务（同包各版本一致）**', '', item['prompts'][0]['user_prompt'], '']
        for p in item['prompts']:
            questions += [f'### 版本 {p["prompt_id"]}', '', '**系统要求**', '', p['system_prompt'], '',
                          '**任务**', '', p['user_prompt'], '']
            for asset in p['assets']:
                questions += ['**附件**', '']
                if Path(asset).suffix == '.png':
                    questions += [f'![学生原作]({asset})', '']
                else:
                    questions += ['```' + ('json' if asset.endswith('.json') else 'text'),
                                  outputs[BATCH / asset].decode().rstrip(), '```', '']
    review = ('# 中性题面对照：沿用参考解与评分标准\n\n' + spec['scoring_note'] +
              '\n\n当前运行/审阅状态由独立实验记录维护；以下为父批次作者参考。\n\n' +
              (PARENT / 'review.md').read_text())
    for name, markdown in [('questions', '\n'.join(questions) + '\n'),
                           ('prompt_comparison', '\n'.join(comparison) + '\n'), ('review', review)]:
        outputs[BATCH / f'{name}.md'] = markdown.encode()
        outputs[BATCH / f'{name}.html'] = parent.html_document(markdown, '中性题面对照 · ' + name)
    source_files = [SPEC, Path(__file__).resolve(), BATCH / 'README.md',
                    PARENT / 'manifest.json', PARENT / 'prompts.jsonl',
                    ROOT / 'scripts/build/build_edu_last_exam_scenario_v1.py']
    manifest = {
        'schema_version': spec['schema_version'], 'status': 'author_offline_validated_candidate',
        'package_count': len(items), 'prompt_count': len(rows), 'image_prompt_count': spec['image_prompt_count'],
        'parent_prompt_sha256': spec['parent_prompt_sha256'], 'parent_manifest_sha256': spec['parent_manifest_sha256'],
        'intervention': spec['intervention'], 'baseline_run': spec['baseline_run'],
        'human_review': 'pending', 'model_evaluation': 'tracked_in_separate_run_artifacts',
        'difficulty': 'not_measured', 'canonical': False, 'frozen': False, 'real_multiturn': False,
        'source_sha256': {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in source_files},
        'asset_sha256': {a: sha(outputs[BATCH / a]) for a in assets},
        'export_sha256': {str(p.relative_to(BATCH)): sha(content) for p, content in sorted(outputs.items())},
        'offline_checks': checks, 'conditions_preserved': True, 'gold_and_rubric_preserved': True,
        'comparison_limits': spec['comparison_limits']}
    outputs[BATCH / 'manifest.json'] = encoded(manifest)
    outputs[REPORT] = encoded({'status': manifest['status'], 'package_count': len(items), 'prompt_count': len(rows),
                              'parent_oracles': checks, 'conditions_preserved': True, 'stimulus_bytes_preserved': True,
                              'gold_and_rubric_preserved': True, 'human_review': 'pending', 'model_calls': 0,
                              'manifest_sha256': sha(outputs[BATCH / 'manifest.json'])})
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    spec, original, checks = load_context()
    outputs = build_outputs(spec, original, checks)
    if args.validate_only:
        stale = [str(p.relative_to(ROOT)) for p, data in outputs.items() if not p.is_file() or p.read_bytes() != data]
        require(not stale, 'Missing/stale neutral exports: ' + ', '.join(stale))
    else:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({'status': 'validated' if args.validate_only else 'exported', 'packages': spec['package_count'],
                      'prompts': spec['prompt_count'], 'parent_oracles': len(checks),
                      'conditions_preserved': True, 'stimulus_bytes_preserved': True, 'model_calls': 0}))


if __name__ == '__main__':
    main()
