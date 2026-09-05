import polars as pl

def validate_provider_bars(frame: pl.DataFrame) -> None:
    """Validate one provider's market-bar dataset."""

    required_columns = {
    "timestamp",
    "symbol",
    "open",
    "high",
    "low",
    "close",
    "adj_close",
    "volume",
}

    missing_columns = required_columns - set(frame.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    if frame["timestamp"].is_duplicated().any():
        raise ValueError("Duplicate timestamps found")

    if frame.null_count().sum_horizontal().sum() > 0:
        raise ValueError("Null values found")

    if not frame["timestamp"].is_sorted():
        raise ValueError("Timestamps are not sorted")

    if (frame["high"] < frame["low"]).any():
        raise ValueError("High values are less than low values")

    if (frame["open"] > frame["high"]).any():
        raise ValueError("Open values are greater than high values")

    if (frame["close"] > frame["high"]).any():
        raise ValueError("Close values are greater than high values")

    if (frame["open"] < frame["low"]).any():
        raise ValueError("Open values are less than low values")

    if (frame["close"] < frame["low"]).any():
        raise ValueError("Close values are less than low values")