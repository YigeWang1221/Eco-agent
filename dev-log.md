# 开发日志

只记已经发生的事实。动机和未决问题写在 `dev-recoding.md`。每条使用下面的格式。

```text
日期：
指令：用户要求做什么
结果：实际落地了什么
验证：命令或检查；没做就写「未运行」
偏差：和指令不一致的地方；没有就写「无」
```

## 2026-10-21 · 建立工作方式

- 日期：2026-10-21
- 指令：安装软件开发的标准流程。建立 `AGENTS.md`、`dev-plan.md`、`dev-log.md`，以及 `plan/`。`dev-plan.md` 只记录大体进行到哪一步，每一步的计划放在 `plan/`。不写功能代码。
- 结果：新增 `AGENTS.md`、`dev-plan.md`、`dev-log.md`、`dev-limit.md`、`dev-recoding.md`、`plan/README.md`、`plan/00-process.md`，以及始终生效的 `.cursor/rules/dev-process.mdc`。仓库内没有应用代码。
- 验证：未运行。本步没有可执行程序。
- 偏差：无。文件名用 `AGENTS.md`（Cursor 会加载），其余流程文件用连字符：`dev-plan.md`、`dev-log.md`、`dev-limit.md`、`dev-recoding.md`。

## 2026-10-21 · 写入 AFTS 架构

- 日期：2026-10-21
- 指令：把 AFTS 架构讨论稿和 LangGraph4j 1.9.x 的决定写入 `plan/`，并只更新流程索引与边界。不创建源码目录，不搭 Spring 工程。
- 结果：新增 `plan/afts-base.md`、`plan/afts-architecture.md`。`dev-plan.md` 改为索引 AFTS 与这两份 plan。`plan/README.md`、`AGENTS.md`、`dev-limit.md`、`dev-recoding.md` 同步。未建 `backend/` 等目录，未改 `MAIC_learning/re-built-try`。
- 验证：未运行。本步只有文档。
- 偏差：无。Java 21、Maven、Spring Boot 4.1.1、Spring AI 2.0.1 写成沿用待确认，没有当成新锁定。LangGraph4j 只锁定 1.9.x，没有写死补丁号。

## 2026-10-21 · 本地脚手架

- 日期：2026-10-21
- 指令：按 `plan/afts-base.md` 的技术选型搭建本地项目脚手架。只搭工程。把原先「沿用待确认」的 Java 21、Maven、Spring Boot 4.1.1、Spring AI 2.0.1 视为已确认。LangGraph4j 钉 1.9.x 的精确补丁。不实现 Agent、Harness、Workflow、Memory、Python Runner、Dashboard 或业务 API。不提交。
- 结果：仓库根新增单模块 `pom.xml`、`AftsApplication`、`application.yml`、`.gitignore`、上下文测试，以及 `afts` 下 11 个只有 `package-info.java` 的包。Spring Boot 父 POM `4.1.1`，Spring AI BOM `2.0.1`，直接依赖 `spring-ai-client-chat`。LangGraph4j 钉 `langgraph4j-core` 与 `langgraph4j-spring-ai` 的 `1.9.6`（Maven Central 上 1.9 线最新发布；父 POM `spring-ai.version` 为 2.0.1）。新增 `plan/afts-scaffold.md`。`plan/afts-base.md` 中上述四项改为已确认，Workflow Runtime 补丁写为 1.9.6。`dev-plan.md` 与 `plan/README.md` 只加索引。未改 `dev-limit.md`。
- 验证：`mvn -B compile test`（工作目录仓库根，允许访问 Maven Central）退出码 0。`BUILD SUCCESS`。`afts.AftsApplicationTest`：Tests run: 1, Failures: 0, Errors: 0, Skipped: 0。日志含 `Spring Boot :: (v4.1.1)`，`Started AftsApplicationTest`。随后 `mvn -B dependency:tree -Dincludes=org.springframework.ai:*,org.bsc.langgraph4j:*` 退出码 0，解析为 `spring-ai-client-chat:2.0.1`、`spring-ai-model:2.0.1`、`spring-ai-commons:2.0.1`、`langgraph4j-core:1.9.6`、`langgraph4j-spring-ai:1.9.6`。
- 偏差：无。未注册模型 starter，未调用模型。

