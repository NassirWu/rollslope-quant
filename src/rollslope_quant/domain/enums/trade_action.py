from enum import Enum


class TradeAction(str, Enum):
    """交易動作枚舉。"""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    NO_TRADE = "NO_TRADE"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    RECONNECT_DATA = "RECONNECT_DATA"
    TIGHTEN_TRAILING_STOP = "TIGHTEN_TRAILING_STOP"
