import pytest

from datetime import datetime

from qie.data.ingestion.yahoo import YahooMarketDataProvider


def test_yahoo_returns_canonical_columns() -> None:
    provider = YahooMarketDataProvider()

    data = provider.get_bars(
        symbol="AAPL",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 2, 1),
        timeframe="1Day",
    )

    assert data.columns == [
        "timestamp",
        "symbol",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
    ]



def test_yahoo_prices_are_logically_valid() -> None:
    provider = YahooMarketDataProvider()

    data = provider.get_bars(
        symbol="AAPL",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 2, 1),
        timeframe="1Day",
    )

    assert (data["high"] >= data["low"]).all()
    assert (data["high"] >= data["open"]).all()
    assert (data["high"] >= data["close"]).all()
    assert (data["low"] <= data["open"]).all()
    assert (data["low"] <= data["close"]).all()


def test_yahoo_normalizes_symbol() -> None:
    provider = YahooMarketDataProvider()

    data = provider.get_bars(
        symbol=" aapl ",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 2, 1),
        timeframe="1Day",
    )

    assert data["symbol"].unique().to_list() == ["AAPL"]



def test_yahoo_timestamps_are_sorted() -> None:
    provider = YahooMarketDataProvider()

    data = provider.get_bars(
        symbol="AAPL",
        start=datetime(2024, 1, 1),
        end=datetime(2024, 2, 1),
        timeframe="1Day",
    )

    assert data["timestamp"].is_sorted()


def test_yahoo_rejects_bad_symbol() -> None:
    provider = YahooMarketDataProvider()

    with pytest.raises(ValueError, match="No data found"):
        provider.get_bars(
            symbol="THIS_IS_NOT_A_REAL_TICKER_12345",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 2, 1),
            timeframe="1Day",
        )


def test_yahoo_rejects_invalid_date_range() -> None:
    provider = YahooMarketDataProvider()

    with pytest.raises(ValueError, match="start must be earlier than end"):
        provider.get_bars(
            symbol="AAPL",
            start=datetime(2024, 2, 1),
            end=datetime(2024, 1, 1),
            timeframe="1Day",
        )



def test_yahoo_rejects_blank_symbol() -> None:
    provider = YahooMarketDataProvider()

    with pytest.raises(ValueError, match="symbol must not be blank"):
        provider.get_bars(
            symbol="   ",
            start=datetime(2024, 1, 1),
            end=datetime(2024, 2, 1),
            timeframe="1Day",
        )
