from __future__ import annotations

import pandas as pd


def calculate_rolling_volatility(log_returns: pd.Series, window: int = 20) -> pd.Series:
    """
    計算滾動標準差波動率。

    Formula:
        σ_t = std(r_{t-window+1}, ..., r_t)

    其中：
        r_t = ln(P_t) - ln(P_{t-1})
    """
    if window < 2:
        raise ValueError("window must be >= 2")
    return log_returns.rolling(window=window).std().dropna()
