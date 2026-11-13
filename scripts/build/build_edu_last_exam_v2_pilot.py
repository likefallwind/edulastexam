#!/usr/bin/env python3
"""Validate and export mechanism-driven V2 batches, offline only."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path, PurePosixPath
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage.core import digest
from scripts.build.build_edu_last_exam_full_coverage import build
from scripts.build.build_edu_last_exam_mechanism_generation import read_json, validate_blueprints

DATA = ROOT / "data/edu_last_exam_v2_pilot/protocol.json"
BATCH = ROOT / "private/edu_last_exam_v2_pilot"


def local_evidence_path(value, root=ROOT, must_exist=True):
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe evidence path: {value}")
    path = root / str(relative)
    if must_exist and not path.is_file():
        raise ValueError(f"Missing local evidence: {relative}")
    return path


def mechanism_index(protocol, root=ROOT):
    generation_protocol_path = local_evidence_path(protocol["mechanism_generation_protocol"], root)
    generation_protocol = read_json(generation_protocol_path)
    validated = validate_blueprints(generation_protocol, root=root)
    return {
        row["direction_id"]: row["mechanism_id"]
        for row in validated["blueprints"]["directions"]
    }


def validate_cards(protocol, batch=None, root=ROOT):
    batch = Path(batch) if batch is not None else root / protocol["batch"]
    cards = [json.loads(line) for line in (batch / "cards.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    authored = [json.loads(path.read_text(encoding="utf-8")) for path in (batch / "authored").glob(protocol["item_glob"])]
    card_map = {card["item_id"]: card for card in cards}
    item_map = {item["item_id"]: item for item in authored}
    if len(card_map) != len(cards) or set(card_map) != set(protocol["expected_item_ids"]):
        raise ValueError("V2 cards do not match protocol item IDs")
    if set(item_map) != set(card_map):
        raise ValueError("V2 cards/authored mismatch")

    mechanisms = mechanism_index(protocol, root=root)
    evidence_cases = []
    evidence_hashes = {}
    items_with_v1_failures = 0
    reviews = None
    for item_id, card in card_map.items():
        item = item_map[item_id]
        if card["direction_id"] != item["direction_id"] or card["title"] != item["title"]:
            raise ValueError(f"{item_id}: card identity mismatch")
        if card.get("generation_batch_id") != protocol.get("generation_batch_id"):
            raise ValueError(f"{item_id}: generation batch identity mismatch")
        direction_id = card["direction_id"]
        if card.get("mechanism_ref") != mechanisms.get(direction_id):
            raise ValueError(f"{item_id}: card does not bind the direction mechanism blueprint")
        expected_card = f"data/edu_last_exam_source_fidelity_v1/directions/{direction_id}.json"
        if card.get("source_card") != expected_card:
            raise ValueError(f"{item_id}: source card mismatch")
        local_evidence_path(expected_card, root)
        if not card.get("controls"):
            raise ValueError(f"{item_id}: planned controls required")
        if set(card["controls"]) != {prompt["prompt_id"] for prompt in item["prompts"]}:
            raise ValueError(f"{item_id}: card controls do not cover authored variants")

        v1_evidence = card.get("v1_evidence", [])
        if not isinstance(v1_evidence, list):
            raise ValueError(f"{item_id}: v1_evidence must be an array")
        if v1_evidence:
            items_with_v1_failures += 1
            if reviews is None:
                reviews_path = root / "reports/full_coverage_v1/glm53flash_20261110_codex_review/case_reviews.jsonl"
                reviews = {
                    row["case_id"]: row
                    for row in (json.loads(line) for line in reviews_path.read_text(encoding="utf-8").splitlines() if line.strip())
                }
        for evidence in v1_evidence:
            path = local_evidence_path(evidence["local_path"], root)
            evidence_hashes[evidence["local_path"]] = digest(path.read_bytes())
            case_id = evidence["case_id"]
            if case_id not in reviews or reviews[case_id].get("verdict") != "fail":
                raise ValueError(f"{item_id}: {case_id} is not a reviewed V1 failure")
            evidence_cases.append(case_id)
        for evidence in item["source_evidence"]:
            if "local_path" in evidence:
                path = local_evidence_path(evidence["local_path"], root)
                evidence_hashes[evidence["local_path"]] = digest(path.read_bytes())
        if item["status"] != {"stage": "authored_candidate", "human_review": "pending", "frozen": False, "model_evaluation": "not_run"}:
            raise ValueError(f"{item_id}: invalid V2 authoring-time candidate status")
    return evidence_cases, evidence_hashes, items_with_v1_failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default=str(DATA), help="V2 batch protocol path")
    parser.add_argument("--validate-only", action="store_true", help="Do not write; fail on missing or stale exports")
    args = parser.parse_args()
    protocol_path = Path(args.protocol).resolve()
    protocol = read_json(protocol_path)
    batch = local_evidence_path(protocol["batch"], ROOT, must_exist=False)
    if not batch.is_dir():
        raise ValueError(f"Missing V2 batch: {protocol['batch']}")
    evidence_cases, evidence_hashes, items_with_v1_failures = validate_cards(protocol, batch=batch)
    protocol = copy.deepcopy(protocol)
    protocol["validation_extra"]["v1_failure_evidence"] = {
        "required_for_all_items": False,
        "items_with_v1_failure_evidence": items_with_v1_failures,
        "references": len(evidence_cases),
        "unique_cases": len(set(evidence_cases)),
        "all_reviewed_verdicts": "fail" if evidence_cases else "not_applicable",
    }
    protocol["manifest_extra"]["v1_evidence_sha256"] = evidence_hashes
    build(batch, validate_only=args.validate_only, check=args.validate_only, protocol=protocol)


if __name__ == "__main__":
    main()
