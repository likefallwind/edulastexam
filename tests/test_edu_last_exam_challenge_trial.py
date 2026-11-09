"""Offline safeguards for the noncanonical challenge trial runner."""
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("challenge_trial", ROOT / "scripts/experiments/run_edu_last_exam_challenge_v2.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


class TrialSafetyTests(unittest.TestCase):
    def test_attachment_delivery_and_reference_exclusion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            batch, output = root / "batch", root / "out"
            (batch / "stimuli/01").mkdir(parents=True)
            (batch / "reference/01").mkdir(parents=True)
            (batch / "stimuli/01/table.csv").write_text("x,y\n4,7\n")
            (batch / "stimuli/01/image.png").write_bytes(b"fake-image")
            (batch / "reference/01/gold.txt").write_text("SECRET_GOLD_NEVER_SEND")
            rows = [{"item_id": "T1", "prompt_id": "base", "interaction_mode": "single_turn", "system_prompt": "Teacher", "user_prompt": "Read data", "assets": ["stimuli/01/table.csv"]},
                    {"item_id": "T2", "prompt_id": "base", "interaction_mode": "single_turn", "system_prompt": "Teacher", "user_prompt": "Read image", "assets": ["stimuli/01/image.png"]}]
            (batch / "prompts.jsonl").write_text(''.join(json.dumps(r) + "\n" for r in rows))
            with patch.object(trial, "BATCH", batch):
                tasks, manifest = trial.prepare(output, "GLM-5.3", trial.ENDPOINT)
                self.assertIn("4,7", tasks[0]["payload"]["messages"][1]["content"])
                image_content = tasks[1]["payload"]["messages"][1]["content"]
                self.assertIsInstance(image_content, list)
                self.assertEqual(image_content[1]["type"], "image_url")
                self.assertTrue(image_content[1]["image_url"]["url"].startswith("data:image/png;base64,"))
                self.assertNotIn("SECRET_GOLD_NEVER_SEND", json.dumps(tasks))
                self.assertNotIn("max_tokens", tasks[0]["payload"])
                self.assertEqual((manifest["eligible_prompts"], manifest["unsupported_prompts"]), (2, 0))
                rows[0]["user_prompt"] = "Changed prompt"
                (batch / "prompts.jsonl").write_text(''.join(json.dumps(r) + "\n" for r in rows))
                with self.assertRaisesRegex(ValueError, "drift"):
                    trial.prepare(output, "GLM-5.3", trial.ENDPOINT)

    def test_gold_path_cannot_be_injected_as_asset(self):
        with tempfile.TemporaryDirectory() as temp:
            batch = Path(temp)
            row = {"item_id": "T", "prompt_id": "base", "assets": ["reference/01/gold.txt"]}
            (batch / "prompts.jsonl").write_text(json.dumps(row))
            with patch.object(trial, "BATCH", batch), self.assertRaisesRegex(ValueError, "Unsafe stimulus"):
                trial.prepare(batch / "out", "GLM-5.3", trial.ENDPOINT)

    def test_model_filename_is_not_a_write_path(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            result = trial.collect_artifacts("```html filename=../../escaped.html\nbad\n```\n```html filename=corrected.html\n<script>example()</script>\n```", output)
            self.assertEqual(result[0]["status"], "rejected_filename")
            self.assertEqual(result[1]["status"], "saved_not_executed")
            self.assertEqual(len(list(output.rglob("*.html"))), 1)

    def test_stream_error_is_not_silent_success(self):
        raw = io.BytesIO(b'data: {"error":{"message":"provider failure"}}\n\n')
        with self.assertRaisesRegex(RuntimeError, "stream error"):
            trial.read_sse_stream(trial.RecordedStream(raw, io.BytesIO()))

    def test_length_and_empty_are_not_generated(self):
        for text, finish, expected in [("answer", "length", "incomplete_output"), ("", "stop", "empty_response"), ("answer", "stop", "generated")]:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp:
                output = Path(temp)
                (output / "cases/T__base").mkdir(parents=True)
                task = {"case_id": "T__base", "item_id": "T", "prompt_id": "base", "request_sha256": "test", "interaction_mode": "single_turn", "payload": {"model": "GLM-5.3", "messages": [], "stream": True}}
                event = {"model": "GLM-5.3", "choices": [{"delta": {"content": text}, "finish_reason": finish}]}
                stream = io.BytesIO(("data: " + json.dumps(event) + "\n\ndata: [DONE]\n\n").encode())
                args = SimpleNamespace(retries=0, timeout=1, endpoint=trial.ENDPOINT, model="GLM-5.3")
                with patch.object(trial.urllib.request, "urlopen", return_value=stream):
                    result = trial.request_one(task, args, "test-only-key", output)
                self.assertEqual(result["status"], expected)
                self.assertEqual(result["returned_models"], ["GLM-5.3"])
                self.assertTrue(result["stream_done_seen"])
                first = (output / "cases/T__base/attempt_01.sse").read_bytes()
                with patch.object(trial.urllib.request, "urlopen", return_value=io.BytesIO(first)):
                    second = trial.request_one(task, args, "test-only-key", output)
                self.assertEqual(second["last_attempt_number"], 2)
                self.assertEqual((output / "cases/T__base/attempt_01.sse").read_bytes(), first)


if __name__ == "__main__":
    unittest.main()
