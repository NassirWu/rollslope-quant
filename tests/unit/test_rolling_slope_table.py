from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from rollslope_quant.application.services.rolling_slope_table import (
    calculate_rolling_slope_table,
    calculate_rolling_slope_table_from_dataframe,
)
from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data

MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "rollslope_quant"
    / "application"
    / "services"
    / "rolling_slope_table.py"
)


def _synthetic_xy(n: int = 20) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(1)
    x = np.arange(n, dtype=float) * 2.0 + 100.0
    y = np.arange(n, dtype=float) * 0.5 + rng.normal(0, 0.1, n)
    return x, y


def test_v_reversal_data_produces_non_empty_rolling_table() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    table = calculate_rolling_slope_table_from_dataframe(df, window_size=30)

    assert isinstance(table, pd.DataFrame)
    assert len(table) > 0


def test_table_contains_engineering_and_user_named_columns() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    table = calculate_rolling_slope_table_from_dataframe(df, window_size=30)

    for col in ("t1", "t2", "t3", "z1", "z2", "z3"):
        assert col in table.columns


def test_z_columns_equal_t_columns() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    table = calculate_rolling_slope_table_from_dataframe(df, window_size=30)
    successful = table[table["error"].isna()]

    assert len(successful) > 0
    assert (successful["z1"] == successful["t1"]).all()
    assert (successful["z2"] == successful["t2"]).all()
    assert (successful["z3"] == successful["t3"]).all()


def test_window_start_and_window_end_are_correct() -> None:
    x, y = _synthetic_xy(20)

    table = calculate_rolling_slope_table(x, y, window_size=10, step_size=5)

    assert list(table["window_start"]) == [0, 5, 10]
    assert list(table["window_end"]) == [9, 14, 19]


def test_x_start_and_x_end_columns_present() -> None:
    x, y = _synthetic_xy(20)

    table = calculate_rolling_slope_table(x, y, window_size=10, step_size=5)

    assert "x_start" in table.columns
    assert "x_end" in table.columns


def test_x_start_and_x_end_match_actual_window_x_values() -> None:
    x, y = _synthetic_xy(20)

    table = calculate_rolling_slope_table(x, y, window_size=10, step_size=5)

    for _, row in table.iterrows():
        expected_x_start = x[int(row["window_start"])]
        expected_x_end = x[int(row["window_end"])]
        assert row["x_start"] == pytest.approx(expected_x_start)
        assert row["x_end"] == pytest.approx(expected_x_end)


def test_window_size_below_minimum_raises_value_error() -> None:
    x, y = _synthetic_xy(20)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table(x, y, window_size=5)


def test_step_size_below_minimum_raises_value_error() -> None:
    x, y = _synthetic_xy(20)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table(x, y, window_size=10, step_size=0)


def test_mismatched_x_y_length_raises_value_error() -> None:
    x = list(range(20))
    y = list(range(19))

    with pytest.raises(ValueError):
        calculate_rolling_slope_table(x, y, window_size=10)


def test_data_shorter_than_window_size_raises_value_error() -> None:
    x, y = _synthetic_xy(10)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table(x, y, window_size=20)


def test_dataframe_missing_price_col_raises_value_error() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table_from_dataframe(df, price_col="not_exist", window_size=30)


def test_dataframe_missing_x_col_raises_value_error() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table_from_dataframe(df, x_col="not_exist", window_size=30)


def test_min_r_squared_below_zero_raises_value_error() -> None:
    x, y = _synthetic_xy(20)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table(x, y, window_size=10, min_r_squared=-0.1)


def test_min_r_squared_above_one_raises_value_error() -> None:
    x, y = _synthetic_xy(20)

    with pytest.raises(ValueError):
        calculate_rolling_slope_table(x, y, window_size=10, min_r_squared=1.1)


def test_min_r_squared_produces_is_valid_column() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    table = calculate_rolling_slope_table_from_dataframe(df, window_size=30, min_r_squared=0.9)

    assert "is_valid" in table.columns
    successful = table[table["error"].isna()]
    assert (successful["is_valid"] == (successful["r_squared"] >= 0.9)).all()


def test_without_min_r_squared_is_valid_column_absent() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    table = calculate_rolling_slope_table_from_dataframe(df, window_size=30)

    assert "is_valid" not in table.columns


def test_no_trade_signal_columns_are_produced() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    table = calculate_rolling_slope_table_from_dataframe(df, window_size=30, min_r_squared=0.9)

    forbidden = {"signal", "action", "buy", "sell"}
    assert forbidden.isdisjoint(set(table.columns))


def test_module_source_does_not_reference_broker_shioaji_or_plutus() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()

    assert "shioaji" not in source
    assert "broker" not in source
    assert "plutus" not in source
