from datetime import datetime

import polars as pl
import yfinance as yf  # type: ignore

from qie.data.ingestion.base import MarketDataProvider


class YahooMarketDataProvider(MarketDataProvider):
    """Market data provider for Yahoo Finance."""

    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> pl.DataFrame:
        interval_map = {
            "1Day": "1d",
            "1Hour": "1h",
            "1Min": "1m",
        }

        if start >= end:
            raise ValueError("start must be earlier than end")

        if not symbol.strip():
            raise ValueError("symbol must not be blank")

        if timeframe not in interval_map:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        data = yf.download(  # type: ignore
            symbol,
            start=start,
            end=end,
            interval=interval_map[timeframe],
            auto_adjust=False,
            progress=False,
        )

        if data is None or data.empty:
            raise ValueError(f"No data found for {symbol}")

        data.columns = [
            column[0] if isinstance(column, tuple) else column
            for column in data.columns
        ]

        data = data.reset_index()

        frame = pl.from_pandas(data)

        frame = frame.rename(
            {
                "Date": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )

        frame = frame.with_columns(
            pl.lit(symbol.strip().upper()).alias("symbol")
        )

        return frame.select(
            [
                "timestamp",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "adj_close",
                "volume",
            ]
        )