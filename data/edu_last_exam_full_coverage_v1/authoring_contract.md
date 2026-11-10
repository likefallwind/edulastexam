# Full coverage v1 authoring integration contract

This is an exploratory candidate batch, not a frozen benchmark. Every inventory direction must have a concrete task and an explicit measurement boundary. Author with Codex; GLM-5.3-Flash is for testing only. Do not overwrite older evidence.

Write one or more JSON objects to `private/edu_last_exam_full_coverage_v1/authored/ELE-FC-NN-001.json`; assets belong to `stimuli/NN/`. Use independent directories per direction. Do not edit another contributor's direction or the shared runner/builder.

Required item fields:

- `item_id`: `ELE-FC-01-001` etc; `direction_id`: two digits; `title`.
- `material_origin`: source_reuse / source_adaptation / literature_mechanism_adaptation / local_failure_adaptation.
- `source_evidence`: list of objects with `source_id`, `locator`, and `local_path` or `url`; distinguish mechanism evidence from copied materials. Existing inventory records may provide literature provenance without pretending a new online verification occurred.
- `failure_mechanism`, `education_consequence`, `adaptations` (list), `limitations` (list), `measurement_claim`, `unmeasured_subclaims` (list).
- `status`: `{ "stage":"authored_candidate", "human_review":"pending", "frozen":false, "model_evaluation":"not_run" }`.
- `prompts`: list, each with `prompt_id`, neutral `system_prompt`, complete `user_prompt`, `assets` (relative paths under stimuli), `interaction_mode`.
- `gold.per_prompt`: keyed by prompt_id. Include `reference_answer`, `acceptable_alternatives`, `critical_errors`; optional machine-readable expected fields. Gold is never sent to the tested model.
- `rubric`: `{ "criteria":[{"criterion_id":"...","observable":"...","required":true}], "pass_rule":"all required criteria met and no evidenced critical error", "aggregation":"per_direction_and_task_view_only" }`. Mark minor flaws separately; do not require hidden response style.
- `controls`: list describing paired variants or explicit positive controls.
- `runtime`: optional per-prompt map keyed by prompt_id. Default `{ "mode":"single_turn" }`.

Runtime modes:

- `single_turn`: ordinary text/raster input.
- `scripted_dialogue`: `{ "mode":"scripted_dialogue", "followups":["actual next user message", ...] }`; each receives a real API response with previous messages. This is controlled dialogue, not evidence of natural student learning.
- `branching_dialogue`: `{ "mode":"branching_dialogue", "initial_state":"s0", "max_turns":5, "states":{"s0":{"actions":{"probe":{"observation":"student's actual next response","next_state":"s1"},"explain":{"observation":"...","next_state":"s2"}}},"s1":...}, "terminal_states":["done"] }`. Each state action menu is public during that state; hidden future observations are not shown. Model outputs JSON `{ "action":"...", "message":"..." }`. Judge checks whether message actually implements action; no claim of unrestricted natural tutoring.
- `artifact`: `{ "mode":"artifact", "artifact_type":"svg|html|slides_json|lesson_json|python_function", "validator":"NN", "repair_turns":1 }`. Prefer deterministic declarative output/JSON with a trusted renderer over executing arbitrary model code. Put validator contracts and reference artifacts under `reference/NN/` and any optional implementation in `scripts/full_coverage/directions/dNN.py`, exporting `validate_artifact(response_text: str, output_dir: Path, prompt_id: str) -> dict` (JSON-serializable result; may write trusted-rendered artifacts). Do not execute arbitrary code or network calls. Can use existing trusted render tools.
- `workspace`: coordinate with root; supports isolated declarative read/write/list/submit JSON actions, no shell.
- `media`: use actual media under stimuli; transcript is separate control, never silently substituted. Root handles endpoint support and unavailable status.

All assets copied from other batches must be copied explicitly; record source paths and hashes in adaptations/provenance. Full direct measurement may remain incomplete where real learner data are missing; provide an executable bounded task plus explicit pending subclaims. Do not fabricate real student data or claim the entire direction is solved by a proxy. Build meaningful minimal cases with controls, not placeholders.
