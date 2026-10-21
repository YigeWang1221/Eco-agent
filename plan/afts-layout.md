# 目录迁移

状态：完成。日期：2026-10-21。

产品目标见 [afts-base.md](afts-base.md)。目录职责见 [afts-architecture.md](afts-architecture.md)。脚手架版本见 [afts-scaffold.md](afts-scaffold.md)。

## 目标

把单模块 Spring Boot 从仓库根移到 `backend/`，包树与已确认的目录一致。仓库根保留 `python/`、`frontend/`、`storage/`、`docs/` 的空目录。

## 不做

- 不写单轮 Harness，不接模型，不发网络。
- 不实现 Workflow、Memory、Python、Dashboard。
- 不拆 Maven 多模块。
- 不创建 `frontend` 子视图目录、`storage` 子目录、`python/environments`、根上的 `config/`、`tests/`、`infra/`。
- 不改依赖版本。

## 物理路径

仓库根就是产品。流程文档留在根上。

`backend/` 子目录对应 `backend/src/main/java/afts/` 下的包，每个包只有 `package-info.java`：

- `config`、`agents`、`memory`、`tools`、`execution`、`domain`、`persistence`、`observability`、`api`
- `harness`，以及 `harness.runtime`、`harness.context`、`harness.policies`
- `workflow`，以及 `workflow.graphs`、`workflow.nodes`、`workflow.state`、`workflow.delegation`、`workflow.checkpoints`

`pom.xml`、`AftsApplication`、`application.yml`、`AftsApplicationTest` 在 `backend/`。仓库根不再有 `pom.xml` 和 `src/`。

空目录用 `.gitkeep` 保住：`python/scripts`、`python/runner`、`python/sandbox`、`frontend`、`storage`、`docs`。

## 完成定义

- 上面的路径都在。
- 在 `backend/` 执行 `mvn -B compile test` 退出码为 0。
