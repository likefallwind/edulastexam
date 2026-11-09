# challenge_v2 作者检查与导出

- 任务包：21；独立投递 prompt：34；覆盖方向：21。
- 材料：合成研究启发题，作者 Codex；未使用受测模型 API 生成。
- 状态：作者离线自检通过；人工审核 pending；模型实测 not_run。
- 原 pilot 的 12 题与评测适配器未纳入此次构建。
- 检查只验证所列数学、程序或材料一致性，不能证明教育有效性或前沿模型难度。
- 浏览器检查另见 reports/challenge_v2/authoring_checks/；不能从数学检查推定浏览器检查已完成。

## 离线检查

- `checks/01.py`：01 PASS: weighted conditional counts, two independent cancelling errors, follow-up oracle
- `checks/02.py`：02 PASS: projection/sign convention, off-plane alternative, carry-forward marks
- `checks/03.py`：03 PASS: executable independent defects, valid controls, note invariance
- `checks/04.py`：04 PASS: exhaustive good implementation, actual nontermination counterexample, partial marks
- `checks/05.py`：05 PASS: Simpson reversal, standardization, score controls; causality boundary requires human review
- `checks/06.py`：06 PASS: weighted moments, carry-forward arithmetic, strict threshold, identical substantive materials
- `checks/07.py`：07: topology equations and both reference directions verified
- `checks/08.py`：08: slack transition, positive speed, and nonduplicating partial credit verified
- `checks/09.py`：09: four cells, pooled/stratified/target calculations verified
- `checks/10.py`：10: measurement bounds and uncompleted transfer state verified
- `checks/11.py`：11: both worksheets and fixed-fee error independently verified
- `checks/12.py`：12: 40 raw answers, hint separation, time contrasts and proposed probes verified
- `checks/13.py`：13: all three independent snapshots and fraction/unit references verified
- `checks/14.py`：14: eight exercise answers, equivalent forms and three accurate fraction diagrams verified
- `checks/15.py`：ELE-C2-15: 3003 parameter checks and endpoint/option witnesses passed
- `checks/16.py`：ELE-C2-16: all 10 point pairs, single-reading ambiguity, transfer and absolute-reading anomaly checked
- `checks/17.py`：PASS 17: exact bounds, feasible endpoint tables, 651 joint worlds, updated selection
- `checks/18.py`：PASS 18: 10 valid triples, 640 answer records, minimum-length counterexamples, L/M diagnosis
- `checks/19.py`：19: ideal-gas invariant, stop complementarity, and SVG geometry verified
- `checks/20.py`：20: actual reference JavaScript matches piecewise RC law, signed current, continuity, history and reset
- `checks/21.py`：21 PASS: labels share identical work/rubric, inequalities and practice oracle; accessibility judgments remain human-reviewed
