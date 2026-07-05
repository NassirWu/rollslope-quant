from __future__ import annotations

import numpy as np
import pwlf
import pytest

from rollslope_quant.infrastructure.data.mock_market_data import (
    generate_inverted_v_market_data,
    generate_v_reversal_market_data,
)
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes


def test_v_reversal_data_produces_expected_slope_signs() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)

    result = calculate_dynamic_slopes(
        df.index.to_numpy(dtype=float), df["close"].to_numpy(dtype=float)
    )

    assert result.t1 < 0
    assert abs(result.t2) < 0.5
    assert result.t3 > 0


def test_inverted_v_data_produces_expected_slope_signs() -> None:
    df = generate_inverted_v_market_data(seed=11, n_each=30)

    result = calculate_dynamic_slopes(
        df.index.to_numpy(dtype=float), df["close"].to_numpy(dtype=float)
    )

    assert result.t1 > 0
    assert abs(result.t2) < 0.5
    assert result.t3 < 0


def test_straight_uptrend_produces_three_positive_close_slopes() -> None:
    rng = np.random.default_rng(3)
    n_each = 30
    stage_a_x = np.arange(n_each)
    stage_a = 100.0 + 2.0 * stage_a_x + rng.normal(0, 0.2, n_each)
    stage_b_x = np.arange(1, n_each + 1)
    stage_b = float(stage_a[-1]) + 2.2 * stage_b_x + rng.normal(0, 0.2, n_each)
    stage_c_x = np.arange(1, n_each + 1)
    stage_c = float(stage_b[-1]) + 1.8 * stage_c_x + rng.normal(0, 0.2, n_each)
    y = np.concatenate([stage_a, stage_b, stage_c])
    x = np.arange(len(y), dtype=float)
    result = calculate_dynamic_slopes(x, y)
    assert result.t1 > 0
    assert result.t2 > 0
    assert result.t3 > 0
    assert result.t1 == pytest.approx(2.0, abs=0.3)
    assert result.t2 == pytest.approx(2.2, abs=0.3)
    assert result.t3 == pytest.approx(1.8, abs=0.3)


def test_insufficient_data_raises_value_error() -> None:
    x = [0.0, 1.0, 2.0]
    y = [1.0, 2.0, 3.0]

    with pytest.raises(ValueError):
        calculate_dynamic_slopes(x, y)


def test_mismatched_length_raises_value_error() -> None:
    x = list(range(10))
    y = list(range(9))

    with pytest.raises(ValueError):
        calculate_dynamic_slopes(x, y)


def test_constant_x_raises_value_error() -> None:
    x = [5.0] * 10
    y = list(range(10))

    with pytest.raises(ValueError, match="x values must not be constant"):
        calculate_dynamic_slopes(x, y)


def test_n_segments_other_than_three_raises_value_error() -> None:
    x = np.arange(30, dtype=float)
    y = x.copy()

    with pytest.raises(ValueError):
        calculate_dynamic_slopes(x, y, n_segments=4)


def test_result_contains_breakpoints_r_squared_and_fitted_y() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)
    x = df.index.to_numpy(dtype=float)

    result = calculate_dynamic_slopes(x, df["close"].to_numpy(dtype=float))

    assert len(result.breakpoints) == 2
    assert x.min() < result.breakpoints[0] < result.breakpoints[1] < x.max()
    assert 0.0 <= result.r_squared <= 1.0
    assert len(result.fitted_y) == len(x)


def test_fallback_used_when_pwlf_fit_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_fit(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("simulated pwlf fitting failure")

    monkeypatch.setattr(pwlf.PiecewiseLinFit, "fit", broken_fit)

    rng = np.random.default_rng(5)
    x = np.arange(30, dtype=float)
    y = 2.0 * x + rng.normal(0, 0.2, len(x))

    result = calculate_dynamic_slopes(x, y)

    assert result.model_name == "numpy_dp_fallback"
    assert len(result.fitted_y) == len(x)
