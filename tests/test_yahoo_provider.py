from datetime import UTC, datetime
from unittest.mock import Mock

import pandas as pd
import polars as pl
import pytest

from qie.data.exceptions import (
    InvalidDateRangeError,
    InvalidMarketDataError,
    MarketDataUnavailableError,
    UnsupportedTimeframeError,
)
from qie.data.ingestion.yahoo import YahooMarketDataProvider
from qie.data.validation.contract import BAR_SCHEMA
from qie.features.technical.returns import add_returns, cumulative_return

START = datetime(2024, 1, 1, tzinfo=UTC)
END = datetime(2024, 2, 1, tzinfo=UTC)


@pytest.fixture
def vendor() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Open": [100.0, 110.0],
            "High": [112.0, 122.0],
            "Low": [99.0, 109.0],
            "Close": [110.0, 121.0],
            "Adj Close": [110.0, 121.0],
            "Volume": [1000, 1200],
        },
        index=pd.DatetimeIndex(["2024-01-02", "2024-01-03"], name="Date"),
    )


@pytest.fixture(autouse=True)
def download(monkeypatch: pytest.MonkeyPatch, vendor: pd.DataFrame) -> Mock:
    mock = Mock(return_value=vendor)
    monkeypatch.setattr("qie.data.ingestion.yahoo.yf.download", mock)
    return mock


def bars(**kwargs: object) -> pl.DataFrame:
    arguments = {"symbol": "AAPL", "start": START, "end": END, **kwargs}
    return YahooMarketDataProvider().get_bars(**arguments)


@pytest.mark.parametrize("layout", ["flat", "price_first", "ticker_first"])
def test_canonical_download(vendor: pd.DataFrame, download: Mock, layout: str) -> None:
    if layout != "flat":
        tuples = [
            (field, "AAPL") if layout == "price_first" else ("AAPL", field)
            for field in vendor.columns
        ]
        vendor.columns = pd.MultiIndex.from_tuples(tuples)
    result = bars(symbol=" aapl ")
    assert result.schema == BAR_SCHEMA
    assert result["symbol"].to_list() == ["AAPL", "AAPL"]
    assert result["timestamp"].to_list() == [
        datetime(2024, 1, 2, tzinfo=UTC),
        datetime(2024, 1, 3, tzinfo=UTC),
    ]
    download.assert_called_once_with(
        "AAPL",
        start="2024-01-01",
        end="2024-02-01",
        interval="1d",
        auto_adjust=False,
        progress=False,
        ignore_tz=True,
        keepna=True,
    )
    assert cumulative_return(add_returns(result)) == pytest.approx(0.1)
    assert add_returns(result)["log_return"][1] == pytest.approx(0.0953101798)


@pytest.mark.parametrize("timeframe,interval", [("1Hour", "1h"), ("1Min", "1m")])
def test_intraday_dst(
    vendor: pd.DataFrame, download: Mock, timeframe: str, interval: str
) -> None:
    vendor.index = pd.DatetimeIndex(
        ["2024-03-08 09:30", "2024-03-11 09:30"], tz="America/New_York", name="Datetime"
    )
    start = datetime(2024, 3, 8, tzinfo=UTC)
    end = datetime(2024, 3, 12, tzinfo=UTC)
    result = bars(start=start, end=end, timeframe=timeframe)
    assert result["timestamp"].to_list() == [
        datetime(2024, 3, 8, 14, 30, tzinfo=UTC),
        datetime(2024, 3, 11, 13, 30, tzinfo=UTC),
    ]
    assert download.call_args.kwargs["interval"] == interval
    assert download.call_args.kwargs["ignore_tz"] is False


def test_daily_preserves_local_session_date(vendor: pd.DataFrame) -> None:
    vendor.index = vendor.index.tz_localize("Asia/Tokyo")
    assert bars()["timestamp"][0] == datetime(2024, 1, 2, tzinfo=UTC)


@pytest.mark.parametrize("response", [None, pd.DataFrame()])
def test_empty_response(download: Mock, response: object) -> None:
    download.return_value = response
    with pytest.raises(MarketDataUnavailableError, match="No data found"):
        bars()


@pytest.mark.parametrize("symbol", ["", "   ", "AAPL MSFT", "AAPL,MSFT", None])
def test_invalid_symbol_before_download(download: Mock, symbol: object) -> None:
    with pytest.raises(ValueError, match="symbol"):
        bars(symbol=symbol)
    download.assert_not_called()


def test_unsupported_timeframe(download: Mock) -> None:
    with pytest.raises(UnsupportedTimeframeError, match="Unsupported timeframe"):
        bars(timeframe="2Day")
    download.assert_not_called()
    assert YahooMarketDataProvider().supported_timeframes == {"1Day", "1Hour", "1Min"}


@pytest.mark.parametrize(
    "start,end",
    [
        (END, START),
        (START, START),
        (datetime(2024, 1, 1, 1, tzinfo=UTC), END),
        ("2024-01-01", END),
    ],
)
def test_invalid_range(download: Mock, start: object, end: object) -> None:
    with pytest.raises(InvalidDateRangeError):
        bars(start=start, end=end)
    download.assert_not_called()


def test_naive_request_compatibility(vendor: pd.DataFrame, download: Mock) -> None:
    vendor.index = vendor.index.tz_localize("UTC")
    result = bars(start=START.replace(tzinfo=None), end=END, timeframe="1Hour")
    assert result.height == 2
    assert download.call_args.kwargs["start"] == START


