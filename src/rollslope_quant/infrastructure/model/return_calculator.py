from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_log_returns(prices: pd.Series) -> pd.Series:
    """
    計算一階對數收益率。

    Formula:
        r_t = ln(P_t) - ln(P_{t-1})

    用途：
        將非平穩價格序列轉換為相對平穩的收益率序列，供波動率、VaR、HMM 使用。
    """
    clean_prices = prices.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
    if (clean_prices <= 0).any():
        raise ValueError("prices must be positive to calculate log returns")
    return np.log(clean_prices).diff().dropna()
