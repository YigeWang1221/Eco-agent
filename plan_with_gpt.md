# AFTS — Multi-Agent Financial Research Platform

## 项目设计与开发交接文档

**版本：** Design Handoff v0.2  
**日期：** 2026-10-21  
**状态：** 架构设计阶段，部分技术路线已确定，具体实现待讨论

---

## 1. 项目背景与核心目标

### 1.1 项目背景

AFTS 原名 **America-Fina-Tech-Stock**，最初是基于 Hermes Agent 搭建的多 Agent 美股量化研究团队。

原系统已经探索和实现过以下能力：

- 多个具有不同职责的 Agent 协作执行研究任务。
- 任务看板、任务依赖、自动派发及任务交接。
- 本地 Python 数据分析与量化回测。
- 独立的 Mac Python Runner。
- 代码审批、执行记录、资源监控和异常处理。
- 通过 Telegram 进行任务管理和人工审批。

现在计划重新设计 Agent 系统，使用 Java 生态构建一个具有高度自主控制能力的多 Agent 平台。

**新系统不是简单复刻 Hermes，而是借鉴 Hermes 和 Deep Agents 中成熟的设计思想，建立自有 Agent Runtime 与团队协作系统。**

原 Hermes 系统作为需求和实现经验的参考，不代表新系统必须继承旧的角色配置、调度方式或工具限制。

### 1.2 产品目标

构建一个由 GPT 等 LLM 驱动的多 Agent 金融研究平台，模拟真实金融咨询和量化研究团队的协作过程。

用户只需要提出一个研究目标，系统能够自主完成：

1. 理解用户需求、规划研究任务。
2. 动态选择专业 Agent 参与工作。
3. 根据任务复杂度创建临时 Subagent。
4. 并行开展金融信息检索、数据分析、研究和计算。
5. 通过本地 Python 环境完成复杂数据处理、统计分析和回测。
6. 汇总、交叉验证及审查阶段性成果。
7. 通过 Web Dashboard 展示 Agent 工作过程、研究数据和分析图表。
8. 将经过验证的工作经验逐渐积累为 Agent 长期 Memory。

最终希望形成一个**可长期运行、可以不断扩展专业能力、拥有持久化知识与研究经验的 AI 团队**。

---

## 2. 已确定的技术路线

| 技术层 | 当前决定 | 主要职责 |
|---|---|---|
| 应用框架 | Spring Boot | API、业务服务、应用基础设施 |
| LLM 集成 | Spring AI | ChatModel、消息结构、模型及工具接口 |
| Workflow Runtime | **LangGraph4j** | 图执行、状态、条件路由、并行、Checkpoint、暂停恢复 |
| Agent Runtime | **Custom Harness** | 自研 Agent Loop、Context、Tool 调用、预算、停止条件 |
| Python Runtime | 本地 Conda / venv + Sandbox | Python 分析、统计、回测和新代码测试 |
| Memory | 自定义分层 Memory System | Session、Project、Agent、Shared Memory |
| 前端 | Web Dashboard | Agent 活动、协作状态、数据和研究成果可视化 |
| 持久化 | 待定 | Session、任务、事件、Memory、Artifacts |

当前倾向 Spring AI 2.x 和 Spring Boot 4.x 技术线，具体版本需要与 LangGraph4j 进行兼容性验证后再锁定。

### 2.1 关键架构原则

**Spring AI 只作为模型和工具调用的基础层，不采用其封装好的自动 Agent Loop 作为系统默认运行机制。**

**LangGraph4j 负责 Graph Runtime，不负责定义全部 Agent 业务逻辑。**

**Custom Harness 负责单个 Agent 内部的 Model → Tool → Model 执行循环。**

不引入 Spring AI Alibaba Graph，当前也不计划直接采用 LangGraph4j 自带的 ReAct AgentExecutor 作为默认 Agent Loop。

参考 Deep Agents 和 LangGraph4j Deep Agents 的架构与编码工具设计，但不直接移植它们的整套执行体系。

---

## 3. Agent 组织架构

### 3.1 Main Agent

Main Agent 是所有新 Session 的统一入口。

每次用户创建 Session 后，系统将任务交给 Main Agent，由其负责理解用户需求、制定计划和组织团队。

Main Agent 拥有一个 **Agent Catalog**，其中注册固定一级 Agent 的专业职责及能力描述。

Main Agent 可以通过类似 Tool Calling 的机制，让 LLM 自主决定：

