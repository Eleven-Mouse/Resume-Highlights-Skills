# 项目亮点 Skill

这是一个面向本地代码仓库的分析型 skill，用来产出项目亮点、简历表述、面试深挖点、JD 匹配分析和改进建议。

它不是传统业务系统，更像一个“提示词工程 + 知识组织 + 输出治理”的工具型项目。最适合体现的能力是：

- 工程化的提示词设计
- 规则系统拆分与治理
- 基于代码证据的结构化分析
- 简历 / 面试 / JD 匹配输出的模板化沉淀

## 怎么用

常见调用方式：

```text
$project-highlights 帮我看这个项目有哪些亮点
```

```text
$project-highlights 给我 Java 后端工程师版本的简历亮点
```

```text
$project-highlights 分析这个项目和 AI 应用开发工程师 JD 的匹配度
```

推荐用户补充 3 个信息：

1. 目标岗位
2. 产物类型
3. 项目定位

## 仓库结构

```text
SKILL.md                      skill 入口文档，只放导航和最小流程
references/
  core-guidelines.md          唯一规则源
  analysis-workflow.md        扫描流程与分析维度
  jd-and-company-mapping.md   JD 和公司口径映射
  output-formats.md           输出格式与岗位版本
  detailed-report-template.md 长报告与专项模板
  java-backend-rubric.md      Java 后端专项口径
  system-optimization.md      系统优化专项
  risk-and-self-check.md      风险审查与最终自检
scripts/
  repo_snapshot.py            轻量级仓库结构摘要脚本
agents/
  openai.yaml                 agent 展示配置
```

## 文件职责

`SKILL.md`

- 只保留 skill 用途、调用示例、最小执行流程、按需阅读导航、最小边界

`references/core-guidelines.md`

- 唯一规则源
- 负责维护候选人定位、证据分层、默认 seniority、高风险措辞边界

其它 `references/*.md`

- 只展开单个专题
- 不重复定义核心规则

## 维护原则

1. 改核心规则，先改 `references/core-guidelines.md`。
2. 改输出风格，优先改 `references/output-formats.md` 或 `references/detailed-report-template.md`。
3. 改岗位 / JD 口径，优先改 `references/jd-and-company-mapping.md`。
4. 改扫描逻辑，改 `scripts/repo_snapshot.py`。
5. 不要把 `SKILL.md` 再写回“大一统长提示词”。

## 自测命令

改完后，至少跑下面两条：

```powershell
python scripts\repo_snapshot.py .
```

用途：确认结构摘要能正常输出，且当前这类文档型 / 工具型仓库仍能识别出 `references`、`scripts`、`agents` 线索。

```powershell
python -m unittest tests.test_repo_snapshot
```

用途：回归验证 `repo_snapshot.py` 的 3 个关键行为：

- 不把普通 `service` 误判成入口
- 真正忽略 `node_modules`、`target` 等目录
- 文档型 / 工具型仓库仍能给出有效区域线索

## 当前支持的常见输出

- 快速点评版
- 简历版
- 面试版
- JD 映射版
- 详细报告
- S 级亮点专项文档
- 系统优化专项
- 风险审查与自检

常见岗位版本和长报告模板不要在这里重复维护，统一以 [references/output-formats.md](references/output-formats.md) 和 [references/detailed-report-template.md](references/detailed-report-template.md) 为准。

## 维护时别踩坑

- 不要在多个文档里重复维护同一套规则
- 不要脱离代码事实写指标、规模、主导度
- 不要把普通 CRUD 或外部 LLM API 调用硬包装成高阶架构亮点
- 如果只是改文案，不要顺手改规则；规则统一回到 `core-guidelines.md`
