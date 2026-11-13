"""Offline contract tests for the 37-direction mechanism-generation pipeline."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.build import build_edu_last_exam_mechanism_generation as generation

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "data/edu_last_exam_mechanism_generation_v1/protocol.json"
PROTOCOL = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
BLUEPRINTS = json.loads((ROOT / PROTOCOL["blueprints"]).read_text(encoding="utf-8"))


def test_all_37_directions_have_mechanism_driven_family_blueprints():
    validated = generation.validate_blueprints(PROTOCOL)
    rows = validated["blueprints"]["directions"]
    assert {row["direction_id"] for row in rows} == {f"{number:02d}" for number in range(1, 38)}
    assert all(row["mechanism_analysis"]["failure_conditions"] for row in rows)
    assert all(row["family_plans"] for row in rows)
    assert PROTOCOL["historical_failure_required"] is False


def test_historical_model_failures_are_not_an_entry_requirement():
    candidate = copy.deepcopy(BLUEPRINTS)
    for row in candidate["directions"]:
        row["historical_examples"] = []
    validated = generation.validate_blueprints(PROTOCOL, blueprint_data=candidate)
    assert len(validated["blueprints"]["directions"]) == 37


def test_missing_direction_is_rejected():
    candidate = copy.deepcopy(BLUEPRINTS)
    candidate["directions"] = candidate["directions"][1:]
    with pytest.raises(ValueError, match="01-37"):
        generation.validate_blueprints(PROTOCOL, blueprint_data=candidate)


def test_missing_generation_conditions_are_rejected():
    candidate = copy.deepcopy(BLUEPRINTS)
    candidate["directions"][0]["required_conditions"] = []
    with pytest.raises(ValueError, match="required_conditions"):
        generation.validate_blueprints(PROTOCOL, blueprint_data=candidate)


def test_duplicate_family_ids_are_rejected():
    candidate = copy.deepcopy(BLUEPRINTS)
    duplicate = copy.deepcopy(candidate["directions"][0]["family_plans"][0])
    candidate["directions"][0]["family_plans"].append(duplicate)
    with pytest.raises(ValueError, match="Duplicate family ID"):
        generation.validate_blueprints(PROTOCOL, blueprint_data=candidate)


def test_blocked_family_must_expose_its_blockers():
    candidate = copy.deepcopy(BLUEPRINTS)
    family = candidate["directions"][0]["family_plans"][0]
    family["authoring_status"] = "blocked"
    family["blockers"] = []
    with pytest.raises(ValueError, match="must name blockers"):
        generation.validate_blueprints(PROTOCOL, blueprint_data=candidate)


def test_builder_exports_and_checks_queue_without_model_calls(tmp_path):
    summary = generation.build(PROTOCOL, output_root=tmp_path)
    assert summary["status"] == "built"
    report_dir = tmp_path / PROTOCOL["report_directory"]
    queue = json.loads((report_dir / "direction_generation_queue.json").read_text(encoding="utf-8"))
    coverage = json.loads((report_dir / "coverage.json").read_text(encoding="utf-8"))
    assert coverage["blueprint_coverage"] == {"covered": 37, "total": 37}
    assert queue["ordering"] == "direction_id_then_family_id_not_model_failure_rank"
    assert all(row["historical_failure_required"] is False for row in queue["families"])
    assert generation.build(PROTOCOL, output_root=tmp_path, validate_only=True)["status"] == "validated"

    (report_dir / "direction_generation_queue.md").write_text("STALE", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing/stale"):
        generation.build(PROTOCOL, output_root=tmp_path, validate_only=True)
    assert (report_dir / "direction_generation_queue.md").read_text(encoding="utf-8") == "STALE"
