from datetime import UTC, datetime

import polars as pl
import pytest

from qie.features.technical.returns import add_returns, cumulative_return


@pytest.mark.parametrize(
    "prices",
    [
        [0.0, 1.0],
        [-1.0, 1.0],
        [None, 1.0],
        [float("nan"), 1.0],
        [float("inf"), 1.0],
        ["1", "2"],
        [True, False],
    ],
)
def test_invalid_prices(prices: list[object]) -> None:
    with pytest.raises(ValueError):
        add_returns(pl.DataFrame({"close": prices}))


@pytest.mark.parametrize("function", [add_returns, cumulative_return])
def test_multiple_symbols(function) -> None:
    with pytest.raises(ValueError, match="single"):
        function(
            pl.DataFrame(
                {
                    "symbol": ["AAPL", "MSFT"],
                    "close": [1.0, 2.0],
                    "simple_return": [None, 1.0],
                }
            )
        )


@pytest.mark.parametrize("kind", ["unsorted", "duplicate", "null", "string"])
def test_timestamp_guards(kind: str) -> None:
    times = [datetime(2024, 1, 2, tzinfo=UTC), datetime(2024, 1, 1, tzinfo=UTC)]
    if kind == "duplicate":
        times = [times[0], times[0]]
    elif kind == "null":
        times = [None, times[0]]
    elif kind == "string":
        times = ["2024-01-01", "2024-01-02"]
    with pytest.raises(ValueError, match="timestamps"):
        add_returns(pl.DataFrame({"timestamp": times, "close": [1.0, 2.0]}))


def test_adjusted_price_selection_and_first_null() -> None:
    frame = pl.DataFrame({"close": [100.0, 50.0], "adj_close": [50.0, 50.0]})
    assert add_returns(frame)["simple_return"].to_list() == [None, -0.5]
    assert add_returns(frame, "adj_close")["simple_return"].to_list() == [None, 0.0]


def test_empty_series_compatibility() -> None:
    result = add_returns(pl.DataFrame(schema={"close": pl.Float64}))
    assert result.is_empty()
    assert cumulative_return(result) == 0.0
    assert cumulative_return(pl.DataFrame({"simple_return": [None]})) == 0.0


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.1, "0.1"])
def test_invalid_cumulative_return(value: object) -> None:
    with pytest.raises(ValueError):
        cumulative_return(pl.DataFrame({"simple_return": [value]}))


def test_total_loss() -> None:
    assert cumulative_return(pl.DataFrame({"simple_return": [None, -1.0]})) == -1.0


def test_price_ratio_overflow() -> None:
    with pytest.raises(ValueError, match="nonfinite result"):
        add_returns(pl.DataFrame({"close": [1e-300, 1e300]}))


def test_compounding_overflow() -> None:
    with pytest.raises(ValueError, match="nonfinite result"):
        cumulative_return(pl.DataFrame({"simple_return": [1e300, 1e300]}))
