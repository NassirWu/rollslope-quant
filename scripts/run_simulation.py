from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rollslope_quant.application.dto.decision_context_dto import DecisionContextDTO
from rollslope_quant.application.agents.plutus_router_agent import RollSlopeRouterAgent
from rollslope_quant.domain.entities.account_state import AccountState
from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes
from rollslope_quant.infrastructure.model.return_calculator import calculate_log_returns
from rollslope_quant.infrastructure.model.volatility_calculator import calculate_rolling_volatility
from rollslope_quant.infrastructure.risk.var_engine import HistoricalVaREngine


def main() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)
    x = df.index.to_numpy(dtype=float)
    y = df["close"].to_numpy(dtype=float)

    slope_result = calculate_dynamic_slopes(x, y)
    log_returns = calculate_log_returns(df["close"])
    rolling_vol = calculate_rolling_volatility(log_returns, window=20)
    var_95 = HistoricalVaREngine(confidence=0.95).calculate_var(log_returns)

    account = AccountState(
        equity=1_000_000.0,
        peak_equity=1_020_000.0,
        cash=1_000_000.0,
        current_position_qty=0.0,
        current_position_value=0.0,
    )

    context = DecisionContextDTO(
        slope_result=slope_result,
        account_state=account,
        previous_t3=0.80,
        var_95=var_95,
        max_var_95=0.05,
        win_probability=0.55,
        win_loss_ratio=1.50,
        kelly_cap=0.25,
    )

    signal = RollSlopeRouterAgent().decide(context)

    print("=" * 72)
    print("RollSlope Quant / Plutus V-Reversal Simulation")
    print("=" * 72)
    print(f"Model                  : {slope_result.model_name}")
    print(f"t1                     : {slope_result.t1:.4f}")
    print(f"t2                     : {slope_result.t2:.4f}")
    print(f"t3                     : {slope_result.t3:.4f}")
    print(f"Breakpoints            : {tuple(round(v, 2) for v in slope_result.breakpoints)}")
    print(f"R Squared              : {slope_result.r_squared:.4f}")
    print(f"Rolling Vol Latest     : {rolling_vol.iloc[-1]:.6f}")
    print(f"Historical VaR 95      : {var_95:.6f}")
    print("-" * 72)
    print(f"Plutus Action          : {signal.action.value}")
    print(f"Route To               : {signal.route_to}")
    print(f"Position Fraction      : {signal.position_fraction:.4f}")
    print(f"Risk Level             : {signal.risk_level.value}")
    print(f"Confidence             : {signal.confidence:.4f}")
    print(f"Reason                 : {signal.reason}")
    print(f"Trailing Stop Required : {signal.metadata.get('trailing_stop_required')}")
    print("=" * 72)


if __name__ == "__main__":
    main()
