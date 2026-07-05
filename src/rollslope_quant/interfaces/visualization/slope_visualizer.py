from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg", force=True)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from rollslope_quant.domain.entities.slope_result import SlopeResult
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes


def plot_slope_fitting(
    x: Iterable[float],
    y: Iterable[float],
    slope_result: SlopeResult,
    *,
    show: bool = False,
    save_path: str | Path | None = None,
    ax: Axes | None = None,
) -> Figure:
    """人工複查用：畫出原始資料、三段擬合線與兩個轉折點。不產生任何交易判斷。"""
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    fitted_arr = np.asarray(slope_result.fitted_y, dtype=float)

    if not (len(x_arr) == len(y_arr) == len(fitted_arr)):
        raise ValueError(
            "x, y and slope_result.fitted_y must have the same length, got "
            f"{len(x_arr)}, {len(y_arr)}, {len(fitted_arr)}"
        )
    if len(slope_result.breakpoints) != 2:
        raise ValueError(
            f"slope_result.breakpoints must contain exactly 2 values, got {len(slope_result.breakpoints)}"
        )

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.figure

    ax.scatter(x_arr, y_arr, s=12, alpha=0.5, label="Raw Price")

    order = np.argsort(x_arr)
    x_sorted = x_arr[order]
    fitted_sorted = fitted_arr[order]

    b1, b2 = slope_result.breakpoints

    seg_a_mask = x_sorted <= b1
    seg_b_mask = (x_sorted > b1) & (x_sorted <= b2)
    seg_c_mask = x_sorted > b2

    ax.plot(
        x_sorted[seg_a_mask],
        fitted_sorted[seg_a_mask],
        linewidth=2,
        label=f"Segment A (t1/z1={slope_result.t1:.3f})",
    )
    ax.plot(
        x_sorted[seg_b_mask],
        fitted_sorted[seg_b_mask],
        linewidth=2,
        label=f"Segment B (t2/z2={slope_result.t2:.3f})",
    )
    ax.plot(
        x_sorted[seg_c_mask],
        fitted_sorted[seg_c_mask],
        linewidth=2,
        label=f"Segment C (t3/z3={slope_result.t3:.3f})",
    )

    ax.axvline(b1, linestyle="--", linewidth=1, label="Breakpoint 1")
    ax.axvline(b2, linestyle="--", linewidth=1, label="Breakpoint 2")

    ax.set_title(
        "RollSlope Dynamic Slope Fit\n"
        f"Slope A (t1/z1): {slope_result.t1:.3f}  |  "
        f"Slope B (t2/z2): {slope_result.t2:.3f}  |  "
        f"Slope C (t3/z3): {slope_result.t3:.3f}  |  "
        f"R-squared: {slope_result.r_squared:.3f}"
    )
    ax.set_xlabel("x (time index)")
    ax.set_ylabel("y (price)")
    ax.legend(loc="best", fontsize=8)

    if save_path is not None:
        fig.savefig(save_path)
    if show:
        plt.show()

    return fig


def plot_from_dataframe(
    df: pd.DataFrame,
    slope_result: SlopeResult | None = None,
    *,
    x_col: str | None = None,
    price_col: str = "close",
    show: bool = False,
    save_path: str | Path | None = None,
) -> Figure:
    """人工複查用的 DataFrame 輔助接口。不產生任何交易判斷。"""
    if price_col not in df.columns:
        raise ValueError(f"price_col {price_col!r} not found in DataFrame columns: {list(df.columns)}")
    if x_col is not None and x_col not in df.columns:
        raise ValueError(f"x_col {x_col!r} not found in DataFrame columns: {list(df.columns)}")

    x = df.index.to_numpy(dtype=float) if x_col is None else df[x_col].to_numpy(dtype=float)
    y = df[price_col].to_numpy(dtype=float)

    if slope_result is None:
        slope_result = calculate_dynamic_slopes(x, y)

    return plot_slope_fitting(x, y, slope_result, show=show, save_path=save_path)
