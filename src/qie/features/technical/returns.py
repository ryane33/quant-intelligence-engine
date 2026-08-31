from __future__ import annotations

import numpy as np
import polars as pl


def add_returns(
    frame: pl.DataFrame,
    price_column: str = "close",
) -> pl.DataFrame:
    """Add simple and logarithmic returns to a price DataFrame."""

    if price_column not in frame.columns:
        raise ValueError(f"missing required price column: {price_column}")

    return frame.with_columns(
        [
            pl.col(price_column).pct_change().alias("simple_return"),
            (pl.col(price_column).log().diff()).alias("log_return"),
        ]
    )


def cumulative_return(
    frame: pl.DataFrame,
    return_column: str = "simple_return",
) -> float:
    """Calculate compounded cumulative return."""

    if return_column not in frame.columns:
        raise ValueError(f"missing return column: {return_column}")

    returns = frame.select(return_column).drop_nulls().to_series().to_numpy()

    if len(returns) == 0:
        return 0.0

    return float(np.prod(1.0 + returns) - 1.0)
