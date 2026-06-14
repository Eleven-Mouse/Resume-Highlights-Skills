---
name: project-highlights
description: 基于本地代码仓库提炼有代码证据支撑的项目亮点、简历表述、面试深挖点、岗位匹配分析和改进建议。适用于用户询问项目亮点、项目是否能写进简历、面试如何讲项目、JD 匹配度、Java 后端深度、AI 应用/Agent/RAG/workflow 能力、平台工程价值或架构治理价值等场景。
---

# 项目亮点

只从代码里找亮点，不替项目编故事。

## 入口规则

- `references/core-guidelines.md` 是唯一规则源。
- 候选人定位、证据分层、默认 seniority、高风险措辞边界，只在 `core-guidelines.md` 定义。
- 其他 `references/*.md` 只负责展开某个专题，不再重复定义这些核心规则。

## 最小执行流程

1. 先明确用户要的产物、目标岗位和目标 seniority。
2. 用 `python scripts/repo_snapshot.py <repo_path>` 快速拿仓库结构摘要。
3. 再看入口、模块结构、README、配置、部署文件、表结构、测试。
4. 先重建项目画像，再提炼亮点、风险边界和补齐建议。
5. 关键结论必须回到源码核实，不靠 README 或想象补故事。

## 按需阅读

- 通用规则、候选人定位、证据分层、项目识别、业务背景重建：读 [core-guidelines.md](references/core-guidelines.md)
- 深度扫描清单、代码阅读路径、分析维度：读 [analysis-workflow.md](references/analysis-workflow.md)
- JD 能力模型、公司口径映射、工程深度分层：读 [jd-and-company-mapping.md](references/jd-and-company-mapping.md)
- 简历版、面试版、JD 映射、公司定向排序：读 [output-formats.md](references/output-formats.md)
- 超长报告、S 级亮点专项文档、1 分钟 / 5 分钟讲法：读 [detailed-report-template.md](references/detailed-report-template.md)
- Java 技术栈或 Java 后端岗位：读 [java-backend-rubric.md](references/java-backend-rubric.md)
- 系统优化专项、建议补齐项：读 [system-optimization.md](references/system-optimization.md)
- JD 差距分析、风险审查、最终自检：读 [risk-and-self-check.md](references/risk-and-self-check.md)

不要默认把全部 `references` 都灌进上下文，只读当前任务相关的那部分。

## 最小边界

- 没有证据，不写指标、不写规模、不写主导度。
- 普通 CRUD、框架标准用法、外部 LLM API 调用，不硬包装成架构亮点或模型推理优化。
- 输出前至少确认：亮点能否追溯到代码、是否区分了 `代码已实现 / 强推导亮点 / 可扩展设计`、措辞是否与目标岗位一致。
