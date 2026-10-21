# 开发实录

这里记过程：用户要什么、当时怎么理解、放弃过什么、还没定什么。它不是变更清单；变更清单在 `dev-log.md`。

一条实录回答四件事：

1. 用户这一步的原意。
2. 实际采用的理解。
3. 故意没做的选择。
4. 留给用户决定的问题。

## 2026-10-21 · 建立工作方式

用户要先把软件开发的标准流程装进空仓库 `Eco_agent`：`AGENTS.md`、`dev-plan.md`、`dev-log.md`、`plan/`，以及同一套里的其余文件。`dev-plan.md` 只标明现在大体到哪一步，每一步的计划放在 `plan/`。

采用的理解：分工与 `MAIC_learning/re-built-try` 的后期约定相同，文件名按本次口令用连字符，代理入口用 Cursor 会加载的 `AGENTS.md`。本步只建立流程，不选定产品行为。

故意没做：不写产品目标，不锁技术栈，不搭工程，不写应用代码，不把 AFTS 或 TypeScript 实验的阶段计划抄进来。

留给用户：Eco_agent 的一句话目标，以及第一段要跑通的可观察行为。

## 2026-10-21 · 写入 AFTS 架构

用户给出 AFTS 架构讨论稿，并决定用 LangGraph4j 1.9.x、自研 Harness、不用 Alibaba Graph、不用 ReActAgent 当默认循环。Workflow 业务保留自研，不重复开发图执行内核。

采用的理解：本仓库就是 AFTS。本步只把已确认方向写入 `plan/afts-base.md` 与 `plan/afts-architecture.md`，索引和边界跟着改。讨论稿里仍开放的接口、存储、前端和一级 Agent 人设留在「暂不固定」。

故意没做：不建目录，不搭工程，不把旁支计划里的 Java 21、Maven、Spring Boot 4.1.1、Spring AI 2.0.1 写成新锁定，不钉 LangGraph4j 的补丁号，不改 `re-built-try`。

留给用户：是否确认那四项沿用版本，以及下一条施工从哪一段开始。

## 2026-10-21 · 本地脚手架

用户要求按 `plan/afts-base.md` 已写的技术选型搭本地脚手架，并把它当作对原先「沿用待确认」四项的确认。

采用的理解：仓库根本身就是应用。单模块足够，因为多模块如何映射 `backend/` 仍未固定。LangGraph4j 取 Central 上 1.9 线最新的 1.9.6，原因是其父 POM 把 Spring AI 标成 2.0.1，和已确认的 Spring AI 一致。同时放入 `langgraph4j-core` 与 `langgraph4j-spring-ai`。Spring AI 只引 `spring-ai-client-chat`，让消息和 ChatClient 类型在 classpath 上，上下文不要求模型密钥。测试只启动上下文并触碰这三个类的类字面量。

故意没做：不建多模块 reactor，不加 Web starter，不加模型 starter，不写图、循环、Memory、Python、Dashboard 或业务 API，不加 Docker，不提交。

留给用户：下一条施工从哪一段开始。

## 2026-10-21 · 只迁移目录

用户要求按新的目录树搬家，并明确先不做「单轮可观察行为」那一段。

采用的理解：仓库根就是 AFTS。`backend/` 是 Maven 工程，图里的子目录是 `afts.*` 包。`python/`、`frontend/`、`storage/`、`docs/` 只建空目录。流程文档留在根上。

故意没做：不写 Harness 循环，不把前端视图或 storage 再拆成子目录，不改版本，不提交。

留给用户：下一条施工指令。
