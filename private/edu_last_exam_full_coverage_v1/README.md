# Edu Last Exam 全方向探索候选 v1

本批次落实完整证据清单 01–37，供作者离线核验和 GLM-5.3-Flash 探索试跑。**有题包不等于整个方向的全部子构念已被直接测量；独立领域教师审核与冻结尚未完成。** 实际数量和每项边界以 `manifest.json`、`reports/full_coverage_v1/implementation_status.html` 为准。

- `cards.jsonl`：基于37项实施矩阵的场景卡。
- `authored/`：完整候选题、来源、gold、rubric、控制及 runtime。
- `questions.html`：不含评分金标的题册；`review.html`：审阅册。
- `prompts.jsonl`：仅公开题面和素材路径；`runtimes.json`：运行器私有环境配置，不整体投递模型。
- `reference/`：参考解、复用身份、产物正反例及离线核验。
- `stimuli/`：实际投递材料。外部学生图片、作文与数据派生输入保留在本地，来源与再发布条件另查 NOTICE。

## 运行与评分

```bash
python3 scripts/build/build_edu_last_exam_full_coverage.py
python3 scripts/build/build_edu_last_exam_full_coverage.py --check
python3 -m pytest -q tests/test_edu_last_exam_full_coverage.py
/usr/bin/python3 scripts/experiments/launch_edu_last_exam_full_coverage.py --with-judge
```

从仓库根目录运行。真实 PPT 渲染需要可启动 LibreOffice 的宿主环境；受限沙箱出现环境错误时不能算模型失败。后台启动器在新目录冻结题包、运行代码与输入身份，继承 `GLM_API` 环境变量，不写凭证。并发上限4，预测与初评顺序执行，所有调用省略 `max_tokens`。

本机已安装依赖与可执行文件见 [runtime_environment.json](../../data/edu_last_exam_full_coverage_v1/runtime_environment.json)。启动时显式使用 `/usr/bin/python3`；交互shell中的默认Python可能指向缺少PPT依赖的其他虚拟环境。它记录本次环境，不冒充可移植容器。GLM测试作者与本批题目作者分离；保存试跑快照不等于正式benchmark冻结。

普通任务单轮；申诉、流程与复查执行真实续轮；帮助与提问采用公开动作接口、私有后续观察；跨会话任务清空原上下文，仅保留模型实际写下的 memory。工作区支持受限文件读写和提交。产物通过声明式合同及可信渲染器/解释器交付，不执行任意模型代码。这些均是明确受限的实验环境，不冒称完整自主Agent或真实课堂。

评分分为确定性检查、连续指标和语义初评。17按真实留出学习者的正确率预测误差与排序报告，不设人为二元难度通过线。其他语义任务由GLM-5.3-Flash先按逐项标准初评，引用必须来自实际模型输出；格式、证据或确定性结果冲突保留待审，不强判。所有方向分项报告，不合成跨方向正确率。

2026-11-10这轮回答已另行完成[全量Codex复核](../../reports/full_coverage_v1/glm53flash_20261110_codex_review/review.html)：保留原运行，逐份核对冻结题面、完整回答、实际产物与引用。源记录位于 `reviews/glm53flash_20261110_codex/`，按[复核协议](../../data/edu_last_exam_full_coverage_v1/codex_review_protocol_v1.md)审阅，并由 `python3 scripts/build/build_edu_last_exam_codex_review.py --check` 校验生成报告。报告另给本批明确二元版本的描述性计数，争议、连续指标和未测单列；不将其解释为统一能力分数。Codex参与过候选编写，这次复核不替代独立教师审核。

## 媒体与未测范围

GLM-5.3-Flash 官方文档列出文本、图像、视频和文件输入；音频字段在接口规范中仅列给 glm-4-voice。见 [模型说明](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-5.3-flash) 和 [接口规范](https://docs.bigmodel.cn/api-reference/模型-api/对话补全)。本批保留真实 WAV/MP4 文件及独立转写控制；选定接口不支持的音频标为 `unsupported_input_not_scored`，不会偷偷用转写替代。视频 data URI 的实际接受情况由运行回包记录。

真实学生长期学习收益、新生成题真实投放难度、所有年龄/语言/学科的泛化、完整生产LMS等仍未测。每题 `measurement_claim` 和 `unmeasured_subclaims` 列出具体边界。正式发布还需要独立教师审核、评分校准、多模型及留出实例证据、作者模型身份确认与排除关系，以及原始材料许可核验。
