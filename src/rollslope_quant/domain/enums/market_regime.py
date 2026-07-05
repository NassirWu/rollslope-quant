from enum import Enum


class MarketRegime(str, Enum):
    """市場狀態。HMM 可在未來輸出此枚舉。"""

    UNKNOWN = "UNKNOWN"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    SIDEWAYS = "SIDEWAYS"
