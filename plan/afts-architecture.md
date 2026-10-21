# AFTS 文件架构

来源：架构讨论稿 v0.1。日期：2026-10-21。

这是**已采纳的目录**。仓库根就是 AFTS，不再套一层 `AFTS/`。具体类名仍不锁死。`storage/` 是数据分类，不表示全部用本地文件。

Spring Boot 在 `backend/`。图中的 `backend/` 子目录是包，物理路径为 `backend/src/main/java/afts/...`。见 [afts-layout.md](afts-layout.md)。

栈与产品目标见 [afts-base.md](afts-base.md)。

## 目录树

```text
AFTS/
├── backend/                    # Spring Boot
│   ├── config/
│   ├── agents/                 # Main / Level 1 / Subagent
│   ├── harness/                # 自定义 Agent Loop
│   │   ├── runtime/
│   │   ├── context/
│   │   └── policies/
│   ├── workflow/               # 基于 LangGraph4j
│   │   ├── graphs/             # 主图与子图
│   │   ├── nodes/              # Agent 执行节点
│   │   ├── state/              # Graph State
│   │   ├── delegation/         # 动态委托与生命周期
│   │   └── checkpoints/        # 状态保存与恢复
│   ├── memory/                 # 长期记忆管理
│   ├── tools/                  # Agent Tool 接口
│   ├── execution/              # Python Runner 集成
│   ├── domain/                 # 业务数据结构
│   ├── persistence/            # 数据持久化
│   ├── observability/          # 事件与追踪
│   └── api/
├── python/
│   ├── scripts/
│   ├── runner/
│   └── sandbox/
├── frontend/                   # Dashboard
├── storage/                    # 数据与研究产物
└── docs/
```

## 目录与模块

| 路径 | 模块 | 职责 |
| --- | --- | --- |
| `backend/agents` | Agent Management | 角色定义、Catalog、实例创建与生命周期 |
| `backend/harness` | Custom Harness | 自研单 Agent loop。子包 `runtime`、`context`、`policies` |
| `backend/workflow` | Workflow + LangGraph4j | 子包 `graphs`、`nodes`、`state`、`delegation`、`checkpoints`。业务仍自研，图执行用 LangGraph4j |
| `backend/memory` | Memory | Session / Project / Agent / Global |
| `backend/tools` | Tool Gateway | Agent 与外部工具、Web 等能力 |
| `backend/execution` + `python/scripts`、`python/runner`、`python/sandbox` | Python Execution | 本地脚本、Runner、隔离测试。目录已在，没有实现 |
| `backend/persistence` + `storage/` | Persistence | 任务、Session、Memory、产物、执行记录。`storage/` 尚未再分子目录 |
| `frontend/` | Dashboard | 正式产品视图 |
| `backend/observability` | Security & Audit 的观测面 | 追踪、指标、审计；权限、审批、预算、资源限制可落 config 与 workflow |
| `backend/config` | 系统配置 | 系统、模型与运行配置 |
| `backend/domain` | 领域结构 | 自定义数据结构 |
| `backend/api` | 对外接口 | Web / API |

## Custom Harness（`backend/harness`）

自研 Agent Loop，不用框架封装的 ReActAgent 当默认循环。必须能控制：

- 每一轮模型输入、Context、历史消息及工具列表
- 模型输出与 Tool Call 的解析和验证
- 工具调用前后的权限、审批与结果处理
- 每轮状态更新、上下文压缩与 Memory 检索
- 循环次数、Token 预算、异常恢复与停止条件
- Subagent 的创建请求及其执行结果回传

初期用 Spring AI 的模型、消息和工具接口。Harness 作为 LangGraph4j 图中的节点被调用，不在 Harness 里再实现一套图引擎。

## Workflow（`backend/workflow`）

与单个 Agent 的 Harness 分离。Agent 提出任务决策，Workflow 负责确定性执行和验证。

