import json

import numpy as np
import pandas as pd
import pytest

from scripts.cli import ToolInputError
from scripts.ols_regression import main, ols_regression


def make_frame(n=1_000, seed=0, rho=0.0, hetero=False, collinear=False):
    rng = np.random.default_rng(seed)
    x1 = rng.normal(size=n)
    x2 = x1 + rng.normal(scale=0.05, size=n) if collinear else rng.normal(size=n)
    noise = rng.normal(size=n) * (np.exp(0.5 * x1) if hetero else 1.0)
    errors = np.zeros(n)
    for t in range(n):
        errors[t] = (rho * errors[t - 1] if t else 0) + noise[t]
    y = 0.5 + 1.2 * x1 - 0.8 * x2 + 0.3 * errors
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def test_recovers_coefficients_and_clean_diagnostics():
    result = ols_regression(make_frame(), "y", ["x1", "x2"])

    coef = result["coefficients"]
    assert coef["const"]["estimate"] == pytest.approx(0.5, abs=0.05)
    assert coef["x1"]["estimate"] == pytest.approx(1.2, abs=0.05)
    assert coef["x2"]["estimate"] == pytest.approx(-0.8, abs=0.05)
    diag = result["diagnostics"]
    assert max(diag["vif"].values()) < 2
    assert diag["breusch_pagan"]["p_value"] > 0.01
    assert diag["durbin_watson"] == pytest.approx(2, abs=0.2)


def test_flags_collinearity():
    vif = ols_regression(make_frame(collinear=True), "y", ["x1", "x2"])["diagnostics"]["vif"]
    assert min(vif.values()) > 10


def test_flags_heteroskedasticity():
    bp = ols_regression(make_frame(hetero=True), "y", ["x1", "x2"])["diagnostics"]["breusch_pagan"]
    assert bp["p_value"] < 0.01


def test_flags_autocorrelation():
    dw = ols_regression(make_frame(rho=0.8), "y", ["x1", "x2"])["diagnostics"]["durbin_watson"]
    assert dw < 1


def test_single_regressor_is_capm_beta():
    frame = make_frame()
    result = ols_regression(frame, "y", ["x1"])
    assert result["coefficients"]["x1"]["estimate"] == pytest.approx(1.2, abs=0.1)
    assert result["diagnostics"]["vif"] == {"x1": 1.0}


def test_rejects_too_few_rows():
    with pytest.raises(ToolInputError):
        ols_regression(make_frame(n=3), "y", ["x1", "x2"])


def test_cli_prints_json(tmp_path, capsys):
    csv = tmp_path / "data.csv"
    make_frame(n=200).to_csv(csv, index=False)

    assert main(["--input", str(csv), "--y", "y", "--x", "x1", "x2"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["n_observations"] == 200
    assert set(out["coefficients"]) == {"const", "x1", "x2"}
