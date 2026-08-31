from datetime import UTC, datetime

import polars as pl
import pytest

from qie.data.validation.market_data import OHLCVBar
from qie.features.technical.returns import add_returns, cumulative_return


def test_ohlcv_bar_normalizes_symbol() -> None:
    bar = OHLCVBar(
        symbol=" aapl ",
        timestamp=datetime(2026, 1, 2, tzinfo=UTC),
        open=100.0,
        high=105.0,
        low=99.0,
        close=104.0,
        volume=1_000_000,
    )

    assert bar.symbol == "AAPL"


def test_add_returns() -> None:
    frame = pl.DataFrame(
        {
            "close": [100.0, 110.0, 121.0],
        }
    )

    result = add_returns(frame)

    simple = result["simple_return"].to_list()

    assert simple[0] is None
    assert simple[1] == pytest.approx(0.10)
    assert simple[2] == pytest.approx(0.10)


def test_cumulative_return() -> None:
    frame = pl.DataFrame(
        {
            "close": [100.0, 110.0, 121.0],
        }
    )

    result = add_returns(frame)

    assert cumulative_return(result) == pytest.approx(0.21)