- **底层（用 LangGraph4j 1.9.x，不自研）：** 状态图、条件边、并行节点、子图、Checkpoint、暂停/恢复。
- **业务（自研，叠在图之上）：** Agent Catalog、动态派生策略、权限继承、任务委托记录、循环依赖检测、预算与审批。

至少支持：

- Task 创建、委托、依赖和状态管理
- Agent / Subagent 动态启动、暂停、恢复、终止
- 并发控制、任务预算与权限继承
- 任务完成、异常、审批等事件通知
- Main Agent 对全局任务状态的查询
- 多 Session、多 Project 并行
- 任务依赖必须能检测循环、重复执行和无法结束的等待

## Memory（`backend/memory` + `storage/`）

| 类型 | 内容 | 更新策略 |
| --- | --- | --- |
| Session Memory | 当前 Session 的过程、阶段成果、Compact Context | 执行中持续更新 |
| Project Memory | 项目目标、研究状态、重要决策、成果引用 | 重要事件发生时更新 |
| Agent Memory | Main / 一级 Agent 的长期专业知识及经验 | 任务结束后提取候选，验证后写入 |
| Global Memory | 跨角色、跨项目的共享知识和规则 | 暂保留接口，具体定义待讨论 |

同一长期 Agent 可能同时参与多个 Session 或 Project，禁止各运行实例直接覆盖长期 Memory。

1. 各 Session 独立维护执行上下文。
2. 任务结束后生成 Memory Candidate。
3. 由统一 Memory Consolidator 检查证据、重复、冲突和适用范围。
4. 通过版本号、事务或并发控制安全写入。
5. 保留原始证据、更新历史和撤回能力。

Session 压缩摘要不能替代原始历史。原始消息、任务事件和工具结果需要可追溯。Agent Profile / 权限配置与 Agent Memory 分开存储，防止 Agent 在学习过程中擅自改变职责或权限。

## Python（`python/` + `backend/execution`）

独立本地计算层，不直接依附 Agent Loop。

- 复用和扩展已有 Python 数据分析脚本
- 本地 Anaconda / Conda、venv
- 未审查或 AI 新生成的代码进入隔离 Sandbox；已批准脚本走正式 Runner
- 异步任务、队列、超时、取消、日志、资源限制
- 产物：CSV、Parquet、JSON、PNG、SVG、HTML 等
- 每次执行生成可追踪的 Job ID / Run ID

现有 Hermes AFTS 的 Runner 和代码审批机制可作为复用候选，不预设必须完全重写。

## Dashboard（`frontend/`）

正式产品模块，不是开发调试台。所有 UI 数据以任务记录、运行事件和实际产物为准，不依赖 Main Agent 的自然语言描述。

这些是产品视图，目录还没有拆开，都留在 `frontend/`。

| 视图 | 内容 |
| --- | --- |
| Team Overview | Agent 状态、当前任务、动态委托关系、任务依赖、进度和异常 |
| Agent Activity | 任务历史、模型调用、工具调用、Subagent 活动、执行结果与错误日志 |
| Data Explorer | 清洗产物 Schema、样本、清洗前后对比、缺失值、异常值、数据来源 |
| Research Results | 统计指标、图片、交互图表、研究报告（例如 Rolling Beta、因子稳定性、回归分析、回测结果） |
| Memory 审查 | Memory 审查与历史 |

## 暂不固定（后续施工计划）

- 自定义 Agent Loop 与框架 Hooks 的使用边界细节
- Agent Catalog 的描述、选择与启动接口
- Subagent 最大并发、委托权限和执行预算
- Agent 间通信与 Workflow 的事件模型
- Session、Project 和 Agent Memory 的具体存储技术
- Long-term Memory 的验证机制及是否使用向量检索
- Web Dashboard 的前端框架与实时数据推送方式
- Python Runner 的接口协议、进程隔离和 Sandbox 方案
- 具体一级 Agent 的人设、职责、工具和协作规范
- 是否再把 `backend/` 拆成多个 Maven 模块
