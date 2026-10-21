# Base plan：AFTS

状态：方向已确认。Java 21、Maven、Spring Boot 4.1.1、Spring AI 2.0.1 已确认。LangGraph4j 补丁 1.9.6 记在 [afts-scaffold.md](afts-scaffold.md)。未写业务代码。日期：2026-10-21。

文件架构见 [afts-architecture.md](afts-architecture.md)。本文件不重复目录树。

## 最终目的

做一个可持续扩展的多 Agent 金融研究平台（**AFTS**），放在本仓库 `Eco_agent`。

Main Agent 统一接收用户请求，按任务动态选择固定的一级专业 Agent，并允许各 Agent 派生临时 Subagent，做网页研究、数据处理、本地 Python 计算。系统支持多 Session、多 Project 并行，具备持久化记忆、动态任务委托、执行控制、研究产物管理和可视化 Dashboard。

原则：**Agent 负责推理与决策，系统负责状态管理、权限校验、资源调度和可靠执行。**

不绑定某一个封装好的 Agent 框架或预设工作流。

## 技术路线

**不上** Spring AI Alibaba Graph。**不用**框架封装的 ReActAgent 当默认 Agent Loop。

```text
Frontend / Dashboard
        ↓
Spring Boot 应用层（API、配置、权限、业务服务）
        ↓
LangGraph4j 1.9.x — Workflow Runtime
  图状态 · 条件路由 · 并行 · Checkpoint · 暂停/恢复
        ↓
Custom Agent Harness（自研 Model → Tool → Model）
  Context / Memory / Tool / Budget / Stop
        ↓
Spring AI ChatModel          Tool / Python Runner
```

LangGraph4j 提供状态图、条件边、并行节点、子图、Checkpoint、暂停恢复。Agent Catalog、动态派生、权限继承、任务委托和循环依赖检测仍在 Workflow 业务层自行设计，叠在图引擎之上，不重复实现图执行内核。

| 类别 | 状态 | 说明 |
| --- | --- | --- |
| 应用框架 | **已锁定** | Spring Boot **4.1.1** |
| 模型 / 消息 / 工具 | **已锁定** | Spring AI **2.0.1** 的模型、消息和工具接口。脚手架不注册可用模型 |
| Workflow Runtime | **已锁定** | LangGraph4j **1.9.6**（1.9.x 线上最新补丁；父 POM 的 `spring-ai.version` 为 2.0.1）。坐标见 [afts-scaffold.md](afts-scaffold.md) |
| Agent 循环 | **已锁定** | 自研 Custom Harness |
| 图运行时排除 | **已锁定** | 不上 Spring AI Alibaba Graph；不用 ReActAgent 当默认循环 |
| 1.8 LTS 对比 | **不做** | 主线只用 1.9.x，不再做 1.8 对比测试 |

用户已按下列选型下令搭建脚手架，不再标待确认：

| 类别 | 值 | 状态 |
| --- | --- | --- |
| 语言 | Java 21 | 已确认 |
| 构建 | Maven | 已确认。多模块如何映射 `backend/` 仍不固定；脚手架用单模块 |
| Spring Boot | 4.1.1 | 已确认 |
| Spring AI | 2.0.1 | 已确认 |

## Agent 组织

采用 **Dynamic Delegation Network**。Main Agent 负责全局管理。Agent 之间不强制只能按固定树形路径通信。支持跨角色委托、并行执行、任务依赖、返工与重新规划。所有正式任务与委托必须经过统一 Workflow 记录、校验与跟踪。

### Main Agent

- 每个新 Session 首先进入 Main Agent。
- 读取用户目标及相关 Session、Project 和长期 Memory。
- 通过 Agent Catalog 查看固定一级 Agent 的职责及能力。
- 按任务动态选择需要启动的一级 Agent，不要求全部参与。
- 负责全局任务规划、阶段性成果汇总、异常协调和用户汇报。
- 可以重新调整任务安排，但必须遵守系统权限及审批规则。

### Level 1 Agent

- 固定约 5–6 个核心角色。具体身份、职责和数量后续讨论。
- 各自拥有独立的角色配置、工具权限、Session Context 和长期 Memory。
- 根据 Main Agent 的任务分配按需启动。
- 可以在权限范围内与其他一级 Agent 协作或委托任务。
- 能够根据工作需要动态启动多个 Subagent。

### Subagent

- 按需创建，不预设固定数量。
- 适合独立、可并行的工作，例如多个网页检索、不同数据表清洗、Python 分析。
- 每个 Subagent 拥有独立的临时执行上下文。
- 通过受控工具执行具体工作，返回结果、日志及研究产物。
- 任务完成后可以释放运行实例，保留必要记录。
- 默认不拥有独立的长期 Memory，可将经验候选提交给上级 Agent。

## 项目边界

做（方向已定，实现另开施工计划）：

- 产品为 AFTS。栈为 Spring Boot 4.1.1 + Spring AI 2.0.1 + LangGraph4j 1.9.6 + 自研 Harness。
- 施工计划只写 `plan/`。

后置（见 [afts-architecture.md](afts-architecture.md) 的「暂不固定」）：

- 一级 Agent 人设、Catalog 接口、Subagent 并发上限与预算
- Workflow 事件模型、存储选型、向量检索是否上
- Dashboard 前端框架与推送方式
- Python Runner 协议、隔离与是否复用 Hermes
- 账号、计费、对外部署

不做：

- Alibaba Graph
- 用框架封装的 ReActAgent 当默认 Agent Loop
- 在 Harness 里再实现一套图执行引擎
- 在本文件展开脚手架目录或版本表（见 [afts-scaffold.md](afts-scaffold.md)）
