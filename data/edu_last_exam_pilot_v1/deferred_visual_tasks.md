# Deferred visual / interactive tasks

These are intentionally **not** included in `edu_last_exam_pilot_v1`.

## 1. Geometry diagram consistency

- Task: given a geometry statement and a rendered diagram, determine whether the diagram satisfies the statement.
- Why deferred: requires image assets and geometric parsing.
- Needed next: a small set of SVG diagrams with machine-checkable constraints.

## 2. Physics diagram consistency

- Task: detect mismatched labels, lengths, or force arrows in a physics diagram.
- Why deferred: requires domain-specific visual checks.
- Needed next: diagram metadata and expected invariant checks.

## 3. Interactive science demonstration

- Task: generate or audit an interactive demo whose controls produce scientifically correct behavior.
- Why deferred: requires executable code and browser automation.
- Needed next: Playwright-style deterministic tests and reference screenshots.
