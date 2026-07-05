from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True, slots=True)
class HistoricalVaREngine:
    """
    Historical VaR 風險模型。

    Formula:
        VaR_α = -Quantile(R, 1 - α)

    Example:
        confidence = 0.95
        VaR_95 = -5th percentile of historical returns

    輸出為正數，代表在信心水準 α 下的單期潛在損失比例。
    """

    confidence: float = 0.95

    def calculate_var(self, returns: pd.Series) -> float:
        clean = returns.astype(float).replace([np.inf, -np.inf], np.nan).dropna()
        if clean.empty:
            return 0.0
        loss_quantile = float(clean.quantile(1.0 - self.confidence))
        return max(0.0, -loss_quantile)
