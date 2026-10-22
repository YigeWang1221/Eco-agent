# Python 基础工具（草案）

状态：完成。日期：2026-10-21。

产品目标见 [afts-base.md](afts-base.md)。目录职责见 [afts-architecture.md](afts-architecture.md)。

## 题目

把用户课程代码 `/Users/eric/Documents/MSIS/Info 7374 Trading/code` 里已验证过的量化方法，整理成 `python/scripts/` 下可单独运行、可测试的工具。之后 Agent 通过 Runner 调用它们，work case 也围绕它们设计。

## 来源盘点（只读）

该目录只有 Lecture1、Lecture2 共 11 个 notebook，没有因子研究代码。

| notebook | 可提炼的方法 | 是否做成工具 |
| --- | --- | --- |
| L01_02 moments | 收益率均值、标准差、偏度、峰度 | 是 → `return_stats` |
| L01_06 risk metrics | VaR / ES：历史法、正态、Student t、KDE | 是 → `risk_metrics` |
| L02_01 OLS | 手写 OLS 与 statsmodels 对照 | 是 → `ols_regression` 的核心 |
| L02_02 多重共线性 | 相关矩阵（notebook 未算 VIF） | 是 → 并入 `ols_regression` 诊断 |
| L02_03 异方差 | OLS vs GLS | 是 → 并入诊断（Breusch-Pagan，新增） |
| L02_04 自相关 | Durbin-Watson、残差 ACF | 是 → 并入诊断 |
| L01_01、03、04、05、07 | 缩放、分布演示、KDE 画图、多元正态 | 否，教学演示，无独立输出 |

## 拟建工具

| 工具 | 输入 | 输出 |
| --- | --- | --- |
| `return_stats` | 价格 CSV（date, close） | 日收益的 n、均值、标准差、偏度、峰度、年化波动 |
| `risk_metrics` | 收益 CSV，置信度 | 四种方法的 VaR 与 ES 对照表 |
| `ols_regression` | CSV，y 列名，x 列名列表 | 系数、t 值、R²，以及 VIF、Breusch-Pagan、Durbin-Watson |

`ols_regression` 让一个 y 对多个 x 回归，所以 CAPM beta、Fama-French 因子暴露都用它表达，不单独建 beta 工具。

## 统一约定

- 命令行调用：`python -m scripts.<工具> --input <csv> [参数]`，结果以一个 JSON 打到 stdout，失败时非零退出码并把错误写 stderr。
- 工具只读本地文件，不联网，不下载数据。
- 计算与命令行分开：每个工具一个纯函数，供测试直接调用。
- 不画图。图表后面单独做。
- 测试：pytest，数据用固定种子合成，并以 statsmodels / scipy 的结果或已知解析值作对照。

## Python 环境（已确认）

- 开发用 Anaconda：conda 环境 `fina-tech`，Python 3.12。定义文件 `python/environment.yml`，装好后的实际版本写入 `python/pinned-versions.txt`。
- 依赖：numpy、pandas、scipy、statsmodels、pytest。
- 产品上线后由用户自己选择解释器或环境。因此工具代码不依赖 conda 特性，不硬编码解释器路径；以后 Runner 通过配置拿到解释器，本步不做这项配置。

## 仍待决定

1. **数据来源**：notebook 用 yfinance。Hermes 调研结论是 Yahoo 条款禁止自动化获取。本步工具只吃 CSV；拉数据的工具另开一步再定来源。
2. **因子代码**：课程目录里没有。如在别处，另开一步纳入。

## 完成定义

- 三个工具各有纯函数、命令行入口和 pytest 测试。
- 在 `python/` 下执行 `pytest` 全部通过。
- 用一份合成 CSV 手动跑每个工具，拿到 JSON 输出。

## 不做

- 不接 Java、Runner、Agent。
- 不拉网络数据，不做因子库，不做回测。
- 不复制 notebook 原文；按方法重写。
- 不改课程目录里的任何文件。

## 实际落地

- `python/scripts/cli.py`：三个工具共用的命令行约定（读 CSV、查列、JSON 输出、输入错误退出码 2）。
- `python/scripts/return_stats.py`、`risk_metrics.py`、`ols_regression.py`。
- `python/tests/`：16 个测试。`python/pytest.ini` 设 `pythonpath = .`。
- `python/environment.yml` 钉精确版本；`python/pinned-versions.txt`：Python 3.12.15、numpy 2.5.4、pandas 3.0.6、scipy 1.18.1、statsmodels 0.15.0、pytest 9.1.1。
- 运行：在 `python/` 下 `conda run -n fina-tech python -m pytest`。
