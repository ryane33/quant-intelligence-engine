# Canonical market-data contract

This is the enforced contract for MarketDataProvider.get_bars. It is a single-symbol, single-timeframe dataset, not an arbitrary feature table. BAR_SCHEMA in src/qie/data/validation/contract.py is the code definition.

## Schema

Exactly these columns, in this order; no extra columns:

| Column | Polars dtype | Meaning |
| --- | --- | --- |
| timestamp | Datetime(us, UTC) | Daily session-date label or intraday bar instant, as below |
| symbol | String | One nonempty, stripped, uppercase ticker |
| open | Float64 | Finite, strictly positive unadjusted price |
| high | Float64 | Finite, strictly positive unadjusted price |
| low | Float64 | Finite, strictly positive unadjusted price |
| close | Float64 | Finite, strictly positive unadjusted price |
| adj_close | Float64 | Finite, strictly positive vendor-adjusted close |
| volume | Int64 | Whole nonnegative volume, at most 2**63 - 1 |

No nulls, NaN, infinity, duplicate timestamps, or unsorted rows. High must be at least open/close/low; low must be at most open/close/high. Adjusted close is not compared to raw high/low. All rows contain exactly one symbol; a supplied expected_symbol must match. Tickers may contain vendor punctuation, but commas and internal whitespace are rejected to prevent accidental multi-ticker requests. No ticker registry is implied.

The validator checks and returns None; it never mutates, sorts, deduplicates, or coerces a frame. Missing, extra, reordered, or incorrectly typed columns fail with InvalidMarketDataError. Canonical frames must be nonempty.

## Time and request boundaries

- Requests use inclusive start, exclusive end: [start, end). start must precede end after normalization.
- Daily requests accept midnight datetime boundaries, aware or naive. Their written calendar dates are used, regardless of offset, and sent to Yahoo as date strings. Nonmidnight daily boundaries fail rather than silently selecting partial days.
- Daily output timestamps label the vendor's local session date at midnight UTC. This preserves the session date even for positive UTC offsets. A daily label is neither the market-open instant nor the time the completed bar became available.
- Intraday requests interpret naive datetime boundaries as UTC for compatibility; aware boundaries are converted to UTC instants. Prefer aware boundaries in new code.
- Intraday vendor indexes must already be timezone-aware. They are converted to UTC, preserving DST offsets and instants. No exchange timezone is guessed for naive responses.
- Vendor indexes must be a pandas DatetimeIndex with no NaT. Daily indexes must contain midnight labels. Submicrosecond timestamps are rejected to avoid silent precision loss.
- All normalized vendor rows are validated before clipping to the request window. Corruption outside the window is not hidden. If clipping leaves no bars, the provider raises MarketDataUnavailableError.
- No promise of a complete exchange-calendar grid, closed-bar status, or point-in-time availability is made. The same schema does not imply that different timeframes can be concatenated safely without external timeframe metadata.

## Yahoo boundary

The adapter retains 1Day/1Hour/1Min and the existing get_bars signature. It normalizes the requested symbol before download. It requests auto_adjust=False, progress=False, keepna=True, and explicitly selects timezone preservation for intraday data. keepna=True allows QIE to see vendor null rows instead of allowing the downloader to drop them silently.

Flat columns and unambiguous two-level price/ticker or ticker/price MultiIndexes are supported. MultiIndex ticker metadata must contain exactly the requested ticker. Flat Yahoo responses have no ticker identity metadata; identity necessarily follows the single-symbol request. Duplicate column names, missing fields, multiple tickers, ambiguous layouts, and malformed response types fail explicitly. Extra vendor fields are discarded before canonical validation.

Numeric vendor columns must have real numeric dtypes: numeric strings, booleans, and complex values are rejected. Prices convert to Float64. Integral float volume is accepted only after non-null, range, and whole-number checks; fractional values are never truncated. Vendor frames are copied, not mutated.

None/empty downloads and empty clipped results raise MarketDataUnavailableError. Unsupported intervals raise UnsupportedTimeframeError; invalid bounds raise InvalidDateRangeError; invalid symbols raise ValueError. These preserve the existing ValueError-compatible error family. Data/schema failures raise InvalidMarketDataError. Unexpected downloader/transport exceptions propagate; there is no retry or broad exception-swallowing policy.

## Returns and row models

add_returns retains price-only input support, default close, a leading null return, and explicit price_column selection. It requires numeric, finite, positive, non-null prices. If symbol/timestamp metadata is present, it rejects mixed/null symbols and non-datetime/null/duplicate/unsorted timestamps. It does not group or sort. Without timestamps, the caller owns ordering. With a canonical provider frame, these requirements are already satisfied.

cumulative_return retains empty/all-null = 0.0 and compounding after null removal. Non-null simple returns must be numeric, finite, and at least -1; a total loss is valid. It applies the same optional series metadata guards. Nonfinite computed returns or compounding results raise ValueError, including overflow from otherwise finite inputs.

OHLCVBar remains a separate, smaller Pydantic input model, not a substitute for the frame schema: it has no adjusted close and permits float volume. It now rejects nonfinite numbers and automatically enforces OHLC relationships during construction while retaining validate_price_relationships().

## Compatibility and deliberate tightening

Public method names/signatures, interval support, column names/order, exception inheritance, and ordinary return calculations are preserved. Canonical dtypes/timezone, daily midnight bounds, strict frame column order, finite/positive numbers, single-series guards, and rejection of naive intraday vendor output are deliberate stricter behavior. Code passing loose frames directly to validation must now construct BAR_SCHEMA explicitly. Research must not treat normalized or adjusted history as historically available data.

## Verification

All provider tests mock yf.download; no network integration tests are retained. Run `.venv/bin/python -m pytest -q` from the repository root. This verifies adapter logic, not live Yahoo availability, retention limits, or undocumented future vendor layout changes.
