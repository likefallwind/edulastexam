"""Deterministic checks for the reviewed v1 selection and its revisions."""
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("edu_last_exam_v1_builder", ROOT / "scripts/build/build_edu_last_exam_v1.py")
BUILDER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILDER)


class EduLastExamV1Tests(unittest.TestCase):
    def test_manifest_selection_and_assets(self):
        manifest = json.loads((ROOT / "private/edu_last_exam_v1/manifest.json").read_text(encoding="utf-8"))
        expected = ["ELE-C2-01", "ELE-C2-03", "ELE-C2-09", "ELE-C2-10", "ELE-C2-12", "ELE-C2-13", "ELE-C2-16", "ELE-C2-20"]
        self.assertEqual(manifest["status"], "test_release_candidate")
        self.assertEqual(manifest["item_ids"], expected)
        self.assertEqual(manifest["package_count"], 8)
        self.assertEqual(manifest["prompt_count"], 11)
        rows = [json.loads(line) for line in (ROOT / "private/edu_last_exam_v1/items.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([row["item_id"] for row in rows], expected)
        for row in rows:
            for prompt in row["prompts"]:
                for asset in prompt["assets"]:
                    self.assertTrue((ROOT / "private/edu_last_exam_v1" / asset).is_file(), asset)

    def test_audit_revisions_are_present(self):
        rows = [json.loads(line) for line in (ROOT / "private/edu_last_exam_v1/items.jsonl").read_text(encoding="utf-8").splitlines()]
        by_id = {row["item_id"]: row for row in rows}
        c10 = by_id["ELE-C2-10"]["gold"]["per_prompt"]["base"]["reference_answer"]["quantitative"]
        self.assertEqual(c10["max_difference_error_g"], "0.4")
        self.assertIn("两次读数各自的误差界为±0.2g", c10["error_explanation"])
        c12 = by_id["ELE-C2-12"]["gold"]["per_prompt"]["base"]["reference_answer"]["current_state"]
        for record_id in ("R03", "R14", "R23", "R38", "R05", "R40"):
            self.assertIn(record_id, c12)
        c16 = by_id["ELE-C2-16"]["rubric"]["criteria"]
        self.assertTrue(all("交付3" not in criterion["description"] for criterion in c16))
        c20 = by_id["ELE-C2-20"]
        self.assertIn("9.9326V", c20["prompts"][0]["user_prompt"])
        self.assertIn("中间采样", c20["rubric"]["criteria"][2]["description"])


if __name__ == "__main__":
    unittest.main()
