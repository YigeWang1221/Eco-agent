"""Shared command-line contract for AFTS tools.

Every tool reads a local CSV, prints one JSON object to stdout on success,
and exits non-zero with a message on stderr on failure.
"""

import json
import math
import sys
from pathlib import Path

import pandas as pd

EXIT_BAD_INPUT = 2


class ToolInputError(ValueError):
    """Input the caller can fix: missing file, missing column, too few rows."""


def read_csv(path):
    file = Path(path)
    if not file.is_file():
        raise ToolInputError(f"input file not found: {path}")
    return pd.read_csv(file)


def require_columns(frame, columns):
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise ToolInputError(f"missing columns: {missing}; available: {list(frame.columns)}")


def _jsonable(value):
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "item"):  # numpy scalar
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def run(compute):
    """Call compute() and turn its result or failure into the CLI contract."""
    try:
        result = compute()
    except ToolInputError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_BAD_INPUT
    json.dump(_jsonable(result), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0
