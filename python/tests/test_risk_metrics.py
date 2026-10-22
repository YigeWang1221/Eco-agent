import json

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from scripts.cli import ToolInputError
from scripts.risk_metrics import main, risk_metrics


@pytest.fixture
def normal_returns():
    return np.random.default_rng(1).normal(0.0, 0.01, 20_000)


def test_normal_method_matches_closed_form(normal_returns):
    result = risk_metrics(normal_returns, 0.99)["methods"]["normal"]

    z = stats.norm.ppf(0.99)
    sigma = normal_returns.std(ddof=1)
    mu = -normal_returns.mean()
    assert result["var"] == pytest.approx(mu + sigma * z)
    assert result["es"] == pytest.approx(mu + sigma * stats.norm.pdf(z) / 0.01)


def test_all_methods_agree_on_normal_data(normal_returns):
    methods = risk_metrics(normal_returns, 0.99)["methods"]
    true_var = 0.01 * stats.norm.ppf(0.99)
    true_es = 0.01 * stats.norm.pdf(stats.norm.ppf(0.99)) / 0.01

    for name, values in methods.items():
        assert values["var"] == pytest.approx(true_var, rel=0.05), name
        assert values["es"] == pytest.approx(true_es, rel=0.07), name
        assert values["es"] > values["var"], name


def test_fat_tails_raise_t_var_above_normal():
    returns = stats.t.rvs(3, scale=0.01, size=20_000, random_state=2)
    methods = risk_metrics(returns, 0.99)["methods"]

    assert methods["student_t"]["degrees_of_freedom"] == pytest.approx(3, abs=0.5)
    assert methods["historical"]["es"] > methods["normal"]["es"]


def test_rejects_short_series():
    with pytest.raises(ToolInputError):
        risk_metrics(np.zeros(10))


def test_cli_from_prices(tmp_path, capsys):
    rng = np.random.default_rng(3)
    prices = 100 * np.cumprod(1 + rng.normal(0, 0.01, 300))
    csv = tmp_path / "prices.csv"
    pd.DataFrame({"close": prices}).to_csv(csv, index=False)

    assert main(["--input", str(csv), "--column", "close", "--from-prices", "--confidence", "0.95"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["n_observations"] == 299
    assert out["confidence"] == 0.95
    assert set(out["methods"]) == {"historical", "normal", "student_t", "kde"}
