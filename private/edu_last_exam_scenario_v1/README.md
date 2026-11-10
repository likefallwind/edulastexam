# 场景研究首批候选题 · 2026-11-10

本批为 **5 个任务包、12 个独立投递版本**：10 个纯文本版本、2 个原图版本。不是12道独立题，也不是真实多轮。状态为作者离线核验候选；专家审核、当前模型测试和评分校准尚未完成，未冻结。

- [题册 HTML](questions.html) / [题册 Markdown](questions.md)：题面与各版本的可见材料。
- [审阅册 HTML](review.html) / [审阅册 Markdown](review.md)：参考答案、可接受替代、关键错误、评分标准与对照关系；禁止投递给被测模型。
- [来源及许可说明](NOTICE.md)、[源材料审查记录](../../docs/evidence/edu_last_exam_source_item_audit_2026-11-10.md)。

| 包 | 场景与版本 | 材料及定位 |
|---|---|---|
| ELE-S01-001 | 年龄作业复核：正确学生/错误参考、正确学生/正确参考、错误学生/正确参考 | VtG数组第106条（从0计）；修正错误金标，作为参考稿稳健性候选 |
| ELE-S01-002 | 空间站逐步批改：原错误结论、修正结论 | VtG数组第14条（从0计）；首错应为S6，原标签S4错误 |
| ELE-S02-001 | 电感计算扣分复核：原图、忠实转写 | 真实公开手写作品；相位识别与缺失单位的证据边界 |
| ELE-S02-002 | 交流电路推导复核：原图、忠实转写 | 真实公开手写作品；补齐本题局部电路条件，核验有效移项和幅相 |
| ELE-S03-001 | 学习历史诊断：无帮助、教师给过方法/答案、帮助记录未知 | 自建12条几何学习记录；仅改变3条记录的援助字段 |

前两包的基础数学简单，当前定位包括校准/稳健性；本批不能直接称为已验证的“最难题集”。是否成为挑战题由后续模型结果和教师审核决定。来源中的学生可能是合成学生、真实手写学生或本项目合成记录，逐包注明，不混称真实课堂失败。

## 作者工作流

`cards.jsonl -> authored/*.json -> export -> validate -> review -> freeze`

当前完成到作者离线validate。`authored/` 与文本 `stimuli/` 是可编辑源文件；`items.jsonl`、`prompts.jsonl`、`reference/`、题册、审阅册、`manifest.json` 和构建报告由脚本生成。不要手改导出物；人工审核结果另存文档，不用覆盖`pending`制造已审核状态。

```bash
python3 scripts/build/build_edu_last_exam_scenario_v1.py
python3 scripts/build/build_edu_last_exam_scenario_v1.py --validate-only
python3 -m pytest -q tests/test_edu_last_exam_scenario_v1.py tests/test_edu_last_exam_challenge_trial.py
```

HTML导出依赖`markdown-it-py`（与调研报告生成器一致）。离线校验验证数学、配对变化、资产身份与源/导出一致性；它不能验证教学效度、当前难度或教师评分一致性。

## 外部原图

原始下载保存在忽略目录 `sources/datasets/edu_last_exam_scenario_v1/`。两张投递原图也是忽略文件，字节与原始下载完全一致；没有重画、裁剪或偷偷换成转写。完整来源、固定commit与SHA-256记录于 [source_manifest.json](../../data/edu_last_exam_scenario_v1/source_manifest.json)。

新检出仓库缺少图片时，先显式获取固定版本，再导出：

```bash
python3 scripts/build/build_edu_last_exam_scenario_v1.py --fetch-assets
python3 scripts/build/build_edu_last_exam_scenario_v1.py
```

图片没有下载成功或哈希不符时构建失败，不使用代理图片。图像再分发条件仍未确认，原图不入Git，本批不直接公开发布。已有条件足够进行本地候选研究；公开冻结前还要处理材料授权。

## 投递与评分边界

兼容现有隔离试跑器，只读取`prompts.jsonl`及列出的`stimuli`。离线投递检查可执行：

```bash
python3 scripts/experiments/run_edu_last_exam_challenge_v2.py \
  --batch private/edu_last_exam_scenario_v1 \
  --output /tmp/edu-last-exam-scenario-v1-dry-run \
  --model UNSELECTED-PANEL --dry-run
```

这条命令不调用API、不判分。实际试跑须另定模型版本、提示和供应商协议；作者模型身份尚未由运行环境记录，冻结前需确认并排除作者模型与被测面板的冲突。没有用被测模型API出本批正式题；本批本身也不是canonical题集。

每个版本的rubric为10点，用于待校准的语义审阅；没有设定正式通过阈值。关键错误单列，即使文字流畅也不能掩盖错误扣分或证据捏造。成对差异另报，不把不同场景或图像/转写条件混成总分。未运行API、未进行独立教师判分时，结果保持`not_run`/`pending`。