- 哪些一级 Agent 需要参与当前任务。
- 分别向它们分配什么工作。
- 哪些工作可以并行。
- 哪些任务存在依赖。
- 何时需要查看阶段性成果。
- 是否需要重新规划或要求返工。

Main Agent 负责全局规划、阶段性成果汇报和团队协调。

Main Agent 不需要参与所有 Subagent 的中间执行步骤，也不需要持续占用 LLM 进行推理。

它可以由任务完成、异常、阶段里程碑等事件唤醒。

### 3.2 Level 1 Agent — 固定专业团队

预计存在 **5–6 个固定一级 Agent**。

数量、名称、职责、人设、工具和具体工作流程尚未最终确定。

一级 Agent 的特点：

- 是长期存在的专业角色。
- 每次任务按需启动，不要求全员参与。
- 拥有独立的 Profile、工具权限和长期 Memory。
- 使用统一的 Custom Harness 执行任务。
- 可以直接与其他一级 Agent 进行受控协作。
- 能够根据任务需要派生多个临时 Subagent。
- 可以将阶段性成果汇报给 Main Agent。

这里“长期存在”指角色身份、配置和记忆持久化，不意味着每个角色都需要常驻一个运行中的模型进程。

### 3.3 Subagent — 动态任务执行者

一级 Agent 可以根据自身工作需要动态创建 Subagent。

例如：

**Web Research**

一级 Agent A 需要分析多个新闻事件，可以同时派生三个 Subagent，分别检索不同新闻、访问不同网站，并提交研究结果。

**Data Processing**

一级 Agent B 需要清洗多张金融数据表，可以派生多个 Subagent，分别调用已有 Python 脚本进行清洗、校验和格式转换。

Subagent 的设计原则：

- 按任务创建，不预设固定数量。
- 拥有独立的临时 Session Context。
- 根据父任务获得受限制的工具和资源。
- 可以并行执行独立任务。
- 可以根据授权请求其他 Agent 协助。
- 完成后向委托者返回结构化结果及 Artifacts。
- 运行实例可以释放，但任务历史和产物需要保留。

Subagent 默认不拥有独立长期 Memory。可复用的经验通过审查后由一级 Agent 的 Memory 系统吸收。

**Subagent 不等于 Python 进程。** 一个 Subagent 可以调用多个工具或 Python Job；一个 Python Job 也可以独立于 Agent 的推理过程运行。

### 3.4 Dynamic Delegation Network

采用动态委托网络，而不是固定的三级树形通信模型。

Main Agent → Level 1 → Subagent 只是典型创建关系。

一级 Agent 之间可以协作、委托、共享结果，Subagent 也可以在授权范围内请求其他 Agent 协助。

所有正式委托必须经过 Workflow 的任务登记、权限校验、预算检查和依赖检查。

避免循环委托、无限创建子任务和资源失控。

---

## 4. Custom Agent Harness

这是项目最重要的自研模块之一。

### 4.1 目标

自行控制单个 Agent 的运行过程，而不是将 Agent 行为完全交给现成框架。

基本执行流程：

    Context Assembly
           ↓
       Model Call
           ↓
       Model Output
           ↓
     Tool Call Validation
           ↓
       Tool Execution
           ↓
     Result Processing
           ↓
     Context / State Update
           ↓
      Stop or Continue

### 4.2 控制范围

Harness 需要允许开发者自定义：

- 每次模型调用的消息与上下文。
- System Prompt 与角色配置装配。
- Session 历史选择与压缩。
- 长期 Memory 的按需检索。
- 每轮提供给模型的 Tool Schema。
- 模型返回的 Tool Call 解析。
- 工具权限、参数校验与执行拦截。
- 工具执行结果的压缩、过滤和回传。
- 模型调用预算、循环次数和停止条件。
- 异常处理、重试及取消。
- Subagent 创建或委托的请求接口。

Harness 不直接管理整个团队的业务任务依赖。

**单 Agent 的内部循环与团队级 Workflow 必须保持分离。**

### 4.3 与 LangGraph4j 的关系

Harness 作为 LangGraph4j Graph Node 中的一种执行能力。

LangGraph4j 负责节点之间的调度及 Graph 状态更新；Harness 负责一个 Agent 内部的实际 LLM 推理与工具循环。

项目不需要重复开发 LangGraph4j 已提供的底层图运行能力。

但 Agent Catalog、动态委托策略、权限继承、Subagent 生命周期等业务机制仍需自行设计。

---

## 5. Workflow 与任务系统

