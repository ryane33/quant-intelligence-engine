"""Strict validation; normalization belongs at the provider boundary."""

import polars as pl

from qie.data.exceptions import InvalidMarketDataError
from qie.data.validation.contract import BAR_SCHEMA, PRICE_COLUMNS, normalize_symbol


def validate_provider_bars(
    frame: pl.DataFrame, *, expected_symbol: str | None = None
) -> None:
    """Validate a nonempty canonical single-symbol frame without mutating it."""
    missing = set(BAR_SCHEMA) - set(frame.columns)
    if missing:
        raise InvalidMarketDataError(f"Missing required columns: {sorted(missing)}")
    if frame.columns != list(BAR_SCHEMA):
        raise InvalidMarketDataError("Columns must match canonical order exactly")
    if frame.schema != BAR_SCHEMA:
        raise InvalidMarketDataError(f"Invalid canonical dtypes: {frame.schema}")
    if frame.is_empty():
        raise InvalidMarketDataError("Empty market data frame")
    if frame.null_count().sum_horizontal().sum() > 0:
        raise InvalidMarketDataError("Null values found")
    symbols = frame["symbol"].unique().to_list()
    if len(symbols) != 1:
        raise InvalidMarketDataError("Expected exactly one symbol")
    try:
        normalized = normalize_symbol(symbols[0])
    except ValueError as exc:
        raise InvalidMarketDataError("Invalid symbol") from exc
    if symbols[0] != normalized:
        raise InvalidMarketDataError("Symbol must be stripped and uppercase")
    if expected_symbol is not None and normalized != normalize_symbol(expected_symbol):
        raise InvalidMarketDataError("Symbol does not match request")
    if frame["timestamp"].is_duplicated().any():
        raise InvalidMarketDataError("Duplicate timestamps found")
    if not frame["timestamp"].is_sorted():
        raise InvalidMarketDataError("Timestamps are not sorted")
    for column in PRICE_COLUMNS:
        values = frame[column]
        if not values.is_finite().all() or (values <= 0).any():
            raise InvalidMarketDataError(
                f"{column} must contain finite positive prices"
            )
    if (frame["volume"] < 0).any():
        raise InvalidMarketDataError("volume must be nonnegative")
    for left, right, message in (
        ("high", "low", "High values are less than low values"),
        ("high", "open", "Open values are greater than high values"),
        ("high", "close", "Close values are greater than high values"),
        ("open", "low", "Open values are less than low values"),
        ("close", "low", "Close values are less than low values"),
    ):
        if (frame[left] < frame[right]).any():
            raise InvalidMarketDataError(message)
