from __future__ import annotations

import numpy as np
import pandas as pd


def generate_v_reversal_market_data(seed: int = 7, n_each: int = 30) -> pd.DataFrame:
    """
    生成「先急跌、再盤整、後急漲」的 V 轉模擬資料。

    結構：
        Stage A: y ≈ 100 - 2.0x
        Stage B: y ≈ constant
        Stage C: y ≈ bottom + 2.4x

    預期斜率：
        t1 < -1.0
        -0.5 <= t2 <= 0.5
        t3 > 1.0
    """
    rng = np.random.default_rng(seed)

    stage_a_x = np.arange(n_each)
    stage_a = 100.0 - 2.0 * stage_a_x + rng.normal(0, 0.35, n_each)

    bottom = float(stage_a[-1])
    stage_b = bottom + rng.normal(0, 0.25, n_each)

    stage_c_x = np.arange(1, n_each + 1)
    stage_c = float(stage_b[-1]) + 2.4 * stage_c_x + rng.normal(0, 0.35, n_each)

    close = np.concatenate([stage_a, stage_b, stage_c])
    timestamp = pd.date_range("2026-01-01 09:00:00", periods=len(close), freq="60min")

    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "open": close + rng.normal(0, 0.15, len(close)),
            "high": close + rng.uniform(0.2, 0.8, len(close)),
            "low": close - rng.uniform(0.2, 0.8, len(close)),
            "close": close,
            "volume": rng.integers(100, 1000, len(close)),
        }
    )


def generate_inverted_v_market_data(seed: int = 11, n_each: int = 30) -> pd.DataFrame:
    """生成「先急漲、再橫盤、後急跌」的倒 V 頂模擬資料。"""
    rng = np.random.default_rng(seed)

    stage_a_x = np.arange(n_each)
    stage_a = 50.0 + 2.0 * stage_a_x + rng.normal(0, 0.35, n_each)

    top = float(stage_a[-1])
    stage_b = top + rng.normal(0, 0.25, n_each)

    stage_c_x = np.arange(1, n_each + 1)
    stage_c = float(stage_b[-1]) - 2.4 * stage_c_x + rng.normal(0, 0.35, n_each)

    close = np.concatenate([stage_a, stage_b, stage_c])
    timestamp = pd.date_range("2026-01-01 09:00:00", periods=len(close), freq="60min")

    return pd.DataFrame(
        {
            "timestamp": timestamp,
            "open": close + rng.normal(0, 0.15, len(close)),
            "high": close + rng.uniform(0.2, 0.8, len(close)),
            "low": close - rng.uniform(0.2, 0.8, len(close)),
            "close": close,
            "volume": rng.integers(100, 1000, len(close)),
        }
    )
