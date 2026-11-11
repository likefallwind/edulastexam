# Difficulty mining v1

This report is generated from existing `edubenchmark` scored JSONL files. It is a
candidate discovery index, not a frozen benchmark result. `unanimous_failure`
means that the historical panel models all missed the item under that suite's
protocol. It does not establish human difficulty, a correct gold answer, or an
education failure. `mini_v2` and `frontier_v1` are separate selections and are
reported separately.

Before promotion, inspect the original item, gold, scoring protocol, data
completeness, contamination risk, and educational consequence. Then re-run on
held-out models and, where the claim requires it, obtain independent human or
teacher evidence.

`cross_suite_candidates.jsonl` contains only items shared by `mini_v2` and
`frontier_v1` that remain low-scoring in both views. It is a review queue, not a
second score.
