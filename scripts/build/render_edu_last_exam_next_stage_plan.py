#!/usr/bin/env python3
"""Render the next-stage plan; --check verifies the HTML without writing."""

from pathlib import Path

import render_edu_last_exam_research as renderer


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    renderer.SOURCE = root / "docs/plans/edu_last_exam_next_stage_plan_2026-11-10.md"
    renderer.OUTPUT = root / "reports/research/edu-last-exam-next-stage-plan-2026-11-10.html"
    renderer.main()


if __name__ == "__main__":
    main()
