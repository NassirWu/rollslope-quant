from __future__ import annotations

from dataclasses import dataclass

from rollslope_quant.domain.entities.account_state import AccountState
from rollslope_quant.domain.entities.slope_result import SlopeResult
from rollslope_quant.domain.enums.market_regime import MarketRegime


@dataclass(frozen=True, slots=True)
class DecisionContextDTO:
    """
    Plutus 決策上下文。

    此 DTO 是 Application Layer 的輸入物件，聚合：
    - 模型特徵：SlopeResult
    - 帳戶狀態：AccountState
    - 風控指標：VaR、max drawdown、previous_t3
    - 系統狀態：connection_lost
    - 策略參數：勝率、盈虧比
    """

    slope_result: SlopeResult
    account_state: AccountState
    previous_t3: float | None = None
    var_95: float = 0.0
    max_var_95: float = 0.05
    max_drawdown: float = 0.15
    connection_lost: bool = False
    market_regime: MarketRegime = MarketRegime.UNKNOWN
    win_probability: float = 0.55
    win_loss_ratio: float = 1.50
    kelly_cap: float = 0.25
