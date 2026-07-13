from __future__ import annotations

import pandas as pd
import pytest

from rollslope_quant.application.services.market_kline_csv import (
    prepare_market_kline_dataframe,
)


def _base_df(**overrides: object) -> pd.DataFrame:
    data = {
        "datetime": [
            "2026-01-01 09:00:00",
            "2026-01-01 10:00:00",
            "2026-01-01 11:00:00",
            "2026-01-01 12:00:00",
        ],
        "close": [100.0, 101.0, 99.0, 102.0],
    }
    data.update(overrides)
    return pd.DataFrame(data)


def test_missing_close_column_raises() -> None:
    df = pd.DataFrame({"datetime": ["2026-01-01 09:00:00"], "open": [100.0]})
    with pytest.raises(ValueError, match="close"):
        prepare_market_kline_dataframe(df)


def test_close_non_numeric_raises() -> None:
    df = _base_df(close=[100.0, "abc", 99.0, 102.0])
    with pytest.raises(ValueError, match="close"):
        prepare_market_kline_dataframe(df)


def test_close_blank_raises() -> None:
    df = _base_df(close=[100.0, None, 99.0, 102.0])
    with pytest.raises(ValueError, match="close"):
        prepare_market_kline_dataframe(df)


def test_close_all_identical_raises() -> None:
    df = _base_df(close=[100.0, 100.0, 100.0, 100.0])
    with pytest.raises(ValueError, match="close"):
        prepare_market_kline_dataframe(df)


def test_datetime_auto_sorts_scrambled_order() -> None:
    df = pd.DataFrame(
        {
            "datetime": [
                "2026-01-01 12:00:00",
                "2026-01-01 09:00:00",
                "2026-01-01 11:00:00",
                "2026-01-01 10:00:00",
            ],
            "close": [102.0, 100.0, 99.0, 101.0],
        }
    )
    result = prepare_market_kline_dataframe(df)
    assert list(result["close"]) == [100.0, 101.0, 99.0, 102.0]
    assert list(result["datetime"]) == sorted(result["datetime"])
    assert list(result.index) == list(range(len(result)))


def test_no_datetime_column_preserves_row_order() -> None:
    df = pd.DataFrame({"close": [100.0, 98.0, 101.0, 97.0]})
    result = prepare_market_kline_dataframe(df)
    assert list(result["close"]) == [100.0, 98.0, 101.0, 97.0]
    assert "datetime" not in result.columns


def test_datetime_unparseable_raises() -> None:
    df = _base_df(datetime=["2026-01-01 09:00:00", "not-a-date", "2026-01-01 11:00:00", "2026-01-01 12:00:00"])
    with pytest.raises(ValueError, match="datetime"):
        prepare_market_kline_dataframe(df)


def test_close_and_datetime_column_name_case_insensitive() -> None:
    df = pd.DataFrame(
        {
            "DateTime": [
                "2026-01-01 11:00:00",
                "2026-01-01 09:00:00",
                "2026-01-01 10:00:00",
            ],
            "Close": [99.0, 100.0, 101.0],
        }
    )
    result = prepare_market_kline_dataframe(df)
    assert "close" in result.columns
    assert "datetime" in result.columns
    assert list(result["close"]) == [100.0, 101.0, 99.0]


def test_output_columns_normalized_to_lowercase() -> None:
    df = pd.DataFrame(
        {
            "DATETIME": ["2026-01-01 09:00:00", "2026-01-01 10:00:00"],
            "CLOSE": [100.0, 101.0],
        }
    )
    result = prepare_market_kline_dataframe(df)
    assert "datetime" in result.columns
    assert "close" in result.columns
    assert "DATETIME" not in result.columns
    assert "CLOSE" not in result.columns


def test_open_high_low_volume_preserved_but_not_required() -> None:
    df = _base_df(
        open=[99.5, 100.5, 98.5, 101.5],
        high=[100.5, 101.5, 99.5, 102.5],
        low=[99.0, 100.0, 98.0, 101.0],
        volume=[100, 200, 300, 400],
    )
    result = prepare_market_kline_dataframe(df)
    for col in ["open", "high", "low", "volume"]:
        assert col in result.columns
