# 分析流程

当用户要深度仓库审计、架构判断、证据密集型项目亮点报告时，读取本文件。

## 0. 配套阅读

- 通用规则、候选人定位、证据分层：看 [core-guidelines.md](./core-guidelines.md)
- JD 与公司口径：看 [jd-and-company-mapping.md](./jd-and-company-mapping.md)
- Java 后端专项：看 [java-backend-rubric.md](./java-backend-rubric.md)
- 输出模板：看 [output-formats.md](./output-formats.md) 和 [detailed-report-template.md](./detailed-report-template.md)
- 优化建议与补齐项：看 [system-optimization.md](./system-optimization.md)
- 风险审查与自检：看 [risk-and-self-check.md](./risk-and-self-check.md)

## 1. 扫描顺序

默认按下面顺序推进，除非仓库结构明显更适合别的路径：

1. `python scripts/repo_snapshot.py <repo_path>`，先拿结构摘要
2. `README`、文档、启动脚本
3. 入口、路由、controller、handler
4. service、workflow、agent、use case
5. repository、DAO、mapper、外部 client
6. 配置、manifest、Docker、k8s、CI、环境文件
7. schema、migration、SQL、缓存、MQ、存储布局
8. 测试、benchmark、eval、脚本

优先使用 `rg`、manifest 文件和结构化证据，不要一上来随机翻文件。

## 2. 先重建项目类型

按证据而不是按想象分类。常见类型：

- 业务系统
- 平台/中后台系统
- AI 应用系统
- Agent / workflow 编排系统
- RAG / 知识检索系统
- 数据 / BI 工具
- 基础设施 / 治理工具
- 存储 / 检索系统

至少回答这些问题：

- 核心业务对象是什么？
- 主链路是什么？
- 最危险的失败点是什么？
- 更偏一致性，还是更偏吞吐/可用性？
- 代码事实看下来，它究竟是什么系统？

## 3. 严格区分三种证据层级

### 代码已实现

只有在代码、配置、表结构、测试、部署文件能直接支撑时才能使用。

### 强推导亮点

当命名、调用链、表结构、模块边界强烈暗示某个真实诉求，但实现细节没有完全展开时使用。

例如：

- 存在去重字段 + 重试逻辑，可以谨慎推导出“存在幂等诉求”
- 存在文档导入 + embedding + retrieval 链路，可以推导出“存在 RAG 主链路”

### 可扩展设计

用于描述有价值但当前尚未实现的增强项。

绝不能把它写成已经落地。

## 4. 给亮点分级

用两条轴线独立判断。

### 证据强度

- `S`：代码直接证明，简历价值高
- `A`：支撑较强，可写但措辞要克制
- `B`：更适合面试延展，不建议直接当成已落地成果

### 资深度层级

- `L1`：工程卫生项
- `L2`：强工程师 / 高级工程师能力
- `L3`：有架构相关价值的系统设计或治理能力
- `L4`：平台级、标准化、方向负责人级能力

`L4` 只能慎给，别手滑。

## 5. 各维度要看什么

### 架构与模块边界

重点看：

- 入口和对外接口
- 模块边界
- 主链路核心 service
- strategy、workflow、状态机、事件、领域抽象
- 逻辑是分层清晰还是到处散落

### 数据、存储与一致性

重点看：

- 核心表和实体
- 事务边界
- 索引和查询模式
- 缓存与一致性保护
- 对象存储、搜索、向量存储、元数据
- migration 脚本
- 幂等、乐观锁、唯一约束

### 异步链路与调度

重点看：

- MQ、event、job、scheduler、retry
- 消费幂等
- 死信或补偿
- 批处理
- 长任务 workflow

### 稳定性、治理与安全

重点看：

- 统一异常处理
- 请求日志或操作日志
- trace 或 metrics
- timeout、retry、降级、开关
- 认证、RBAC、租户、审计、防重放、限流

### AI 应用、Agent、RAG、workflow、DSL

重点看：

- 模型 client 抽象
- prompt 模板
- tool 注册与执行
- workflow 或任务编排
- memory 或上下文处理
- 文档加载、切片、embedding、retrieval、rerank
- fallback、timeout、token 或成本意识
- eval 数据集、反馈回流、benchmark 痕迹
- DSL parser 或 executor

如果代码只是调模型 API，更适合定位为应用层编排。

### 性能与规模

重点看：

- 线程池
- batching
- SQL / 缓存优化
- 热点链路瘦身
- 并发控制
- benchmark / profiling 产物

没有测量证据时，禁止自己补规模故事。

## 6. 分布式 / 存储口径边界

只有在代码体现了下列内容时，才适合往分布式或存储方向靠：

- 元数据管理
- 分片 / 分区
- 副本
- 一致性或恢复设计
- 生命周期管理
- 搜索 / 检索基础设施
- 多租户隔离

如果证据偏弱，优先表达为：

- 数据访问与检索链路优化
- 缓存和搜索集成
- 平台侧数据治理

## 7. AI 性能优化口径边界

只有在代码里真的出现下面这些东西时，才适合往 AI 性能优化方向写：

- 量化
- CUDA、Triton、MLIR、TVM
- kernel / operator 优化
- RDMA 或通信调优
- batching、KV cache、prefix cache
- benchmark 或 profiler 输出

否则请明确写：

`未发现模型底层推理优化证据，更适合定位为 AI 应用工程化或系统治理能力。`

## 8. 正确给出改进建议

在事实清楚之后，再推荐最值钱的缺口，例如：

- 可观测性缺口
- 测试缺口
- 幂等与一致性保护不足
- 缓存策略有待加强
- workflow 失败恢复不足
- prompt / 版本 / eval 管理缺失

每条建议尽量写清楚：

- 当前缺什么
- 为什么重要
- 应该落在代码库的哪里
- 它提升的是简历价值，还是主要提升工程质量

## 9. 安全措辞模板

优先：

- `基于代码事实可确认`
- `从模块边界和调用链可以推导`
- `更适合表达为`
- `未发现足够证据支持`

避免：

- `显然是`
- `一定是`
- `主导整体架构`
- `千万级`
- `工业级推理优化`
