#!/usr/bin/env python3
"""Validate 37-direction mechanism blueprints and export the generation queue."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.full_coverage.core import digest

DATA = ROOT / "data/edu_last_exam_mechanism_generation_v1/protocol.json"
FAMILY_ID = re.compile(r"MG-(\d{2})-[A-Z]$")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def local_path(root, value, must_exist=True):
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Unsafe local path: {value}")
    path = root / str(relative)
    if must_exist and not path.is_file():
        raise ValueError(f"Missing local file: {relative}")
    return path


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: non-empty text required")


def require_list(value, label, minimum=1):
    if not isinstance(value, list) or len(value) < minimum:
        raise ValueError(f"{label}: at least {minimum} entries required")
    if not all(isinstance(entry, str) and entry.strip() for entry in value):
        raise ValueError(f"{label}: entries must be non-empty strings")


def validate_blueprints(protocol, root=ROOT, blueprint_data=None):
    index_path = local_path(root, protocol["direction_index"])
    map_path = local_path(root, protocol["mechanism_map"])
    route_path = local_path(root, protocol["route_matrix"])
    index = read_json(index_path)
    mechanism_map = read_json(map_path)
    route_matrix = read_json(route_path)
    expected = protocol["expected_direction_ids"]
    if len(expected) != 37 or len(set(expected)) != 37:
        raise ValueError("Protocol must declare 37 unique direction IDs")

    inventory_path = local_path(root, index["source_path"])
    if digest(inventory_path.read_bytes()) != index["source_sha256"]:
        raise ValueError("Direction index inventory hash is stale")
    index_rows = {row["direction_id"]: row for row in index["directions"]}
    map_rows = {row["direction_id"]: row for row in mechanism_map["directions"]}
    route_rows = {row["direction_id"]: row for row in route_matrix["directions"]}
    for label, rows in (("direction index", index_rows), ("mechanism map", map_rows), ("route matrix", route_rows)):
        if set(rows) != set(expected) or len(rows) != 37:
            raise ValueError(f"{label} does not preserve the 37-direction universe")

    blueprint_path = local_path(root, protocol["blueprints"], must_exist=blueprint_data is None)
    data = blueprint_data if blueprint_data is not None else read_json(blueprint_path)
    rows = data.get("directions") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise ValueError("Blueprint file must contain a directions array")
    row_map = {}
    for row in rows:
        direction_id = row.get("direction_id")
        if direction_id in row_map:
            raise ValueError(f"Duplicate blueprint direction: {direction_id}")
        row_map[direction_id] = row
    if set(row_map) != set(expected) or len(rows) != 37:
        raise ValueError("Blueprints must contain each of 01-37 exactly once")

    source_hashes = {
        protocol["direction_index"]: digest(index_path.read_bytes()),
        protocol["mechanism_map"]: digest(map_path.read_bytes()),
        protocol["route_matrix"]: digest(route_path.read_bytes()),
        index["source_path"]: digest(inventory_path.read_bytes()),
    }
    family_ids = set()
    mechanism_ids = set()
    allowed_views = set(protocol["allowed_task_views"])
    allowed_statuses = set(protocol["allowed_authoring_status"])
    allowed_roles = set(protocol["allowed_variant_roles"])
    allowed_evidence = set(protocol["allowed_evidence_types"])

    for direction_id in expected:
        row = row_map[direction_id]
        prefix = f"Direction {direction_id}"
        if row.get("mechanism_id") != f"M{direction_id}":
            raise ValueError(f"{prefix}: stable mechanism ID must be M{direction_id}")
        if row["mechanism_id"] in mechanism_ids:
            raise ValueError(f"Duplicate mechanism ID: {row['mechanism_id']}")
        mechanism_ids.add(row["mechanism_id"])
        for field in ("task_demand", "education_consequence"):
            require_text(row.get(field), f"{prefix}.{field}")

        analysis = row.get("mechanism_analysis")
        if not isinstance(analysis, dict):
            raise ValueError(f"{prefix}: mechanism_analysis required")
        for field in ("shortcut", "why_surface_quality_is_insufficient", "evidence_note"):
            require_text(analysis.get(field), f"{prefix}.mechanism_analysis.{field}")
        require_list(analysis.get("failure_conditions"), f"{prefix}.mechanism_analysis.failure_conditions", 2)
        evidence_types = analysis.get("evidence_types")
        require_list(evidence_types, f"{prefix}.mechanism_analysis.evidence_types")
        if not set(evidence_types) <= allowed_evidence:
            raise ValueError(f"{prefix}: unsupported mechanism evidence type")

        for field, minimum in (("required_conditions", 3), ("observable_signals", 2), ("critical_errors", 2), ("material_axes", 2), ("context_axes", 2)):
            require_list(row.get(field), f"{prefix}.{field}", minimum)
        related = row.get("related_direction_ids")
        if not isinstance(related, list) or not set(related) <= set(expected) or direction_id in related:
            raise ValueError(f"{prefix}: invalid related_direction_ids")

        expected_card = protocol["source_card_pattern"].format(direction_id=direction_id)
        if map_rows[direction_id]["source_card"] != expected_card:
            raise ValueError(f"{prefix}: mechanism map source card mismatch")
        card_path = local_path(root, expected_card)
        source_hashes[expected_card] = digest(card_path.read_bytes())
        card = read_json(card_path)
        if card.get("direction_id") != direction_id:
            raise ValueError(f"{prefix}: source card identity mismatch")

        families = row.get("family_plans")
        if not isinstance(families, list) or not families:
            raise ValueError(f"{prefix}: at least one family plan required")
        for family in families:
            family_id = family.get("family_id", "")
            match = FAMILY_ID.fullmatch(family_id)
            if not match or match.group(1) != direction_id:
                raise ValueError(f"{prefix}: invalid family ID {family_id!r}")
            if family_id in family_ids:
                raise ValueError(f"Duplicate family ID: {family_id}")
            family_ids.add(family_id)
            for field in ("title", "generation_spec", "oracle"):
                require_text(family.get(field), f"{family_id}.{field}")
            if family.get("task_view") not in allowed_views:
                raise ValueError(f"{family_id}: unsupported task_view")
            status = family.get("authoring_status")
            if status not in allowed_statuses:
                raise ValueError(f"{family_id}: unsupported authoring_status")
            blockers = family.get("blockers")
            if not isinstance(blockers, list):
                raise ValueError(f"{family_id}: blockers array required")
            if status == "blocked" and not blockers:
                raise ValueError(f"{family_id}: blocked plan must name blockers")
            variants = family.get("variant_plan")
            if not isinstance(variants, list) or len(variants) < 2:
                raise ValueError(f"{family_id}: at least two dependent variants required")
            variant_ids = set()
            roles = set()
            for variant in variants:
                variant_id = variant.get("variant_id")
                require_text(variant_id, f"{family_id}.variant_id")
                if variant_id in variant_ids:
                    raise ValueError(f"{family_id}: duplicate variant {variant_id}")
                variant_ids.add(variant_id)
                role = variant.get("role")
                if role not in allowed_roles:
                    raise ValueError(f"{family_id}.{variant_id}: unsupported role")
                roles.add(role)
                require_list(variant.get("changed_factors"), f"{family_id}.{variant_id}.changed_factors")
                require_list(variant.get("invariant_factors"), f"{family_id}.{variant_id}.invariant_factors")
                require_text(variant.get("expected_difference"), f"{family_id}.{variant_id}.expected_difference")
            if not roles & {"target", "transfer"} or not roles & {"correct_control", "counterfactual", "no_op"}:
                raise ValueError(f"{family_id}: target/transfer and a control or counterfactual are required")

        limits = row.get("oracle_and_limits")
        if not isinstance(limits, dict):
            raise ValueError(f"{prefix}: oracle_and_limits required")
        require_list(limits.get("scoring"), f"{prefix}.oracle_and_limits.scoring")
        require_list(limits.get("unmeasured_subclaims"), f"{prefix}.oracle_and_limits.unmeasured_subclaims")
        if not isinstance(limits.get("blockers"), list):
            raise ValueError(f"{prefix}: oracle_and_limits.blockers array required")
        if any(family["authoring_status"] == "blocked" for family in families) and not limits["blockers"]:
            raise ValueError(f"{prefix}: blocked families must be visible in oracle_and_limits")

        examples = row.get("historical_examples", [])
        if not isinstance(examples, list):
            raise ValueError(f"{prefix}: historical_examples must be an array")
        for example in examples:
            if not {"case_id", "role", "local_path"} <= set(example):
                raise ValueError(f"{prefix}: incomplete historical example")
            if example["role"] not in {"support", "refutation", "control", "review"}:
                raise ValueError(f"{prefix}: invalid historical evidence role")
            local_path(root, example["local_path"])

    if blueprint_data is None:
        source_hashes[protocol["blueprints"]] = digest(blueprint_path.read_bytes())
    return {
        "blueprints": data,
        "index_rows": index_rows,
        "map_rows": map_rows,
        "route_rows": route_rows,
        "source_hashes": source_hashes,
    }


def render_documents(protocol, validated):
    rows = validated["blueprints"]["directions"]
    by_direction = {row["direction_id"]: row for row in rows}
    queue_rows = []
    coverage_rows = []
    for direction_id in protocol["expected_direction_ids"]:
        row = by_direction[direction_id]
        families = row["family_plans"]
        ready = [family for family in families if family["authoring_status"] == "ready_to_author"]
        blocked = [family for family in families if family["authoring_status"] == "blocked"]
        blockers = list(dict.fromkeys(
            row["oracle_and_limits"]["blockers"]
            + [blocker for family in families for blocker in family["blockers"]]
        ))
        coverage_rows.append({
            "direction_id": direction_id,
            "original_title": validated["index_rows"][direction_id]["original_title"],
            "mechanism_id": row["mechanism_id"],
            "blueprint_status": "ready",
            "planned_families": len(families),
            "ready_to_author_families": len(ready),
            "blocked_families": len(blocked),
            "coverage_stage": "blueprint_only",
            "authored_reviewed_tested_frozen": "tracked_in_item_batches",
            "blockers": blockers,
        })
        for family in families:
            queue_rows.append({
                "direction_id": direction_id,
                "mechanism_id": row["mechanism_id"],
                "family_id": family["family_id"],
                "title": family["title"],
                "task_view": family["task_view"],
                "authoring_status": family["authoring_status"],
                "generation_spec": family["generation_spec"],
                "variant_ids": [variant["variant_id"] for variant in family["variant_plan"]],
                "oracle": family["oracle"],
                "blockers": family["blockers"],
                "historical_failure_required": False,
            })

    fully_blocked = [row["direction_id"] for row in coverage_rows if row["ready_to_author_families"] == 0]
    coverage = {
        "schema_version": "edu_last_exam_mechanism_generation_coverage_v1",
        "status": "blueprints_validated_not_frozen",
        "blueprint_coverage": {"covered": len(coverage_rows), "total": 37},
        "planned_independent_families": len(queue_rows),
        "planned_dependent_variants": sum(len(row["variant_ids"]) for row in queue_rows),
        "directions_with_ready_to_author_family": sum(row["ready_to_author_families"] > 0 for row in coverage_rows),
        "fully_blocked_directions": fully_blocked,
        "authored_executable_reviewed_tested_frozen_coverage": "not_inferred_from_blueprints",
        "historical_failure_required": False,
        "source_hashes": validated["source_hashes"],
        "directions": coverage_rows,
    }
    queue = {
        "schema_version": "edu_last_exam_mechanism_generation_queue_v1",
        "status": "candidate_generation_queue",
        "ordering": "direction_id_then_family_id_not_model_failure_rank",
        "historical_failure_required": False,
        "direction_quota": protocol["direction_quota"],
        "coverage_claim": protocol["coverage_claim"],
        "families": queue_rows,
    }

    lines = [
        "# Edu Last Exam 37 方向机制驱动生成队列",
        "",
        "本文件由蓝图构建器生成。37/37 表示机制蓝图覆盖，不表示 37 个方向均已有可运行题目或冻结结论。历史模型失败不是造数准入条件。",
        "",
        f"计划题族：{len(queue_rows)}；依赖版本：{coverage['planned_dependent_variants']}；完全阻塞方向：{len(fully_blocked)}。",
        "",
        "|方向|原始构念|机制捷径|题族|状态|阻塞/边界|",
        "|---|---|---|---|---|---|",
    ]
    for coverage_row, queue_row_group in zip(coverage_rows, [by_direction[row["direction_id"]]["family_plans"] for row in coverage_rows]):
        direction_id = coverage_row["direction_id"]
        blueprint = by_direction[direction_id]
        families = "<br>".join(f"{family['family_id']} {family['title']}" for family in queue_row_group)
        status = "ready_to_author" if coverage_row["ready_to_author_families"] else "blocked"
        limits = "；".join(blueprint["oracle_and_limits"]["blockers"] or blueprint["oracle_and_limits"]["unmeasured_subclaims"][:1])
        cells = [
            direction_id,
            coverage_row["original_title"],
            blueprint["mechanism_analysis"]["shortcut"],
            families,
            status,
            limits,
        ]
        lines.append("|" + "|".join(str(cell).replace("|", "\\|").replace("\n", " ") for cell in cells) + "|")
    lines.append("")
    return {
        "direction_generation_queue.json": json.dumps(queue, ensure_ascii=False, indent=2) + "\n",
        "direction_generation_queue.md": "\n".join(lines),
        "coverage.json": json.dumps(coverage, ensure_ascii=False, indent=2) + "\n",
    }


def build(protocol, root=ROOT, output_root=None, validate_only=False):
    validated = validate_blueprints(protocol, root=root)
    documents = render_documents(protocol, validated)
    output_root = root if output_root is None else output_root
    report_relative = PurePosixPath(protocol["report_directory"])
    if report_relative.is_absolute() or ".." in report_relative.parts:
        raise ValueError("Unsafe report directory")
    report_dir = output_root / str(report_relative)
    stale = []
    for name, content in documents.items():
        path = report_dir / name
        if validate_only:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            report_dir.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        raise ValueError("Missing/stale mechanism-generation exports: " + ", ".join(sorted(stale)))
    return {
        "status": "validated" if validate_only else "built",
        "blueprint_directions": 37,
        "planned_families": sum(len(row["family_plans"]) for row in validated["blueprints"]["directions"]),
        "historical_failure_required": False,
        "report_directory": str(report_dir),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", default=str(DATA), help="Mechanism-generation protocol path")
    parser.add_argument("--validate-only", action="store_true", help="Do not write; fail on missing or stale exports")
    args = parser.parse_args()
    protocol_path = Path(args.protocol).resolve()
    protocol = read_json(protocol_path)
    summary = build(protocol, validate_only=args.validate_only)
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
