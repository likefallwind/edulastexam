#!/usr/bin/env python3
"""Build a source-audited candidate manifest; original raw data remains private."""
from collections import Counter
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.source_fidelity.core import AUDIT_REL, BATCH_REL, digest, load, report


def build(root=ROOT, check=False, validate_only=False, allow_partial=False):
    audits, tasks, validations = load(root, require_all=not allow_partial)
    manifest = {
        "protocol": "source_fidelity_v1", "direction_count": len(audits), "case_count": len(tasks),
        "prediction_eligible_cases": sum(t.get("execution", {}).get("eligible") is not False for t in tasks),
        "original_condition_unavailable_cases": [t["case_id"] for t in tasks if t.get("execution", {}).get("eligible") is False],
        "direction_states": dict(Counter(a["status"] for a in audits)),
        "origins": dict(Counter(t["origin"] for t in tasks)),
        "native_scoring_modes": dict(Counter(t["scoring"]["mode"] for t in tasks)),
        "task_sha256": {t["case_id"]: digest(t) for t in tasks},
        "audit_sha256": {a["direction_id"]: digest(a) for a in audits},
        "protocol_sha256": digest((root / AUDIT_REL / "protocol.md").read_bytes()),
        "author": "Codex", "tested_panel": ["GLM-5.3-Flash"], "human_review": "pending",
        "difficulty": "not_established", "canonical": False, "cross_direction_total_score": False,
        "offline_checks": validations,
    }
    prediction_rows = [{k: t[k] for k in ("case_id", "direction_ids", "prediction")} | {
        "assets": [a for a in t.get("assets", []) if a["role"] == "prediction"]} for t in tasks]
    exports = {
        root / BATCH_REL / "items.jsonl": ''.join(json.dumps(t, ensure_ascii=False) + "\n" for t in tasks),
        root / BATCH_REL / "prompts.jsonl": ''.join(json.dumps(t, ensure_ascii=False) + "\n" for t in prediction_rows),
        root / BATCH_REL / "manifest.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        root / "reports/source_fidelity_v1/source_audit.html": report(audits, tasks, {k: v for k, v in manifest.items() if k not in {"task_sha256", "audit_sha256", "offline_checks"}}),
        root / "reports/source_fidelity_v1/offline_validation.json": json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
    }
    for path, content in exports.items():
        if check:
            if not path.exists() or path.read_text() != content:
                raise ValueError(f"Missing or stale export: {path}")
        elif not validate_only:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(json.dumps({k: v for k, v in manifest.items() if k not in {"task_sha256", "audit_sha256", "offline_checks"}}, ensure_ascii=False))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    build(check=args.check, validate_only=args.validate_only, allow_partial=args.allow_partial)
