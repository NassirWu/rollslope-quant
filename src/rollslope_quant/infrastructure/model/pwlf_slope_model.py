from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from rollslope_quant.domain.entities.slope_result import SlopeResult


@dataclass(frozen=True, slots=True)
class CleanSeries:
    x: np.ndarray
    y: np.ndarray


def _clean_xy(x: Iterable[float], y: Iterable[float]) -> CleanSeries:
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    if x_arr.shape != y_arr.shape:
        raise ValueError(f"x and y must have same shape, got {x_arr.shape} and {y_arr.shape}")
    mask = np.isfinite(x_arr) & np.isfinite(y_arr)
    x_arr = x_arr[mask]
    y_arr = y_arr[mask]
    if len(x_arr) < 6:
        raise ValueError("at least 6 valid observations are required for 3-segment fitting")
    order = np.argsort(x_arr)
    return CleanSeries(x=x_arr[order], y=y_arr[order])


def _r_squared(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    if ss_tot <= 0:
        return 1.0 if ss_res <= 1e-12 else 0.0
    return 1.0 - ss_res / ss_tot


def _fit_line(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float, np.ndarray]:
    """Return slope, intercept, SSE, fitted_y for one linear segment."""
    slope, intercept = np.polyfit(x, y, deg=1)
    fitted = slope * x + intercept
    sse = float(np.sum((y - fitted) ** 2))
    return float(slope), float(intercept), sse, fitted


def _fit_with_numpy_dynamic_programming(
    x: np.ndarray,
    y: np.ndarray,
    min_segment_size: int = 5,
) -> SlopeResult:
    """
    NumPy fallback：枚舉兩個內部切點，最小化三段線性 SSE。

    目標函數：
        argmin_{b1,b2} Σ_j Σ_i (y_i - (a_j + t_j x_i))²

    約束：
        每段至少 min_segment_size 個樣本。

    此方法用於 demo 或無法安裝 pwlf 時；正式環境優先使用 pwlf。
    """
    n = len(x)
    if n < min_segment_size * 3:
        min_segment_size = max(2, n // 5)

    best: tuple[float, int, int, tuple[float, float, float], np.ndarray] | None = None

    for b1 in range(min_segment_size, n - 2 * min_segment_size + 1):
        for b2 in range(b1 + min_segment_size, n - min_segment_size + 1):
            segments = ((0, b1), (b1, b2), (b2, n))
            slopes: list[float] = []
            fitted_parts: list[np.ndarray] = []
            total_sse = 0.0
            valid = True
            for start, end in segments:
                if end - start < 2:
                    valid = False
                    break
                slope, _, sse, fitted = _fit_line(x[start:end], y[start:end])
                slopes.append(slope)
                fitted_parts.append(fitted)
                total_sse += sse
            if not valid:
                continue
            fitted_y = np.concatenate(fitted_parts)
            if best is None or total_sse < best[0]:
                best = (total_sse, b1, b2, (slopes[0], slopes[1], slopes[2]), fitted_y)

    if best is None:
        raise RuntimeError("failed to find valid 3-segment fit")

    _, b1, b2, slopes, fitted_y = best
    return SlopeResult.from_sequence(
        slopes=slopes,
        breakpoints=(x[b1], x[b2]),
        r_squared=_r_squared(y, fitted_y),
        fitted_y=fitted_y,
        model_name="numpy_dp_fallback",
    )


def calculate_dynamic_slopes(
    x: Iterable[float],
    y: Iterable[float],
    n_segments: int = 3,
    min_segment_size: int = 5,
) -> SlopeResult:
    """
    計算 RollSlope Quant 核心動態斜率 t1, t2, t3。

    Parameters:
        x:
            時間索引。可使用 0,1,2,... 或 Unix timestamp。
        y:
            價格序列或標準化價格序列。
        n_segments:
            分段數。本系統固定使用 3 段。
        min_segment_size:
            fallback 模型每段最低樣本數。

    Mathematical Definition:
        Piecewise Linear Regression:

            y_i ≈ a_j + t_j x_i,  for x_i ∈ [b_{j-1}, b_j]

        where j ∈ {1,2,3}, and t_j is the slope of each segment.

        The model searches four nodes:
            b_0, b_1, b_2, b_3

        Internal breakpoints:
            b_1, b_2

        Output:
            t1 = slope of early stage
            t2 = slope of middle stage
            t3 = slope of latest stage

        Goodness of fit:
            R² = 1 - Σ(y_i - ŷ_i)² / Σ(y_i - mean(y))²

    Returns:
        SlopeResult containing t1, t2, t3, breakpoints, R² and fitted_y.

    Notes:
        正式環境優先使用 pwlf.PiecewiseLinFit.fit(3)。
        若 pwlf 未安裝，會使用內建 NumPy dynamic programming fallback。
    """
    if n_segments != 3:
        raise ValueError("RollSlope Quant currently supports exactly 3 segments")

    clean = _clean_xy(x, y)
    x_arr, y_arr = clean.x, clean.y

    try:
        import pwlf  # type: ignore

        model = pwlf.PiecewiseLinFit(x_arr, y_arr)
        breaks = model.fit(n_segments)
        fitted = np.asarray(model.predict(x_arr), dtype=float)
        slopes = tuple(float(v) for v in model.slopes[:3])
        internal_breakpoints = (float(breaks[1]), float(breaks[2]))
        return SlopeResult.from_sequence(
            slopes=slopes,
            breakpoints=internal_breakpoints,
            r_squared=_r_squared(y_arr, fitted),
            fitted_y=fitted,
            model_name="pwlf",
        )
    except ImportError:
        return _fit_with_numpy_dynamic_programming(x_arr, y_arr, min_segment_size=min_segment_size)