Workflow 使用 LangGraph4j 作为底层 Graph Runtime。

主要负责：

- Agent 任务分配与交接。
- 动态委托和任务依赖管理。
- Agent / Subagent 生命周期。
- 并行执行与条件路由。
- 状态保存、Checkpoint 和恢复。
- 任务暂停、失败处理及取消。
- Main Agent 的全局任务视图。
- 执行事件的记录与通知。

业务 Task 与 Graph State 不应完全混为一体。

长期任务记录、任务所有权、审批和研究产物由独立的业务层维护。

Graph Checkpoint 负责执行流程恢复，不等于长期业务 Memory，也不保证外部 Python Job 自动恰好执行一次。

未来需要通过 Task ID、Job ID、幂等操作及状态校验处理重复执行问题。

---

## 6. Memory System

采用分层 Memory 体系。

### 6.1 Session Memory

每个 Session 独立维护自身上下文。

主要保存：

- 用户原始需求。
- 当前 Session 的任务进展。
- 重要消息与决策。
- Tool 调用及结果引用。
- 阶段性成果。
- Compact Context / Session Summary。
- 后续需要继续执行的内容。

**Session Context 在执行过程中持续更新和压缩。**

Compact Summary 用于降低上下文消耗，不能替代原始消息与事件历史。

### 6.2 Project Memory

用于跨 Session 保存同一个研究 Project 的连续状态。

例如：

- 项目目标和研究假设。
- 数据来源及版本。
- 已完成的研究阶段。
- 关键结论、重要决策和待解决问题。
- Artifacts 与研究报告引用。

**Project Memory 在重要事件发生时更新。**

同一 Project 可以拥有多个 Session，多个 Project 也可以并行执行。

### 6.3 Agent Long-term Memory

Main Agent 与各一级 Agent 拥有自己的长期专业 Memory。

记录：

- 经过验证的专业知识。
- 历史任务经验。
- 常见问题及解决方法。
- 有效的工作流程。
- 可复用的 Skills。
- 自身专业领域积累的方法与约定。

Agent Profile、固定权限与长期 Memory 必须分开。

Memory 不得自行修改 Agent 的身份、权限或系统规则。

### 6.4 Agent Memory 写入机制

由于同一个 Agent 可能同时参与多个 Session / Project，必须防止并发写入覆盖和错误知识污染。

已确定采用：

    Task / Session 完成
             ↓
       Memory Candidate
             ↓
      Memory Consolidator
             ↓
    证据、冲突、重复检查
             ↓
       版本化安全写入
             ↓
      Agent Long-term Memory

多个 Session 可并发读取长期 Memory，但不允许各自直接覆盖长期 Memory。

需要支持版本控制、冲突检测、来源追踪以及必要时的更正和撤回。

**Agent 长期 Memory 在任务结束后提取候选，经过验证再正式写入。**

这不意味着必须等到整个大型 Project 完成后才能积累知识。

### 6.5 Global / Shared Memory

目前没有确定最终内容和权限边界。

初步考虑用于保存整个团队共享、跨角色或跨项目有效的知识，例如统一数据格式、工具使用规范和经过确认的研究方法。

第一阶段先保留相关接口，不建立未经论证的庞大全局记忆库。

### 6.6 Skills

参考 Hermes 和 Deep Agents 的 Skills 机制。

可复用操作方法、专业流程和工具使用技巧可以按需加载，避免将全部知识放进 System Prompt。

Skills 与 Memory 的具体关系、生成方式和审核机制后续讨论。

---

## 7. Python Execution System

Python 是项目的重要计算执行层。

预计编写大量独立 Python 脚本，负责：

- 金融数据获取与清洗。
- 数据结构转换及校验。
- 财务数据分析。
- 统计计算与回归分析。
- 因子研究。
- Beta 稳定性分析。
- 量化回测。
- 图表与研究报告生成。

### 7.1 执行环境

优先考虑本地 Conda / Anaconda 或 venv。

对新生成、未经批准的代码，可以使用独立 Sandbox 进行限制性测试。

Conda/venv 主要负责依赖隔离，不等于安全沙箱。

### 7.2 Runner 架构

Agent 不直接拥有无限制的 Shell 执行权限。

建议采用：

    Agent Tool Call
           ↓
      Tool Gateway
           ↓
      Python Runner
           ↓
     Local Environment
           ↓
       Run Artifacts

Runner 负责：

