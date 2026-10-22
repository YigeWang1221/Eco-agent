import json

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from scripts.cli import ToolInputError
from scripts.return_stats import main, return_stats


def test_moments_match_scipy_on_returns():
    rng = np.random.default_rng(0)
    returns = rng.normal(0.0005, 0.01, 500)
    prices = 100 * np.cumprod(np.concatenate([[1.0], 1 + returns]))

    result = return_stats(prices)

    assert result["n_returns"] == 500
    assert result["mean"] == pytest.approx(returns.mean())
    assert result["std"] == pytest.approx(returns.std(ddof=1))
    assert result["skewness"] == pytest.approx(stats.skew(returns, bias=False))
    assert result["annualized_volatility"] == pytest.approx(returns.std(ddof=1) * np.sqrt(252))


def test_rejects_non_positive_prices():
    with pytest.raises(ToolInputError):
        return_stats([100, 0, 101, 102])


def test_cli_prints_json(tmp_path, capsys):
    csv = tmp_path / "prices.csv"
    pd.DataFrame({"date": ["2024-01-03", "2024-01-02", "2024-01-04", "2024-01-05"],
                  "close": [101.0, 100.0, 102.0, 101.0]}).to_csv(csv, index=False)

    assert main(["--input", str(csv)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["start_date"] == "2024-01-02"
    assert out["n_returns"] == 3
    assert out["mean"] == pytest.approx(np.mean([1 / 100, 1 / 101, -1 / 102]))


def test_cli_missing_column_exits_2(tmp_path, capsys):
    csv = tmp_path / "prices.csv"
    pd.DataFrame({"date": ["2024-01-02"], "price": [1.0]}).to_csv(csv, index=False)

    assert main(["--input", str(csv)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing columns" in captured.err
