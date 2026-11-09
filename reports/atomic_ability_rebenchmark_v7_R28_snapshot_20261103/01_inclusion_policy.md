# Inclusion Policy

## Main scoring layer

Include a model-run only when all conditions hold:

1. It is a benchmark/model result, not a judge calibration, jury calibration, rubric prompt experiment, or backup copy.
2. It has a concrete model name and a non-zero `total_items`.
3. It has at least 100 total items, unless a human explicitly promotes the run after inspection.
4. It maps to at least one `P01-P21` ability through `02_benchmark_ability_mapping.jsonl`.
5. If multiple judge versions score the same model responses, keep only the selected primary judge in the main scoring layer and keep the others as context rows.
6. For the three new safety mains, require the frozen prompt/rubric version, an allowed full-run path, complete status, expected item count, and at least 95% scored coverage. `age_values_v1` must also carry the complete A+B v7 headline.

## Excluded by default

- Small samples and smoke tests: `total_items < 100`.
- Judge/rubric calibration: paths under `_judge_rubric`, `_judge_jury`, and benchmark ids containing `judge_calibration`.
- Backup directories such as `selfjudge_backup_*`.
- Protocol-only/data-resource rows without model scores.
- Incompatible safety runs: boundary v1/v6 mixes, student-risk v3 or partial v7, age v2/v4/old summaries, and any safety run outside the explicit v7 allowlist.
- Old EduGuard/SATA/MRBench rows as evidence for P18/P19/P20. They remain available as related evidence and for unrelated abilities, but do not feed the new safety scores.

## General-benchmark handling (R20)

MMLU-Pro, C-EVAL, AGIEval, OlympiadBench, and MathTutorBench problem-solving
style results map mostly to `P05` and `P06` (knowledge and reasoning), where
answering IS the construct. The former foundation-gate ×0.45 tier factor was
removed in R20: high answer accuracy still cannot dominate the education-side
abilities because general benchmarks are simply not mounted on education Ps.
Since R25 the guardrail is carried entirely by that structural constraint plus
per-cell relevance — confidence is rule-derived and no longer discounts a
benchmark for being general, so these exam-style benchmarks sit at 1.0
(objective scoring + externally vetted data).

EduIllustrate full-230 runs are included when `total_items >= 100`; 5-item
smoke/calibration runs remain excluded.