## 2026-10-21 · 目录迁移

- 日期：2026-10-21
- 指令：只做目录迁移。Spring Boot 放到 `backend/`，仓库根按新树留下 `python/`、`frontend/`、`storage/`、`docs/`。先不做单轮 Harness。
- 结果：`pom.xml` 与源码迁到 `backend/`。包为 `afts.config`、`afts.agents`、`afts.harness` 及其 `runtime`、`context`、`policies`，`afts.workflow` 及其 `graphs`、`nodes`、`state`、`delegation`、`checkpoints`，以及 `memory`、`tools`、`execution`、`domain`、`persistence`、`observability`、`api`。每个包只有 `package-info.java`。仓库根不再有 `pom.xml` 和 `src/`。空目录用 `.gitkeep` 保住。新增 `plan/afts-layout.md`，并改了 `plan/afts-architecture.md` 的目录树。未改依赖版本，未写 Harness 行为。
- 验证：在 `backend/` 执行 `mvn -B clean test`，退出码 0，`BUILD SUCCESS`。编译 20 个主源文件、1 个测试。`afts.AftsApplicationTest`：Tests run: 1, Failures: 0, Errors: 0, Skipped: 0。日志含 `Spring Boot :: (v4.1.1)`。
- 偏差：无。

## 2026-10-21 · Python 基础工具

- 日期：2026-10-21
- 指令：从 `/Users/eric/Documents/MSIS/Info 7374 Trading/code` 找量化分析与因子代码，做成工具放进 `python/`。环境用 Anaconda，conda env 名为 `fina-tech`，版本固定；上线后由用户选择环境。
- 结果：课程目录只有 Lecture1–2 共 11 个 notebook，无因子代码（只读，未改）。新增 `plan/afts-python-tools.md`；`python/scripts/` 下 `cli.py`、`return_stats.py`、`risk_metrics.py`、`ols_regression.py`；`python/tests/` 三个测试文件；`python/pytest.ini`、`environment.yml`、`pinned-versions.txt`。创建 conda env（先名 `afts-tools`，按用户中途指令 `conda rename` 为 `fina-tech`）。`.gitignore` 加 Python 缓存。删除 `python/scripts/.gitkeep`。`dev-plan.md`、`plan/README.md` 只改索引。
- 验证：`/opt/anaconda3/envs/fina-tech/bin/python -m pytest -q`（在 `python/`）：16 passed。首次运行 2 个失败，均为测试本身问题（一处手算期望值错误；异方差合成数据对称，Breusch-Pagan 测不出），修正后通过。手动 CLI 冒烟：三个工具对合成 CSV 均退出码 0 并输出 JSON，CAPM 合成真值 beta 1.3，估计 1.303；缺列时退出码 2，stderr 有错误信息。
- 偏差：新增 `python/tests/` 目录（`afts-layout.md` 未列出，也未禁止）。

## 2026-10-21 · FX work case 草案

- 日期：2026-10-21
- 指令：经头脑风暴后输出 work case 的 plan；随后要求在主目录 `workflow-design-1` 上按两份草案更新。
- 结果：新增 `plan/afts-workcase-fx.md`（模板参数、阶段与关卡、Project 目录与读写权限、git 规则、导入、通信、返工、插话、唤醒、资源控制、考场与前向比较、待决定、完成定义）与 `plan/afts-workcase-fx-capabilities.md`（Python Tool、后端 Tool、Skill、MCP）。`dev-plan.md`、`plan/README.md` 只加索引并改停靠点。两份草案先在会话 worktree 起草，再复制到主目录；主目录其余改动用脚本做精确替换。未写代码，未改 `.gitignore`，未提交。
- 验证：未运行。本步只有文档。
- 偏差：无。