- 参数校验。
- 环境和脚本选择。
- Python Job 排队。
- 并发、内存及超时控制。
- 执行取消与错误处理。
- 日志及结果收集。
- Job ID / Run ID 管理。

原 Hermes AFTS 项目已经存在独立 Mac Runner、已批准代码快照、代码哈希校验等设计，后续应评估复用程度，而不是默认全部重写。

正式研究任务与 AI 编写的新代码测试，需要不同的权限和运行策略。

### 7.3 Coding Agent

参考 Deep Agents / LangGraph4j Deep Agents 的 Coding Tools 和 Execution Backend 抽象。

未来可以允许特定 Agent：

- 检索与读取代码。
- 创建和修改 Python 脚本。
- 在隔离环境中执行测试。
- 阅读错误并迭代修复。
- 提交代码供审查。

但不能默认允许其直接在 Mac 主机运行未批准代码。

---

## 8. Web Dashboard

Dashboard 是正式产品的一部分，不只是调试界面。

用户希望透明地观察 Agent 团队究竟做了什么，以及它们生成了什么研究成果。

### 8.1 Team Overview

展示：

- Main Agent 与一级 Agent 状态。
- 动态 Subagent 实例。
- 当前任务、任务进度及依赖关系。
- Agent 之间的委托网络。
- 异常、暂停和等待审批的任务。

### 8.2 Agent Activity

支持查看某个 Agent 的完整工作记录，包括：

- 收到的任务。
- 创建的子任务。
- 模型调用和工具调用记录。
- Python Job 执行记录。
- 阶段性结论及产物。
- 错误与返工历史。

### 8.3 Data Explorer

展示实际数据处理结果。

例如一个 Agent 完成数据清洗后，能够查看：

- 原始数据与清洗结果的格式。
- Schema、字段类型、行列数量。
- 数据样本。
- 缺失值与异常值。
- 清洗过程与前后差异。
- CSV / Parquet 等结果文件。

### 8.4 Research Results

展示 Python 生成的分析结果，包括：

- Rolling Beta 和 Beta Stability。
- 回归分析。
- 因子有效性。
- Sharpe Ratio、Drawdown 等指标。
- Python 输出的 PNG、SVG、HTML 图表。
- 研究报告及关联数据。

Dashboard 应从真实的 Task、Event、Job、Artifact 数据获取信息，而不是完全依赖 Main Agent 的自然语言汇报。

因此，从早期阶段就需要建立可追溯的事件记录机制。

---

## 9. 建议的项目文件架构

这是逻辑目录，不是最终 Java Package 设计。

    AFTS/
    │
    ├── backend/                  # Spring Boot / Java
    │   ├── config/               # 模型和应用配置
    │   ├── agents/               # Agent定义、Catalog、实例
    │   ├── harness/              # 自定义Agent Loop
    │   ├── workflow/             # LangGraph4j与业务Workflow
    │   │   ├── graphs/
    │   │   ├── nodes/
    │   │   ├── state/
    │   │   ├── delegation/
    │   │   └── checkpoints/
    │   ├── memory/               # Memory管理和合并
    │   ├── tools/                # Tool接口
    │   ├── execution/            # Python Runner集成
    │   ├── domain/               # 业务数据类型
    │   ├── persistence/          # 数据持久化
    │   ├── observability/        # 事件、指标、审计
    │   └── api/                  # 外部API
    │
    ├── python/
    │   ├── scripts/              # Python研究脚本
    │   ├── runner/               # 本地执行器
    │   ├── environments/         # 环境定义
    │   ├── sandbox/              # 代码隔离测试
    │   └── tests/
    │
    ├── frontend/
    │   ├── team/                 # Agent协作视图
    │   ├── activity/             # 执行时间线
    │   ├── data/                 # 数据预览
    │   ├── research/             # 图表与报告
    │   └── memory/               # Memory审查
    │
    ├── storage/
    │   ├── sessions/
    │   ├── projects/
    │   ├── memory/
    │   ├── tasks/
    │   ├── events/
    │   ├── artifacts/
    │   └── logs/
    │
    ├── config/
    ├── docs/
    ├── tests/
    └── infra/

具体 Java 源代码应遵循标准 Maven / Gradle 项目结构。

storage/ 表示逻辑持久化范围，未来可能由关系数据库、对象存储与文件系统共同承担。

---

## 10. 推荐的开发阶段

### Phase 1 — Core Runtime

确定 Spring AI、LangGraph4j 的版本与集成方式。

验证自定义 Agent Loop 能够作为 LangGraph4j Node 运行，支持完整 Model → Tool → Model 循环。

