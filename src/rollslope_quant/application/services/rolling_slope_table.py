from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes

_BASE_COLUMNS = [
    "window_start",
    "window_end",
    "x_start",
    "x_end",
    "t1",
    "t2",
    "t3",
    "z1",
    "z2",
    "z3",
    "breakpoint_1",
    "breakpoint_2",
    "r_squared",
    "model_name",
    "error",
]


def calculate_rolling_slope_table(
    x: Iterable[float],
    y: Iterable[float],
    *,
    window_size: int,
    step_size: int = 1,
    min_r_squared: float | None = None,
) -> pd.DataFrame:
    """
    滾動計算 z1/z2/z3（使用者手寫模型命名，等於工程命名 t1/t2/t3）並輸出 rolling slope table。

    每個固定大小 window 呼叫一次 calculate_dynamic_slopes()；單一 window 擬合失敗時
    該列記錄 error 訊息並填入 NaN，不影響其他 window 的計算。

    不產生任何交易訊號（不輸出 BUY/SELL），僅輸出斜率與擬合統計量。
    """
    if window_size < 6:
        raise ValueError(f"window_size must be >= 6, got {window_size}")
    if step_size < 1:
        raise ValueError(f"step_size must be >= 1, got {step_size}")
    if min_r_squared is not None and not (0.0 <= min_r_squared <= 1.0):
        raise ValueError(f"min_r_squared must be within [0, 1], got {min_r_squared}")

    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    if x_arr.shape != y_arr.shape:
        raise ValueError(f"x and y must have same shape, got {x_arr.shape} and {y_arr.shape}")
    if len(x_arr) < window_size:
        raise ValueError(f"data length ({len(x_arr)}) must be >= window_size ({window_size})")

    rows: list[dict[str, object]] = []
    n = len(x_arr)

    for start in range(0, n - window_size + 1, step_size):
        end = start + window_size
        window_x = x_arr[start:end]
        window_y = y_arr[start:end]

        row: dict[str, object] = {
            "window_start": start,
            "window_end": end - 1,
            "x_start": float(window_x[0]),
            "x_end": float(window_x[-1]),
        }

        try:
            slope_result = calculate_dynamic_slopes(window_x, window_y)
        except Exception as exc:  # noqa: BLE001 - a single bad window must not crash the table
            row.update(
                {
                    "t1": float("nan"),
                    "t2": float("nan"),
                    "t3": float("nan"),
                    "z1": float("nan"),
                    "z2": float("nan"),
                    "z3": float("nan"),
                    "breakpoint_1": float("nan"),
                    "breakpoint_2": float("nan"),
                    "r_squared": float("nan"),
                    "model_name": None,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            if min_r_squared is not None:
                row["is_valid"] = False
            rows.append(row)
            continue

        row.update(
            {
                "t1": slope_result.t1,
                "t2": slope_result.t2,
                "t3": slope_result.t3,
                "z1": slope_result.t1,
                "z2": slope_result.t2,
                "z3": slope_result.t3,
                "breakpoint_1": slope_result.breakpoints[0],
                "breakpoint_2": slope_result.breakpoints[1],
                "r_squared": slope_result.r_squared,
                "model_name": slope_result.model_name,
                "error": None,
            }
        )
        if min_r_squared is not None:
            row["is_valid"] = slope_result.r_squared >= min_r_squared

        rows.append(row)

    columns = list(_BASE_COLUMNS)
    if min_r_squared is not None:
        columns.append("is_valid")

    return pd.DataFrame(rows, columns=columns)


def calculate_rolling_slope_table_from_dataframe(
    df: pd.DataFrame,
    *,
    price_col: str = "close",
    x_col: str | None = None,
    window_size: int,
    step_size: int = 1,
    min_r_squared: float | None = None,
) -> pd.DataFrame:
    """DataFrame 輔助接口：滾動輸出 z1/z2/z3 table。不產生任何交易訊號。"""
    if price_col not in df.columns:
        raise ValueError(f"price_col {price_col!r} not found in DataFrame columns: {list(df.columns)}")
    if x_col is not None and x_col not in df.columns:
        raise ValueError(f"x_col {x_col!r} not found in DataFrame columns: {list(df.columns)}")

    x = df.index.to_numpy(dtype=float) if x_col is None else df[x_col].to_numpy(dtype=float)
    y = df[price_col].to_numpy(dtype=float)

    return calculate_rolling_slope_table(
        x,
        y,
        window_size=window_size,
        step_size=step_size,
        min_r_squared=min_r_squared,
    )
