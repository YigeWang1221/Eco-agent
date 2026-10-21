# 开发计划

本文件只做**索引**：现在做什么、细节在 `plan/` 的哪一份。不写版本表、目录树、模块规格。那些一律在对应 plan 文件里。

施工约定见 `AGENTS.md`。边界见 `dev-limit.md`。

## 现在做什么

产品：**AFTS**（多 Agent 金融研究平台），放在本仓库。Spring Boot 在 `backend/`。业务行为尚未开始。

## 现行 plan（细节在这些文件）

| 现在做什么 | 文件 | 状态 |
| --- | --- | --- |
| 产品目标、技术路线、Agent 组织、边界 | [plan/afts-base.md](plan/afts-base.md) | 已确认方向 |
| 逻辑目录与模块职责 | [plan/afts-architecture.md](plan/afts-architecture.md) | 已采纳 |
| 目录迁移到 `backend/` 与仓库根空目录 | [plan/afts-layout.md](plan/afts-layout.md) | 完成 |
| 本地单模块脚手架 | [plan/afts-scaffold.md](plan/afts-scaffold.md) | 完成；工程已迁到 `backend/` |
| 安装开发流程文档 | [plan/00-process.md](plan/00-process.md) | 完成 |
| `plan/` 目录说明 | [plan/README.md](plan/README.md) | 完成 |

## 参考（不是施工步骤）

暂无。对照材料写进 `plan/` 之后，在这里加一行路径。

## 停靠点

目录已迁完。单轮 Harness 尚未开始。下一步仍等待用户的施工指令。
