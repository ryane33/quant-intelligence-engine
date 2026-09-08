"""Canonical single-symbol bar schema and request semantics."""

from datetime import UTC, datetime, time

import polars as pl

from qie.data.exceptions import InvalidDateRangeError

PRICE_COLUMNS = ("open", "high", "low", "close", "adj_close")
BAR_SCHEMA = {
    "timestamp": pl.Datetime("us", "UTC"),
    "symbol": pl.String,
    **dict.fromkeys(PRICE_COLUMNS, pl.Float64),
    "volume": pl.Int64,
}


def normalize_symbol(symbol: str) -> str:
    """Accept one ticker, preserving punctuation used by vendors."""
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("symbol must not be blank")
    symbol = symbol.strip().upper()
    if any(character.isspace() for character in symbol) or "," in symbol:
        raise ValueError("symbol must identify a single ticker")
    return symbol


def normalize_range(
    start: datetime, end: datetime, *, daily: bool
) -> tuple[datetime, datetime]:
    """Daily bounds are calendar labels; intraday bounds are UTC instants."""
    bounds = []
    for bound in (start, end):
        if not isinstance(bound, datetime):
            raise InvalidDateRangeError("start and end must be datetime values")
        if daily:
            if bound.time() != time.min:
                raise InvalidDateRangeError("daily boundaries must be midnight")
            bounds.append(datetime.combine(bound.date(), time.min, tzinfo=UTC))
        else:
            bounds.append(
                bound.replace(tzinfo=UTC)
                if bound.utcoffset() is None
                else bound.astimezone(UTC)
            )
    if bounds[0] >= bounds[1]:
        raise InvalidDateRangeError("start must be earlier than end")
    return bounds[0], bounds[1]
