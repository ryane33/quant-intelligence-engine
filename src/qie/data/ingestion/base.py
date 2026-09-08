from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

import polars as pl


class MarketDataProvider(ABC):
    """Abstract interface for historical market-data providers."""

    @property
    @abstractmethod
    def supported_timeframes(self) -> set[str]:
        """Return the timeframes supported by this provider."""
        raise NotImplementedError

    @abstractmethod
    def get_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1Day",
    ) -> pl.DataFrame:
        """Return nonempty canonical single-symbol bars in [start, end).

        See qie.data.validation.contract and docs/DATA_CONTRACT.md. Daily
        timestamps label session dates at midnight UTC; intraday bars use UTC
        instants. Implementations reject duplicate/unsorted or invalid data.
        """
        raise NotImplementedError
