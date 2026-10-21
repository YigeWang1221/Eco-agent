# 脚手架：本地单模块 Spring Boot

状态：完成。日期：2026-10-21。

产品目标与技术路线见 [afts-base.md](afts-base.md)。逻辑目录见 [afts-architecture.md](afts-architecture.md)。本文件只记这一刀实际落地的工程。

## 目标

在仓库根放一个能编译的 Spring Boot 应用。Spring 上下文在没有网络、没有 API key 的情况下能启动。LangGraph4j 1.9.x 与 Spring AI 2.0.1 在 classpath 上可解析。

## 不做

- Agent 行为、ReActAgent、自研 Harness 循环
- Workflow 图、Checkpoint、暂停恢复
- Memory、Python Runner、Dashboard、业务 API
- 多模块 reactor、`frontend/`、`python/`、`storage/`、`infra/`
- Docker、模型调用、真实密钥

## 钉死的版本

查询 Maven Central 时，LangGraph4j 1.9 线最新发布是 **1.9.6**（2026-10-18）。其父 POM `org.bsc.langgraph4j:langgraph4j-parent:1.9.6` 的 `spring-ai.version` 为 **2.0.1**，与本步 Spring AI 一致。没有改用其它补丁。

| 项 | 坐标或值 |
| --- | --- |
| 语言 | Java 21（`java.version` = 21；本机编译器 Temurin 21.0.7） |
| 构建 | Maven 单模块。`groupId` `afts`，`artifactId` `afts`，`version` `0.0.1-SNAPSHOT` |
| Spring Boot | `org.springframework.boot:spring-boot-starter-parent:4.1.1` |
| Spring AI | BOM `org.springframework.ai:spring-ai-bom:2.0.1`；直接依赖 `spring-ai-client-chat`（解析为 2.0.1） |
| LangGraph4j | `org.bsc.langgraph4j:langgraph4j-core:1.9.6` |
| LangGraph4j Spring AI | `org.bsc.langgraph4j:langgraph4j-spring-ai:1.9.6` |
| 测试 | `spring-boot-starter-test`（版本由 Boot 父 POM 管理） |

`pom.xml` 里 LangGraph4j 使用属性 `langgraph4j.version` = `1.9.6`，不是版本范围。没有加入 Spring AI Alibaba，也没有加入 `spring-ai-starter-model-*`。

## 创建了什么

仓库根就是产品，没有嵌套 `AFTS/` 目录。

- `pom.xml`
- `.gitignore`（Maven / IDE / `.env`；不忽略源码）
- `src/main/java/afts/AftsApplication.java`
- `src/main/resources/application.yml`（只有 `spring.application.name: afts`）
- `src/test/java/afts/AftsApplicationTest.java`
- 空包，各只有 `package-info.java`：`afts.config`、`afts.agents`、`afts.harness`、`afts.workflow`、`afts.memory`、`afts.tools`、`afts.execution`、`afts.domain`、`afts.persistence`、`afts.observability`、`afts.api`

应用使用 `spring-boot-starter`，不打开 Web 端口。测试用 `@SpringBootTest` 启动上下文，并用类字面量确认 `StateGraph`、`SpringAIStateSerializer`、`ChatClient` 在 classpath 上。测试不实例化模型，不发网络请求。

## 完成定义

- `mvn -B compile test` 退出码 0。
- 测试 `afts.AftsApplicationTest`：Tests run: 1, Failures: 0, Errors: 0, Skipped: 0。
- 启动日志含 `Spring Boot :: (v4.1.1)`，且 `application.yml` 中没有密钥。

## 仍未做

业务行为都还没有。下一步等待用户点名下一段施工。多模块如何映射逻辑目录仍不固定。
