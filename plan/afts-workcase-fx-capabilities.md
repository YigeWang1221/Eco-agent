# Work case 能力清单：FX 区间预测

状态：草案，待用户确认。未施工。日期：2026-10-21。

从 [afts-workcase-fx.md](afts-workcase-fx.md) 的流程推出。每项标注已有、新建或后置。类名与接口签名不在此锁定。

## 三类能力的分工

| 类型 | 在 AFTS 里是什么 | 管什么 |
| --- | --- | --- |
| Tool | Agent 可调用的确定性操作：Python 脚本（经 Runner）与后端工具 | 算数、读写文件、发消息、git |
| Skill | 按需加载、写给 Agent 看的团队规矩 | 禁止事项、交付契约、协作约定。不写具体方法 |
| MCP | 外部系统连接 | 第一版不用 |

工具有哪些、参数是什么，由工具 schema 告诉模型，不写进 Skill。

## Python Tool

沿用 [afts-python-tools.md](afts-python-tools.md) 的约定：`python -m scripts.<工具>`，结果为 stdout 上的一个 JSON，输入错误退出码 2，错误写 stderr；计算与命令行分开，pytest 覆盖。

| 工具 | 状态 | 输入 | 输出 | 使用者 |
| --- | --- | --- | --- | --- |
| `return_stats` | 已有 | 价格 CSV | 收益分布统计 | 数据工程师、量化 |
| `risk_metrics` | 已有 | 收益 CSV、置信度 | VaR / ES（含 Student-t） | 数据工程师、量化、审查员 |
| `ols_regression` | 已有 | CSV、y、x 列表 | 系数与诊断 | 宏观研究员、量化 |
| `fx_import` | 新建 | `inbox/` 中的一个文件 | 写入 `data/raw`，来源记录 JSON（哈希、行数、列、时间范围） | 数据工程师 |
| `fx_bars` | 新建 | `data/raw`、频率 `1h`/`1d` | 对齐到 UTC 的 OHLC，日线按纽约 17:00 收盘；缺口与异常清单 | 数据工程师 |
| `fx_features` | 新建 | K 线、特征菜单中的名字 | 特征表（收益滞后、滚动波动、动量等） | 量化 |
| `interval_baseline` | 新建 | 特征表、覆盖率目标 | 基准区间模型（分位数回归或 conformal）与模型产物 | 量化 |
| `eval_run` | 新建，**锁定** | 模型产物、`eval/` 配置、段别 | 覆盖率、宽度、interval score、Kupiec 检验；自动写入台账 | 验证段：量化；测试段：仅系统 |
| `predict_next` | 新建 | 上线模型、最新 K 线 | 向 `predictions/` 追加一条 | 仅快循环定时任务 |

`eval_run` 的测试段模式只有阶段 6 的系统流程能调用，任何 Agent 角色都没有该权限。

### 后置

- `fx_fetch`：从免费 API 拉新 K 线放进 `inbox/`，供 `advance` 使用。数据源未选，见 work case「待用户决定」第 5 条。
- 宏观序列导入（如利率、CPI）：数据源与条款待定。
- 新闻信号工具（事件日历、鹰鸽打分）：新闻源待定。
- 菜单外的模型（树模型、LSTM 等）：在第二版开放 Sandbox 写代码之后。

## 后端 Tool

落在 `backend/tools`，权限校验在 `harness/policies` 与 workflow。

| 工具 | 作用 | 使用者 |
| --- | --- | --- |
| 项目文件读写 | 限定 Project 根目录，按角色与目录校验 | 全部 Agent |
| 运行 Python | 经 Runner 运行已批准脚本，返回 Job ID 与结果 | 按工具表授权 |
| Sandbox 执行 | 运行 Agent 写的代码，隔离于主机 | 第一版不开放；第二版开放给数据工程师与量化 |
| 发消息 | `task`、`result`、`question`、`review`，经 Workflow 登记 | 全部 Agent |
| 派生 Subagent | 经准入控制（配额、API 余量、预算） | 一级 Agent |
| 请求用户 | 关卡确认、补问参数 | Main |
| git | `init`、`commit`、`tag`；`revert` 需用户确认 | 仅 Main |

## Skill

第一版是开发者写的底线，很薄。被实验证明有效的做法经 Memory Candidate → Consolidator → 用户批准后，再沉淀为经验型 Skill。

| Skill | 给谁 | 内容 |
| --- | --- | --- |
| `project-conventions` | 全部 Agent | 目录与读写权限、Run ID 规则、消息类型、何时提问而不是猜 |
| `data-intake-contract` | 数据工程师 | 禁止：删改原始数据、用未来值补缺。清洗报告必须回答：分布与尾部、波动聚集、平稳性、缺口与异常处理、结构突变；每个结论附 Run ID，说明为何选该方法 |
| `experiment-discipline` | 量化 | 只看验证段；每次运行进台账；必须与基准比较；预算到即停；不删失败实验 |
| `review-checklist` | 审查员 | 常见泄漏与作弊：未来信息、时区错位、漏算成本、多次试验只挑最好、测试段被多次使用；同时检查考场是否偏离 `eval-standards` |
| `eval-standards` | 全部只读 | 考场采用的业界标准及理由：walk-forward / 滚动样本外切分；覆盖率、宽度、interval score / pinball loss；Kupiec 覆盖率检验；按交易对设点差，隔夜持仓计 swap |

Skill 写「必须回答什么、不能做什么」，不写「按什么步骤做」。方法由 LLM 决定，好坏由考场判断。

## MCP

第一版不接。数据全部由用户导入。

后续候选（均需先核对条款）：FX 行情 API、经济日历、新闻源。

## 薄切 1 用到的最小集合

导入 → 清洗 → 基准区间模型 → 考场评分，只需要：`fx_import`、`fx_bars`、`fx_features`、`interval_baseline`、`eval_run`，加上已有的三个工具。不需要后端 Tool、Skill 与 MCP。
