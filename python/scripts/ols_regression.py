"""OLS regression of one y on several x, with standard diagnostics.

Covers CAPM beta (one x) and factor exposure (several x).
Diagnostics: VIF (multicollinearity), Breusch-Pagan (heteroskedasticity),
Durbin-Watson (residual autocorrelation).
Source method: Info 7374 Lecture02_01 to Lecture02_04.
"""

import argparse
import sys

import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

from scripts.cli import ToolInputError, read_csv, require_columns, run


def ols_regression(frame, y_column, x_columns):
    """Fit y ~ const + x and return coefficients plus diagnostics."""
    require_columns(frame, [y_column, *x_columns])
    data = frame[[y_column, *x_columns]].dropna()
    if len(data) <= len(x_columns) + 2:
        raise ToolInputError(f"need more than {len(x_columns) + 2} complete rows, got {len(data)}")

    X = sm.add_constant(data[x_columns], has_constant="add")
    model = sm.OLS(data[y_column], X).fit()

    coefficients = {
        name: {
            "estimate": model.params[name],
            "std_error": model.bse[name],
            "t_value": model.tvalues[name],
            "p_value": model.pvalues[name],
        }
        for name in X.columns
    }
    if len(x_columns) > 1:
        vif = {name: variance_inflation_factor(X.values, i) for i, name in enumerate(X.columns) if name != "const"}
    else:
        vif = {x_columns[0]: 1.0}
    bp_lm, bp_p, _, _ = het_breuschpagan(model.resid, X)

    return {
        "y": y_column,
        "x": list(x_columns),
        "n_observations": int(model.nobs),
        "coefficients": coefficients,
        "r_squared": model.rsquared,
        "adj_r_squared": model.rsquared_adj,
        "residual_std": np.sqrt(model.scale),
        "diagnostics": {
            "vif": vif,
            "breusch_pagan": {"lm_statistic": bp_lm, "p_value": bp_p},
            "durbin_watson": durbin_watson(model.resid),
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--y", required=True, help="dependent column")
    parser.add_argument("--x", required=True, nargs="+", help="one or more regressor columns")
    args = parser.parse_args(argv)
    return run(lambda: ols_regression(read_csv(args.input), args.y, args.x))


if __name__ == "__main__":
    sys.exit(main())
