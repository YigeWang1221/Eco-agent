"""Value at Risk and Expected Shortfall under four distribution assumptions.

Losses are negative returns, so a positive VaR is a loss.
Source method: Info 7374 Lecture01_06 (risk metrics vs distributions).
"""

import argparse
import sys

import numpy as np
from scipy import stats
from scipy.integrate import quad
from scipy.optimize import brentq

from scripts.cli import ToolInputError, read_csv, require_columns, run

MIN_OBSERVATIONS = 30


def historical(losses, confidence):
    var = np.quantile(losses, confidence)
    return var, losses[losses >= var].mean()


def normal(losses, confidence):
    mu, sigma = losses.mean(), losses.std(ddof=1)
    z = stats.norm.ppf(confidence)
    var = mu + sigma * z
    es = mu + sigma * stats.norm.pdf(z) / (1 - confidence)
    return var, es


def student_t(losses, confidence):
    df, loc, scale = stats.t.fit(losses)
    q = stats.t.ppf(confidence, df)
    var = loc + scale * q
    es = loc + scale * ((df + q**2) / (df - 1)) * stats.t.pdf(q, df) / (1 - confidence)
    return var, es, df


def kernel_density(losses, confidence):
    kde = stats.gaussian_kde(losses)
    var = brentq(lambda x: kde.integrate_box_1d(-np.inf, x) - confidence, losses.min(), losses.max())
    upper = losses.max() + 10 * losses.std(ddof=1)
    tail = quad(lambda x: x * kde(x)[0], var, upper, limit=200)[0]
    return var, tail / (1 - confidence)


def risk_metrics(returns, confidence=0.99):
    """VaR / ES table for a 1-D sequence of returns."""
    if not 0.5 < confidence < 1:
        raise ToolInputError("confidence must be between 0.5 and 1")
    losses = -np.asarray(returns, dtype=float)
    if losses.size < MIN_OBSERVATIONS:
        raise ToolInputError(f"need at least {MIN_OBSERVATIONS} returns, got {losses.size}")

    hist_var, hist_es = historical(losses, confidence)
    norm_var, norm_es = normal(losses, confidence)
    t_var, t_es, t_df = student_t(losses, confidence)
    kde_var, kde_es = kernel_density(losses, confidence)
    return {
        "confidence": confidence,
        "n_observations": int(losses.size),
        "methods": {
            "historical": {"var": hist_var, "es": hist_es},
            "normal": {"var": norm_var, "es": norm_es},
            "student_t": {"var": t_var, "es": t_es, "degrees_of_freedom": t_df},
            "kde": {"var": kde_var, "es": kde_es},
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--column", default="return", help="return column, or price column with --from-prices")
    parser.add_argument("--from-prices", action="store_true", help="convert the column from prices to simple returns")
    parser.add_argument("--confidence", type=float, default=0.99)
    args = parser.parse_args(argv)

    def compute():
        frame = read_csv(args.input)
        require_columns(frame, [args.column])
        values = frame[args.column].dropna()
        if args.from_prices:
            values = values.pct_change().dropna()
        return risk_metrics(values, args.confidence)

    return run(compute)


if __name__ == "__main__":
    sys.exit(main())
