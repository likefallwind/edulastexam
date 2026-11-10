"""Offline checks for repaired gold, counterfactual validity, and safe delivery."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_module('scenario_builder', 'scripts/build/build_edu_last_exam_scenario_v1.py')
trial = load_module('scenario_trial', 'scripts/experiments/run_edu_last_exam_challenge_v2.py')


class ScenarioAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.items = builder.load_items()
        self.sources = builder.read(builder.DATA / 'source_manifest.json')

    def test_export_matches_sources_and_independent_oracles(self):
        builder.validate_contract(self.items, self.sources)
        checks = builder.check_oracles(self.items)
        self.assertEqual(len(checks), 5)
        for path, expected in builder.render_outputs(self.items, self.sources, checks).items():
            self.assertEqual(path.read_bytes(), expected, str(path))

    def test_upstream_bad_gold_cannot_be_reintroduced(self):
        for ident, bad_answer, bad_step in [('ELE-S01-001', 25, 'S3'), ('ELE-S01-002', 15, 'S4')]:
            with self.subTest(ident=ident):
                items = copy.deepcopy(self.items)
                gold = next(i for i in items if i['item_id'] == ident)['gold']['per_prompt']['a']
                gold['answer'] = bad_answer
                gold['first_invalid_step'] = bad_step
                with self.assertRaises(ValueError):
                    builder.check_oracles(items)

    def test_reference_and_curator_metadata_cannot_be_exported_as_prompts(self):
        items = copy.deepcopy(self.items)
        items[0]['prompts'][0]['gold'] = {'SECRET': 'must not be delivered'}
        with self.assertRaisesRegex(ValueError, 'export fields'):
            builder.validate_contract(items, self.sources)
        items = copy.deepcopy(self.items)
        items[0]['prompts'][0]['assets'] = ['reference/ELE-S01-001.json']
        with self.assertRaisesRegex(ValueError, 'Unsafe asset'):
            builder.validate_contract(items, self.sources)
        with self.assertRaisesRegex(ValueError, 'Unsafe asset'):
            builder.safe_asset('stimuli/../reference/ELE-S01-001.json')

    def test_assistance_contrast_rejects_an_unrelated_response_change(self):
        with tempfile.TemporaryDirectory() as temp:
            batch = Path(temp)
            shutil.copytree(builder.BATCH / 'stimuli/S03_001', batch / 'stimuli/S03_001')
            target = batch / 'stimuli/S03_001/history_b.json'
            data = json.loads(target.read_text())
            data['records'][0]['student_response'] = 'changed response'
            target.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'other than assistance'):
                builder.check_oracles(self.items, batch)

    def test_image_identity_is_required_and_no_transcript_fallback_is_silent(self):
        entry = copy.deepcopy(self.sources['images'][0])
        entry['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Image identity mismatch'):
            builder.image_bytes(entry)
        with patch.object(builder, 'source_image_path', return_value=Path('/nonexistent/ele-image.png')):
            with self.assertRaisesRegex(ValueError, 'no proxy image'):
                builder.image_bytes(self.sources['images'][0])

    def test_existing_runner_delivers_images_without_gold_or_token_cap(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(trial, 'BATCH', builder.BATCH):
            tasks, manifest = trial.prepare(Path(temp), 'UNSELECTED-PANEL', 'https://example.invalid')
            self.assertEqual(manifest['total_packages'], 5)
            self.assertEqual(len(tasks), 12)
            image_count = 0
            for task in tasks:
                payload = task['payload']
                self.assertNotIn('max_tokens', payload)
                body = payload['messages'][1]['content']
                serialized = json.dumps(payload, ensure_ascii=False)
                for forbidden in ['critical_errors', 'reference_is_valid', 'upstream_incorrect_index_zero_based', 'acceptable_alternatives']:
                    self.assertNotIn(forbidden, serialized)
                if isinstance(body, list):
                    image_count += sum(p['type'] == 'image_url' for p in body)
                    self.assertNotIn('transcript.md', body[0]['text'])
            self.assertEqual(image_count, 2)


if __name__ == '__main__':
    unittest.main()
