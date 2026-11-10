# 材料来源、改编及许可说明

## VtG改编材料：ELE-S01-001 / ELE-S01-002

来源：Nico Daheim, Jakub Macina, Manu Kapur, Iryna Gurevych, Mrinmaya Sachan. 2024. *Stepwise Verification and Remediation of Student Reasoning Errors with Large Language Model Tutors*. EMNLP 2024, pp. 8386–8411. [论文](https://aclanthology.org/2024.emnlp-main.478/)、[代码及许可说明](https://github.com/eth-lre/verify-then-generate/blob/main/README.md)。原数据基于MathDial的合成学生解答并带教师标注，不是真实学生作业样本。

原文件：`dataset/dataset.json`，commit `f509303b4d5667f79aa10e824ed035f49e8b0776`，数组索引106及14（从0计）。上游README徽章写CC BY 4.0，License段写CC BY-SA 4.0；本项目对这些改编材料采用后者的保守口径。

上述两包中的源题、学生作品及其改编部分按 **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)** 提供，并保留归属。修改包括：增加中文教师任务、步骤编号、参考稿对照、修复结论的控制版本，以及独立重算后的金标和评分说明。逐包详见`authored/`的`adaptations`。上游有误的参考答案和标签只作来源证据，不能当成正确评分依据；作者/原项目不为本项目的改编结论背书。

## EDU-CIRCUIT-HW图像：ELE-S02-001 / ELE-S02-002

来源：Weiyu Sun, Liangliang Chen, Yongnuo Cai, Huiru Xie, Yi Zeng, Ying Zhang. *EDU-CIRCUIT-HW: Evaluating Multimodal Large Language Models on Real-World University-Level STEM Student Handwritten Solutions*. ACL Findings 2026. [论文](https://aclanthology.org/2026.findings-acl.751/)、[官方项目](https://github.com/gt-learning-innovation/CIRCUIT_EDU_HW_ACL)。

使用官方公开样例 `hw5_student42_q7_5-4.png` 和 `hw8_student41_q10_6-1.png`，固定commit `d56d72861f443337d47d44714ee4ef8d4f6e5429`。它们是匿名学生的实际手写图像，本项目未修改图像。题面中的批改草稿和局部任务条件由本项目新写，不是论文中原模型回包；忠实转写按原图核对。

仓库代码许可证不自动覆盖学生图像和教材内容。本轮未确认图像再分发授权，因此图像仅保留本地的忽略文件，**不随Git提交、不直接公开发布**。本项目不授予这些外部图像新的许可。原教材题面没有被下载或复制；局部审查任务所需条件已在题面内明示。

## 自建学习历史：ELE-S03-001

借鉴[LongTutor](https://aclanthology.org/2026.acl-long.1371/)的历史证据使用问题，自建几何记录、任务与评分依据。没有复制该库学生日志，也没有把其诊断标签当成本题唯一心理成因。援助差异与当前题目是新的研究假设，不继承原论文模型难度。

## 共同状态

全部为作者离线核验候选，未完成独立专家审核或本批模型测试。公开来源已知样例不保证无训练污染；后续复用/改编后的结果不直接等于原benchmark结果。原始下载不入Git，精确路径、内容哈希和取得日期记录于`data/edu_last_exam_scenario_v1/source_manifest.json`。
