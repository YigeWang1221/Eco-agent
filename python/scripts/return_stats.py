"""Descriptive statistics of simple returns computed from a price series.

Source method: Info 7374 Lecture01_02 (sample moments).
"""

import argparse
import sys

import numpy as np
from scipy import stats

from scripts.cli import ToolInputError, read_csv, require_columns, run

TRADING_DAYS = 252


def return_stats(prices, periods_per_year=TRADING_DAYS):
    """Moments of simple returns. `prices` is a 1-D sequence ordered in time."""
    prices = np.asarray(prices, dtype=float)
    if np.any(prices <= 0):
        raise ToolInputError("prices must be positive")
    returns = prices[1:] / prices[:-1] - 1
    if returns.size < 3:
        raise ToolInputError("need at least 4 prices")
    std = returns.std(ddof=1)
    return {
        "n_returns": int(returns.size),
        "mean": returns.mean(),
        "std": std,
        "skewness": stats.skew(returns, bias=False),
        "excess_kurtosis": stats.kurtosis(returns, fisher=True, bias=False),
        "annualized_mean": returns.mean() * periods_per_year,
        "annualized_volatility": std * np.sqrt(periods_per_year),
        "min": returns.min(),
        "max": returns.max(),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="CSV with a date column and a price column")
    parser.add_argument("--date-column", default="date")
    parser.add_argument("--price-column", default="close")
    parser.add_argument("--periods-per-year", type=int, default=TRADING_DAYS)
    args = parser.parse_args(argv)

    def compute():
        frame = read_csv(args.input)
        require_columns(frame, [args.date_column, args.price_column])
        frame = frame.sort_values(args.date_column).dropna(subset=[args.price_column])
        result = return_stats(frame[args.price_column], args.periods_per_year)
        result["start_date"] = str(frame[args.date_column].iloc[0])
        result["end_date"] = str(frame[args.date_column].iloc[-1])
        return result

    return run(compute)


if __name__ == "__main__":
    sys.exit(main())
