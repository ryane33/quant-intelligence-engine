from datetime import datetime

import polars as pl
import pytest

from qie.data.validation.provider_data import validate_provider_bars


def test_rejects_duplicate_timestamps() -> None:
    frame = pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 2),
                datetime(2024, 1, 2),
            ],
            "symbol": ["AAPL", "AAPL"],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "adj_close": [101.0, 102.0],
            "volume": [1_000_000, 1_100_000],
        }
    )

    with pytest.raises(ValueError, match="Duplicate timestamps found"):
        validate_provider_bars(frame)



def test_rejects_null_values() -> None:
    frame = pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 2),
                datetime(2024, 1, 3),
            ],
            "symbol": ["AAPL", "AAPL"],
            "open": [100.0, None],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "adj_close": [101.0, 102.0],
            "volume": [1_000_000, 1_100_000],
        }
    )

    with pytest.raises(ValueError, match="Null values found"):
        validate_provider_bars(frame)



def test_rejects_missing_required_columns() -> None:
    frame = pl.DataFrame(
        {
            "timestamp": [datetime(2024, 1, 2)],
            "symbol": ["AAPL"],
            "open": [100.0],
            "high": [102.0],
            "low": [99.0],
            "close": [101.0],
            "adj_close": [101.0],
            # volume intentionally missing
        }
    )

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_provider_bars(frame)


def test_rejects_unsorted_timestamps() -> None:
    frame = pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 3),
                datetime(2024, 1, 2),
            ],
            "symbol": ["AAPL", "AAPL"],
            "open": [101.0, 100.0],
            "high": [103.0, 102.0],
            "low": [100.0, 99.0],
            "close": [102.0, 101.0],
            "adj_close": [102.0, 101.0],
            "volume": [1_100_000, 1_000_000],
        }
    )

    with pytest.raises(ValueError, match="Timestamps are not sorted"):
        validate_provider_bars(frame)


def test_rejects_invalid_ohlc_relationships() -> None:
    frame = pl.DataFrame(
        {
            "timestamp": [datetime(2024, 1, 2)],
            "symbol": ["AAPL"],
            "open": [105.0],
            "high": [100.0],
            "low": [95.0],
            "close": [98.0],
            "adj_close": [98.0],
            "volume": [1_000_000],
        }
    )

    with pytest.raises(ValueError):
        validate_provider_bars(frame)