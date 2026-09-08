from __future__ import annotations

import numpy as np
import polars as pl


def _validate_series_order(frame: pl.DataFrame) -> None:
    """Prevent accidental cross-symbol or out-of-order return calculations."""
    if "symbol" in frame.columns and (
        frame["symbol"].null_count() or frame["symbol"].n_unique() > 1
    ):
        raise ValueError("returns require a single non-null symbol")
    if "timestamp" in frame.columns:
        timestamps = frame["timestamp"]
        if not isinstance(timestamps.dtype, pl.Datetime):
            raise ValueError("return timestamps must have a datetime dtype")
        if (
            timestamps.null_count()
            or timestamps.is_duplicated().any()
            or not timestamps.is_sorted()
        ):
            raise ValueError("return timestamps must be non-null, unique, and sorted")


def add_returns(
    frame: pl.DataFrame,
    price_column: str = "close",
) -> pl.DataFrame:
    """Add returns for one ordered series of finite positive prices.

    Price-only frames remain supported; callers then own ordering. The first
    return is null. Choose adj_close explicitly when adjusted returns are wanted.
    """

    if price_column not in frame.columns:
        raise ValueError(f"missing required price column: {price_column}")
    _validate_series_order(frame)
    prices = frame[price_column]
    if not prices.dtype.is_numeric():
        raise ValueError("return prices must be numeric")
    if prices.null_count() or not prices.is_finite().all() or (prices <= 0).any():
        raise ValueError("return prices must be finite, positive, and non-null")

    result = frame.with_columns(
        [
            pl.col(price_column).pct_change().alias("simple_return"),
            (pl.col(price_column).log().diff()).alias("log_return"),
        ]
    )
    if any(
        not result[column].drop_nulls().is_finite().all()
        for column in ("simple_return", "log_return")
    ):
        raise ValueError("return calculation produced a nonfinite result")
    return result


def cumulative_return(
    frame: pl.DataFrame,
    return_column: str = "simple_return",
) -> float:
    """Calculate compounded cumulative return."""

    if return_column not in frame.columns:
        raise ValueError(f"missing return column: {return_column}")
    _validate_series_order(frame)
    values = frame[return_column]
    if not values.dtype.is_numeric() and values.dtype != pl.Null:
        raise ValueError("returns must be numeric")
    present = values.drop_nulls()
    if len(present) and (not present.is_finite().all() or (present < -1).any()):
        raise ValueError("simple returns must be finite and at least -1")

    returns = frame.select(return_column).drop_nulls().to_series().to_numpy()

    if len(returns) == 0:
        return 0.0

    with np.errstate(over="ignore", invalid="ignore"):
        result = float(np.prod(1.0 + returns) - 1.0)
    if not np.isfinite(result):
        raise ValueError("compounding produced a nonfinite result")
    return result
