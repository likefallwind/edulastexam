#!/usr/bin/env python3
"""Validate the 37-direction implementation plan and render its HTML index.

--check verifies both source invariants and the generated report without writing.
This is a planning index, not an item builder or an evaluation runner.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

from render_edu_last_exam_research import STYLE


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/edu_last_exam_full_coverage_v1/implementation_matrix.json"
OUTPUT = ROOT / "reports/research/edu-last-exam-full-coverage-implementation-2026-11-10.html"


def local_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def link(path: Path, label: str) -> str:
    href = quote(os.path.relpath(path, OUTPUT.parent), safe="/")
    return f'<a href="{href}">{html.escape(label)}</a>'


def render() -> str:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    inventory = local_path(data["inventory_path"])
    titles = dict(re.findall(r"^### (\d{2})\. (.+)$", inventory.read_text(encoding="utf-8"), re.M))
    if hashlib.sha256(inventory.read_bytes()).hexdigest() != data["inventory_sha256"]:
        raise ValueError("Evidence inventory changed; review the implementation matrix first.")
    rows = data["rows"]
    expected = [f"{number:02}" for number in range(1, 38)]
    if [row["id"] for row in rows] != expected or data["coverage_count"] != 37:
        raise ValueError("The plan must cover each inventory entry 01–37 exactly once.")
    if data["status"] != "planning_only" or data["case_count"] is not None:
        raise ValueError("This report must not present planned directions as authored cases.")
    text_fields = ("evidence_basis", "proposed_task", "scoring", "readiness")
    list_fields = ("source_routes", "local_assets", "task_view", "controls", "missing_assets")
    sections = []
    navigation = []
    labels = {
        "evidence_basis": "依据与边界", "source_routes": "来源路线（无默认优先级）",
        "local_assets": "已有本地材料（不等于完成覆盖）", "proposed_task": "拟实现任务",
        "task_view": "任务视图", "scoring": "评分方式", "controls": "必要对照",
        "missing_assets": "待补材料或协议", "scope_limits": "测量限制", "asset_limits": "素材限制",
    }
    for row in rows:
        if row["title"] != titles[row["id"]] or row["evidence_inventory_id"] != row["id"]:
            raise ValueError(f"Inventory identity mismatch: {row['id']}")
        if row["implementation_status"] != "planned_not_implemented":
            raise ValueError("Implemented tasks need their own task manifest and evidence.")
        if row["new_task_package"] is not None or row["new_evaluation_run"] is not None:
            raise ValueError("Planning rows cannot stand in for a task or run manifest.")
        for key in text_fields:
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError(f"Missing {key} in {row['id']}")
        for key in list_fields:
            if not isinstance(row[key], list) or (not row[key] and key != "local_assets") or not all(isinstance(v, str) and v.strip() for v in row[key]):
                raise ValueError(f"Invalid {key} in {row['id']}")
        for asset in row["local_assets"]:
            if not local_path(asset).exists():
                raise ValueError(f"Missing local asset: {asset}")
        title = html.escape(f"{row['id']}. {row['title']}")
        navigation.append(f'<li><a href="#item-{row["id"]}">{title}</a></li>')
        fields = []
        for key, label in labels.items():
            if key not in row:
                continue
            values = row[key] if isinstance(row[key], list) else [row[key]]
            if key == "local_assets":
                content = "<ul>" + "".join(f"<li>{link(local_path(v), v)}</li>" for v in values) + "</ul>" if values else "尚无已核本地任务素材；按下列缺口补齐。"
            else:
                content = "<br>".join(html.escape(v) for v in values)
            fields.append(f"<tr><th>{label}</th><td>{content}</td></tr>")
        sections.append(
            f'<section id="item-{row["id"]}"><h2>{title}</h2>'
            f'<p>就绪条件：{html.escape(row["readiness"])}。状态：规划，未完成新任务实现。</p>'
            f'<table>{"".join(fields)}</table></section>'
        )
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    return (
        '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Edu Last Exam：37项全覆盖实施表</title><style>{STYLE}</style></head><body><main>'
        '<h1>Edu Last Exam：37项全覆盖实施表</h1>'
        '<p><strong>全部37项纳入范围；本表是实施路线，尚非37套已完成题目或已完成实验。</strong></p>'
        '<p>各方向先少量案例，完成全量探索后再判断难度。原库复用、文献机制改编、本地错题迁移按适配性选用。'
        '实际材料、任务视图和评分缺口逐条保留；不把静态或模拟代理当真实互动/学习效果。</p>'
        f'<p>{link(ROOT / "docs/plans/edu_last_exam_next_stage_plan_2026-11-10.md", "完整计划")} · '
        f'{link(inventory, "证据清单")} · {link(SOURCE, "机器可读实施表")}</p>'
        f'<p class="provenance">规划日期：2026-11-10 · Source SHA-256: {digest}</p>'
        f'<nav aria-label="37项目录"><ol>{"".join(navigation)}</ol></nav>'
        f'{"".join(sections)}</main></body></html>\n'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != result:
            raise SystemExit("Full-coverage planning HTML is missing or stale.")
        print("37/37 planning entries validated; local assets and generated HTML match.")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(result, encoding="utf-8")
        print(OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
