# Edu Last Exam Repository Guidelines

## Scope

本仓库专门维护 Edu Last Exam 的教育场景研究、题目、评分协议和实验。源仓库 `/home/likefallwind/code/edubenchmark` 的内容已经按快照复制到这里；今后 Edu Last Exam 的开发、审核和试验默认在这里进行。任何同步都必须是显式复制，禁止为了整理本仓库而删除、移动或重置 `edubenchmark` 中的文件。

本项目的结论必须区分四种状态：设计假设、作者离线检查、模型试跑证据、冻结 benchmark 结论。一次模型的少量错误不能证明“绝大多数 Agent 不通过”，同样，一次通过也不能证明题目没有教育意义。

## Layout

- `docs/plans/`: human-authored plans and decisions.
- `docs/evidence/`: literature and repository evidence matrices.
- `docs/benchmark_profiles/`: benchmark profiles and protocol notes.
- `data/`: machine-readable taxonomies, mappings, manifests, and contracts.
- `private/edu_last_exam_pilot_v1/`: authored items, stimuli, references, review sheets, and generated item books.
- `reports/`: generated research and evaluation evidence. Do not hand-edit generated reports.
- `scripts/`: builders, evaluation entry points, and reusable adapters.
- `tests/`: deterministic offline checks.
- `sources/datasets/`: downloaded external data only; keep it uncommitted and record access/provenance in a manifest.
- `eval/`, `logs/`, and `tmp/`: local run control and scratch artifacts; these are not authoritative evidence.

Do not add unrelated benchmark data merely because a copied adapter can consume it. Port an adapter or dataset only when it is needed by an Edu Last Exam experiment and document the dependency.

## Construct and item rules

Education scenario is the primary classification. P01–P21 is an optional explanatory axis; if a case is tagged, use only the exact existing labels in `docs/atomic_ability_mapping_v7_2026-11-02.md` and `data/mapping_measurement_model_v7.json`. Do not invent new atomic abilities in item files. A case may be single-turn, multi-turn, or long-cycle according to its construct. Student-state maintenance is required only when the target behavior requires it.

Every candidate needs:

- a concrete education consequence and a documented failure mechanism;
- input sufficient for the requested judgment without hidden facts or answer leakage;
- a reference answer or acceptable answer set;
- observable rubric criteria and explicit critical errors;
- controls or counterfactuals when the claim depends on robustness, adaptation, or state;
- a status showing whether human review and model evaluation have actually happened.

Keep the authoring workflow `cards -> authored -> export -> validate -> review -> freeze`. Tested-panel models must not generate the canonical items. Synthetic challenge candidates remain candidates until human review, protocol checks, and multi-model evidence are complete.

## Evaluation and evidence

Use isolated output directories for smoke, exploratory, and canonical runs. Preserve `summary.json`, manifests, completion markers, exit codes, prediction/extraction identity, and scoring configuration. A live process or growing log is not completion. Do not average different task views into a single score when their constructs differ.

Never add a `max_tokens` ceiling to prediction, extraction, or judge calls unless the model or gateway explicitly requires it. The repository-wide exception is `deepseek-v3.2`, which is pinned to 32768 by the existing provider contract.

Raw downloaded datasets and credentials stay out of Git. API keys must come from environment variables. Do not overwrite copied evidence with a new run; use a new dated or explicitly named output directory.

## Validation

Run the smallest relevant offline checks before changing scope:

```bash
python scripts/build/build_edu_last_exam_challenge_items.py --validate-only
pytest -q tests/test_edu_last_exam_challenge_trial.py
```

For a new builder or protocol, add a deterministic validation path before invoking an API. Report missing assets, proxy substitutions, judge dependence, and unmeasured difficulty explicitly.

## Change hygiene

Use short imperative commit messages such as `Add ...`, `Update ...`, and `Refactor ...`. Keep source documents, machine-readable specs, scripts, and generated reports in their designated directories. Do not commit credentials, downloaded datasets, transient logs, or large raw prediction bundles unless the experiment explicitly requires them as durable evidence.

