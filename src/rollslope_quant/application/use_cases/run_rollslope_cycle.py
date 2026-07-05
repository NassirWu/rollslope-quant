from __future__ import annotations

import pandas as pd

from rollslope_quant.application.agents.plutus_router_agent import RollSlopeRouterAgent
from rollslope_quant.application.dto.decision_context_dto import DecisionContextDTO
from rollslope_quant.domain.entities.account_state import AccountState
from rollslope_quant.domain.entities.trade_signal import TradeSignal
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes
from rollslope_quant.infrastructure.model.return_calculator import calculate_log_returns
from rollslope_quant.infrastructure.risk.var_engine import HistoricalVaREngine


def run_rollslope_cycle(
    market_df: pd.DataFrame,
    account_state: AccountState,
    previous_t3: float | None = None,
    price_column: str = "close",
) -> TradeSignal:
    """執行一次完整 RollSlope 決策循環。"""
    if price_column not in market_df.columns:
        raise ValueError(f"market_df must contain column: {price_column}")

    clean = market_df.reset_index(drop=True).copy()
    x = clean.index.to_numpy(dtype=float)
    y = clean[price_column].astype(float).to_numpy()

    slope_result = calculate_dynamic_slopes(x, y)
    returns = calculate_log_returns(clean[price_column])
    var_95 = HistoricalVaREngine(confidence=0.95).calculate_var(returns)

    context = DecisionContextDTO(
        slope_result=slope_result,
        account_state=account_state,
        previous_t3=previous_t3,
        var_95=var_95,
    )
    return RollSlopeRouterAgent().decide(context)
