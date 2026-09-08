"""Yahoo adapter for the canonical single-symbol bar contract."""

from datetime import datetime

import pandas as pd
import polars as pl
import yfinance as yf
from pandas.api.types import is_bool_dtype, is_numeric_dtype

from qie.data.exceptions import (
    InvalidMarketDataError,
    MarketDataUnavailableError,
    UnsupportedTimeframeError,
)
from qie.data.ingestion.base import MarketDataProvider
from qie.data.validation.contract import BAR_SCHEMA, normalize_range, normalize_symbol
from qie.data.validation.provider_data import validate_provider_bars

_INTERVALS = {"1Day": "1d", "1Hour": "1h", "1Min": "1m"}
_FIELDS = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Adj Close": "adj_close",
    "Volume": "volume",
}


def _select_prices(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Accept flat columns or unambiguous two-level price/ticker layouts."""
    if isinstance(data.columns, pd.MultiIndex):
        if data.columns.nlevels != 2:
            raise InvalidMarketDataError("Expected two Yahoo column levels")
        candidates = [
            level
            for level in range(2)
            if set(_FIELDS).issubset(set(data.columns.get_level_values(level)))
        ]
        if len(candidates) != 1:
            raise InvalidMarketDataError(
                "Missing required columns or ambiguous Yahoo layout"
            )
        price_level = candidates[0]
        tickers = set(data.columns.get_level_values(1 - price_level))
        if tickers != {symbol}:
            raise InvalidMarketDataError("Yahoo symbol does not match request")
        data = data.copy()
        data.columns = data.columns.get_level_values(price_level)
    if data.columns.has_duplicates:
        raise InvalidMarketDataError("Duplicate Yahoo columns")
    missing = set(_FIELDS) - set(data.columns)
    if missing:
        raise InvalidMarketDataError(f"Missing required columns: {sorted(missing)}")
    # Flat Yahoo responses have no ticker metadata; identity follows the request.
    return data.loc[:, list(_FIELDS)].copy()


def _timestamps(index: pd.Index, *, daily: bool) -> pd.DatetimeIndex:
    if not isinstance(index, pd.DatetimeIndex) or index.hasnans:
        raise InvalidMarketDataError(
            "Yahoo index must contain valid datetime timestamps"
        )
    if (index.nanosecond != 0).any():
        raise InvalidMarketDataError(
            "Timestamps must have at most microsecond precision"
        )
    if daily:
        # Session dates are labels, not instants or bar availability times.
        labels = index.tz_localize(None) if index.tz is not None else index
        if not (labels == labels.normalize()).all():
            raise InvalidMarketDataError(
                "Daily timestamps must be midnight session labels"
            )
        return labels.tz_localize("UTC")
    if index.tz is None:
        raise InvalidMarketDataError("Intraday timestamps must be timezone-aware")
    return index.tz_convert("UTC")


class YahooMarketDataProvider(MarketDataProvider):
    """Normalize Yahoo data; reject corruption rather than repairing it."""

    @property
    def supported_timeframes(self) -> set[str]:
        return set(_INTERVALS)

    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> pl.DataFrame:
        symbol = normalize_symbol(symbol)
        if timeframe not in self.supported_timeframes:
            raise UnsupportedTimeframeError(f"Unsupported timeframe: {timeframe}")
        daily = timeframe == "1Day"
        start, end = normalize_range(start, end, daily=daily)
        data = yf.download(
            symbol,
            start=start.date().isoformat() if daily else start,
            end=end.date().isoformat() if daily else end,
            interval=_INTERVALS[timeframe],
            auto_adjust=False,
            progress=False,
            ignore_tz=daily,
            keepna=True,
        )
        if data is None:
            raise MarketDataUnavailableError(f"No data found for {symbol}")
        if not isinstance(data, pd.DataFrame):
            raise InvalidMarketDataError("Yahoo response must be a pandas DataFrame")
        if data.empty:
            raise MarketDataUnavailableError(f"No data found for {symbol}")
        prices = _select_prices(data, symbol)
        timestamps = _timestamps(prices.index, daily=daily)
        for column in _FIELDS:
            dtype = prices[column].dtype
            if not is_numeric_dtype(dtype) or is_bool_dtype(dtype) or dtype.kind == "c":
                raise InvalidMarketDataError(f"Malformed numeric column: {column}")
        volume = prices["Volume"]
        if volume.isna().any() or not ((volume >= 0) & (volume < 2**63)).all():
            raise InvalidMarketDataError(
                "volume must be within nonnegative Int64 range"
            )
        if not (volume % 1 == 0).all():
            raise InvalidMarketDataError("volume must contain whole numbers")
        try:
            # Cast volume before conversion to avoid float truncation/overflow.
            prices["Volume"] = volume.astype("int64")
            frame = pl.from_pandas(prices.reset_index(drop=True)).rename(_FIELDS)
            frame = (
                frame.with_columns(
                    pl.Series(
                        "timestamp",
                        list(timestamps.to_pydatetime()),
                        dtype=BAR_SCHEMA["timestamp"],
                    ),
                    pl.lit(symbol).alias("symbol"),
                )
                .select(list(BAR_SCHEMA))
                .cast(BAR_SCHEMA, strict=True)
            )
        except (ValueError, TypeError, OverflowError, pl.exceptions.PolarsError) as exc:
            raise InvalidMarketDataError("Cannot normalize Yahoo bar dtypes") from exc
        # Validate even out-of-range rows: clipping must not hide corruption.
        validate_provider_bars(frame, expected_symbol=symbol)
        frame = frame.filter(
            (pl.col("timestamp") >= start) & (pl.col("timestamp") < end)
        )
        if frame.is_empty():
            raise MarketDataUnavailableError(
                f"No data found for {symbol} in requested range"
            )
        return frame