同时建立最基本的执行事件记录。

### Phase 2 — Python Integration

集成本地 Python Runner。

验证 Tool 调用、参数传递、异步执行、运行结果获取和错误处理。

评估原 Hermes Runner 的复用范围。

### Phase 3 — Dynamic Multi-Agent

实现 Agent Catalog、Main Agent 对一级 Agent 的动态选择、Subagent 创建和跨 Agent 委托。

支持多个任务的并行执行和独立状态管理。

### Phase 4 — Dashboard

实现基础可用的 Web Dashboard。

可查看 Agent 活动、任务状态、Python 结果和分析图表。

### Phase 5 — Memory

建立 Session、Project 和 Agent Memory。

实现上下文压缩、Memory Candidate、Consolidator、版本控制及并发更新验证。

### Phase 6 — Reliability

完善故障恢复、Checkpoint、任务取消、资源限制、人工审批、审计与长期运行稳定性。

开发阶段可根据依赖关系调整，但不要为了快速演示而完全省略早期事件记录和权限边界。

---

## 11. 尚未确定的架构决策

以下问题需要继续与 Coding Agent 讨论，不应由其擅自决定：

1. 固定一级 Agent 的具体数量、职责、人设和权限。
2. Agent Catalog 的定义方式与模型选择协议。
3. Custom Harness 的内部消息类型和 Loop 粒度。
4. LangGraph4j 的 State、Node 和动态子图设计。
5. 跨 Agent 委托采用哪种任务及事件模型。
6. Subagent 生命周期、最大并发及预算分配。
7. Agent Session 与 Project 的关系和恢复策略。
8. Memory 数据模型、持久化方案及检索策略。
9. Global Memory 的范围和权限。
10. Skills 的定义、加载、审核与复用机制。
11. Python Runner 复用、执行接口和 Sandbox 技术。
12. Dashboard 的前端框架及实时事件推送。
13. 实际 Spring AI / LangGraph4j 版本组合。
14. 具体数据存储方案与部署方式。

---

## 12. Coding Agent 工作原则

本项目目前处于架构逐步确定阶段。

Coding Agent 应遵守以下要求：

- 不擅自确定全部一级 Agent 的人设和职责。
- 不预设固定的工具清单及业务流程。
- 不将动态委托网络简化为固定的线性 Graph。
- 不用现成 ReActAgent / AgentExecutor 直接替换 Custom Harness。
- 不重复实现 LangGraph4j 已经提供的底层图执行能力。
- 不将所有 Memory 合并成单个对话历史或 `MEMORY.md`。
- 不让临时 Subagent 直接改写一级 Agent 的长期 Memory。
- 不默认允许 Agent 在主机执行任意 Python 或 Shell 命令。
- 保持 Python Runner、Agent Harness、Workflow 和业务存储之间的独立边界。
- 对存在多个合理实现方案的问题，优先讨论取舍，再确定接口和代码。

已经确定的设计应作为基线；尚未确定的问题应以 Architecture Decision Record（ADR）形式逐项讨论和记录。

---

## 13. 最终目标与验收标准

第一版端到端系统至少应演示以下流程：

    User creates Session
              ↓
         Main Agent
              ↓
       Select Level 1 Agents
              ↓
       Spawn Subagents
              ↓
      Parallel Research / Tools
              ↓
        Local Python Runner
              ↓
       Results and Artifacts
              ↓
       Agent Collaboration
              ↓
      Review and Summarization
              ↓
        Web Dashboard
              ↓
        Memory Updates

需要同时验证：

- 不同 Session / Project 能并行运行。
- 一级 Agent 只在需要时被启动。
- 一级 Agent 可以派生多个 Subagent。
- 多 Agent 委托和工具调用均可追溯。
- Python 产物可以通过 Dashboard 查看。
- Main Agent 能够掌握全局进度并交付阶段成果。
- Context 可以压缩，并保留原始执行记录。
- 长期 Memory 能安全更新，不被并发 Session 覆盖。
- 系统能够暂停、恢复和控制异常任务。

**最终愿景：AFTS 是一个以自定义 Harness 为核心、LangGraph4j 为协作运行时、Python 为研究执行层、分层 Memory 为长期知识基础，并拥有透明可视化界面的自主多 Agent 金融研究平台。**

它不应仅仅是六个具有不同 Prompt 的 Chatbot，而应是一个能够真实分工、执行任务、交付可验证成果，并持续积累专业经验的 AI 团队。