def test_clip_inclusive_start_exclusive_end() -> None:
    result = bars(
        start=datetime(2024, 1, 2, tzinfo=UTC), end=datetime(2024, 1, 3, tzinfo=UTC)
    )
    assert result.height == 1
    assert result["timestamp"][0] == datetime(2024, 1, 2, tzinfo=UTC)
    with pytest.raises(MarketDataUnavailableError, match="requested range"):
        bars(start=datetime(2024, 1, 4, tzinfo=UTC))


@pytest.mark.parametrize("field", ["Open", "Adj Close", "Volume"])
def test_missing_columns(vendor: pd.DataFrame, field: str) -> None:
    vendor.drop(columns=field, inplace=True)
    with pytest.raises(InvalidMarketDataError, match="Missing required columns"):
        bars()


@pytest.mark.parametrize("ticker", ["MSFT", "", "aapl"])
def test_wrong_multiindex_symbol(vendor: pd.DataFrame, ticker: str) -> None:
    vendor.columns = pd.MultiIndex.from_product([vendor.columns, [ticker]])
    with pytest.raises(InvalidMarketDataError, match="symbol"):
        bars()


def test_multiple_tickers(vendor: pd.DataFrame, download: Mock) -> None:
    download.return_value = pd.concat({"AAPL": vendor, "MSFT": vendor}, axis=1)
    with pytest.raises(InvalidMarketDataError, match="symbol"):
        bars()


@pytest.mark.parametrize(
    "bad", ["100", True, complex(1, 2), None, float("nan"), float("inf"), 0.0, -1.0]
)
def test_malformed_prices(vendor: pd.DataFrame, bad: object) -> None:
    vendor["Open"] = [bad, bad]
    with pytest.raises(InvalidMarketDataError):
        bars()


@pytest.mark.parametrize(
    "bad", [-1, 1.5, float("inf"), float("nan"), 2**63, "100", True]
)
def test_invalid_volume(vendor: pd.DataFrame, bad: object) -> None:
    vendor["Volume"] = [bad, bad]
    with pytest.raises(InvalidMarketDataError):
        bars()


def test_whole_float_volume_and_integer_prices(vendor: pd.DataFrame) -> None:
    vendor["Volume"] = [0.0, 12.0]
    vendor["Open"] = [100, 110]
    assert bars()["volume"].to_list() == [0, 12]


@pytest.mark.parametrize(
    "kind", ["duplicate", "unsorted", "string", "missing", "daily_time"]
)
def test_bad_timestamps(vendor: pd.DataFrame, kind: str) -> None:
    if kind == "duplicate":
        vendor.index = vendor.index[[0, 0]]
    elif kind == "unsorted":
        vendor.index = vendor.index[::-1]
    elif kind == "string":
        vendor.index = ["2024-01-02", "2024-01-03"]
    elif kind == "missing":
        vendor.index = pd.DatetimeIndex(["2024-01-02", pd.NaT])
    else:
        vendor.index = vendor.index + pd.Timedelta(hours=1)
    with pytest.raises(InvalidMarketDataError):
        bars()


def test_naive_intraday_rejected() -> None:
    with pytest.raises(InvalidMarketDataError, match="timezone-aware"):
        bars(timeframe="1Hour")


def test_malformed_response(download: Mock) -> None:
    download.return_value = {"Open": [100]}
    with pytest.raises(InvalidMarketDataError, match="DataFrame"):
        bars()


def test_duplicate_columns(vendor: pd.DataFrame, download: Mock) -> None:
    download.return_value = pd.concat([vendor, vendor[["Open"]]], axis=1)
    with pytest.raises(InvalidMarketDataError, match="Duplicate Yahoo columns"):
        bars()


def test_corruption_outside_range_not_hidden(vendor: pd.DataFrame) -> None:
    vendor.loc[vendor.index[0], "Open"] = -1
    with pytest.raises(InvalidMarketDataError):
        bars(start=datetime(2024, 1, 3, tzinfo=UTC))


def test_submicrosecond_timestamp_rejected(vendor: pd.DataFrame) -> None:
    vendor.index = vendor.index.tz_localize("UTC") + pd.Timedelta(nanoseconds=1)
    with pytest.raises(InvalidMarketDataError, match="microsecond"):
        bars(timeframe="1Min")


def test_provider_does_not_mutate_vendor(vendor: pd.DataFrame) -> None:
    original = vendor.copy(deep=True)
    bars()
    pd.testing.assert_frame_equal(vendor, original)


def test_intraday_offset_boundaries(vendor: pd.DataFrame, download: Mock) -> None:
    from zoneinfo import ZoneInfo

    vendor.index = pd.DatetimeIndex(
        ["2024-01-02 09:30", "2024-01-02 10:30"], tz="America/New_York", name="Datetime"
    )
    start = datetime(2024, 1, 2, 9, 30, tzinfo=ZoneInfo("America/New_York"))
    end = datetime(2024, 1, 2, 15, 30, tzinfo=UTC)
    result = bars(start=start, end=end, timeframe="1Hour")
    assert result.height == 1
    assert download.call_args.kwargs["start"] == datetime(
        2024, 1, 2, 14, 30, tzinfo=UTC
    )


def test_int64_max_volume(vendor: pd.DataFrame) -> None:
    vendor["Volume"] = [2**63 - 1, 0]
    assert bars()["volume"][0] == 2**63 - 1
