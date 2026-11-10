"""Protect the instruction-only contrast against hidden stimulus/gold changes."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module('neutral_builder', 'scripts/build/build_edu_last_exam_scenario_neutral.py')
trial = module('neutral_trial', 'scripts/experiments/run_edu_last_exam_challenge_v2.py')


class NeutralContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec, cls.original, cls.checks = builder.load_context()

    def test_export_keeps_original_assets_gold_and_within_package_controls(self):
        outputs = builder.build_outputs(self.spec, self.original, self.checks)
        for path, data in outputs.items():
            self.assertEqual(path.read_bytes(), data, str(path))
        for item in self.original:
            name = 'reference/' + item['item_id'] + '.json'
            self.assertEqual((builder.BATCH / name).read_bytes(), (builder.PARENT / name).read_bytes())
            for prompt in item['prompts']:
                for asset in prompt['assets']:
                    self.assertEqual((builder.BATCH / asset).read_bytes(), (builder.PARENT / asset).read_bytes())

    def test_missing_necessary_circuit_or_assistance_conditions_is_rejected(self):
        for ident, fragment in [('ELE-S02-002', 'V3−V2=25I'),
                                ('ELE-S02-002', '相位误差≤0.1°'),
                                ('ELE-S03-001', 'help=unknown表示援助信息缺失')]:
            with self.subTest(fragment=fragment):
                items = builder.derive(self.original, self.spec)
                item = next(i for i in items if i['item_id'] == ident)
                item['prompts'][0]['user_prompt'] = item['prompts'][0]['user_prompt'].replace(fragment, '')
                with self.assertRaisesRegex(ValueError, 'Missing necessary condition'):
                    builder.validate_intervention(self.original, items, self.spec)

    def test_answer_or_attachment_change_is_rejected(self):
        items = builder.derive(self.original, self.spec)
        items[0]['gold']['per_prompt']['a']['answer'] = 25
        with self.assertRaisesRegex(ValueError, 'Non-prompt item data changed'):
            builder.validate_intervention(self.original, items, self.spec)
        items = builder.derive(self.original, self.spec)
        items[0]['prompts'][0]['assets'] = ['reference/ELE-S01-001.json']
        with self.assertRaisesRegex(ValueError, 'Asset, identity or interaction mode changed'):
            builder.validate_intervention(self.original, items, self.spec)

    def test_direct_instruction_cannot_be_reintroduced(self):
        items = builder.derive(self.original, self.spec)
        item = next(i for i in items if i['item_id'] == 'ELE-S01-001')
        item['prompts'][0]['user_prompt'] += '不要仅凭解法与参考稿不同扣分。'
        with self.assertRaisesRegex(ValueError, 'Removed instruction reintroduced'):
            builder.validate_intervention(self.original, items, self.spec)

    def test_delivery_keeps_pairing_and_does_not_send_control_or_gold(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(trial, 'BATCH', builder.BATCH):
            tasks, manifest = trial.prepare(Path(temp), 'GLM-5.3-Flash', trial.ENDPOINT)
            self.assertEqual((len(tasks), manifest['total_packages']), (12, 5))
            self.assertEqual(sum(isinstance(t['payload']['messages'][1]['content'], list) for t in tasks), 2)
            for task in tasks:
                self.assertNotIn('max_tokens', task['payload'])
                text = json.dumps(task['payload'], ensure_ascii=False)
                for forbidden in ('removed_instruction_fragments', 'critical_errors', 'reference_is_valid', 'prompt_comparison'):
                    self.assertNotIn(forbidden, text)
                self.assertEqual(task['payload']['messages'][0]['content'], self.spec['system_prompt'])


if __name__ == '__main__':
    unittest.main()
