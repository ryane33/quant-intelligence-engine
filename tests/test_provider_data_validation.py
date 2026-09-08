from datetime import UTC, datetime

import polars as pl
import pytest

from qie.data.exceptions import InvalidMarketDataError
from qie.data.validation.contract import BAR_SCHEMA
from qie.data.validation.provider_data import validate_provider_bars


@pytest.fixture
def frame() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "timestamp": [
                datetime(2024, 1, 2, tzinfo=UTC),
                datetime(2024, 1, 3, tzinfo=UTC),
            ],
            "symbol": ["AAPL", "AAPL"],
            "open": [100.0, 101.0],
            "high": [102.0, 103.0],
            "low": [99.0, 100.0],
            "close": [101.0, 102.0],
            "adj_close": [101.0, 102.0],
            "volume": [0, 1000],
        },
        schema=BAR_SCHEMA,
    )


def test_valid(frame: pl.DataFrame) -> None:
    validate_provider_bars(frame, expected_symbol="AAPL")


@pytest.mark.parametrize("column", list(BAR_SCHEMA))
def test_missing_column(frame: pl.DataFrame, column: str) -> None:
    with pytest.raises(InvalidMarketDataError, match="Missing required columns"):
        validate_provider_bars(frame.drop(column))


@pytest.mark.parametrize("column", list(BAR_SCHEMA))
def test_null(frame: pl.DataFrame, column: str) -> None:
    with pytest.raises(InvalidMarketDataError, match="Null"):
        validate_provider_bars(
            frame.with_columns(pl.lit(None, dtype=BAR_SCHEMA[column]).alias(column))
        )


@pytest.mark.parametrize(
    "column,dtype",
    [
        ("timestamp", pl.String),
        ("timestamp", pl.Date),
        ("timestamp", pl.Datetime("us")),
        ("timestamp", pl.Datetime("ns", "UTC")),
        ("timestamp", pl.Datetime("us", "America/New_York")),
        ("open", pl.String),
        ("open", pl.Int64),
        ("volume", pl.Float64),
        ("symbol", pl.Categorical),
    ],
)
def test_wrong_dtype(frame: pl.DataFrame, column: str, dtype: pl.DataType) -> None:
    with pytest.raises(InvalidMarketDataError, match="dtypes"):
        validate_provider_bars(frame.with_columns(pl.col(column).cast(dtype)))


@pytest.mark.parametrize(
    "symbols",
    [
        ["aapl", "aapl"],
        [" AAPL", " AAPL"],
        ["", ""],
        ["AAPL", "MSFT"],
        ["AAPL MSFT", "AAPL MSFT"],
    ],
)
def test_bad_symbol(frame: pl.DataFrame, symbols: list[str]) -> None:
    with pytest.raises(InvalidMarketDataError):
        validate_provider_bars(frame.with_columns(pl.Series("symbol", symbols)))


def test_unexpected_symbol(frame: pl.DataFrame) -> None:
    with pytest.raises(InvalidMarketDataError, match="match request"):
        validate_provider_bars(frame, expected_symbol="MSFT")


def test_empty(frame: pl.DataFrame) -> None:
    with pytest.raises(InvalidMarketDataError, match="Empty"):
        validate_provider_bars(frame.head(0))


def test_duplicates(frame: pl.DataFrame) -> None:
    with pytest.raises(InvalidMarketDataError, match="Duplicate"):
        validate_provider_bars(frame[[0, 0]])


def test_unsorted(frame: pl.DataFrame) -> None:
    with pytest.raises(InvalidMarketDataError, match="not sorted"):
        validate_provider_bars(frame.reverse())


def test_exact_column_order(frame: pl.DataFrame) -> None:
    for invalid in (
        frame.select(list(reversed(frame.columns))),
        frame.with_columns(pl.lit(1).alias("extra")),
    ):
        with pytest.raises(InvalidMarketDataError, match="order"):
            validate_provider_bars(invalid)


@pytest.mark.parametrize(
    "column,value",
    [
        ("open", float("nan")),
        ("close", float("inf")),
        ("adj_close", 0.0),
        ("low", -1.0),
        ("volume", -1),
        ("high", 98.0),
        ("open", 104.0),
        ("close", 104.0),
        ("open", 98.0),
        ("close", 98.0),
    ],
)
def test_invalid_values(frame: pl.DataFrame, column: str, value: float) -> None:
    with pytest.raises(InvalidMarketDataError):
        validate_provider_bars(
            frame.with_columns(pl.lit(value, dtype=BAR_SCHEMA[column]).alias(column))
        )
