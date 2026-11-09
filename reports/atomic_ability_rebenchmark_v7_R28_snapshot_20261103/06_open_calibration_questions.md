# Open Calibration Questions

Resolved in this pass:

- R20: the four-level evidence-tier system is removed; scoring weight = relevance × confidence only.
- R25: both weights become rule-derived — relevance in five tiers (1.0/0.8/0.5/0.2/0), confidence from two factors (objective vs LLM-judge scoring; externally vetted vs self-built data), giving 1.0/0.85/0.7 plus one documented exception.
- R28: active codes are `P01-P21`; general safety is P10 in the base layer, and v6 P10-P16 shift to P11-P17 without changing their constructs or evidence.
- P18/P19/P20 use only education_boundary_v1, student_risk_v2, and age_values_v1. Old related safety benchmarks do not feed these scores.
- Age-values B uses a content-only headline with equal weight over B1-B4; guidance is auxiliary. Full P20 requires both A/core and B.
- CEG reports four separate safety domains and no longer computes a group average.

Remaining review points:

1. P10 needs broad primary general-safety coverage; P21/EduEquity remains exploratory. Do not fill either with old related benchmarks merely to produce a number.
2. Complete and freeze full latest-rubric runs for the three new safety mains, with independent response-level calibration and judge-swap checks before upgrading provisional scores.
3. For cross-model comparison, decide whether to add a strict `common-evidence` mode that only compares models on shared benchmark/subdimension coverage.
