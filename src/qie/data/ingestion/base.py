from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

import polars as pl


class MarketDataProvider(ABC):
    """Abstract interface for historical market-data providers."""

    @abstractmethod
    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> pl.DataFrame:
        """Return historical OHLCV bars for a symbol."""
        raise NotImplementedError
