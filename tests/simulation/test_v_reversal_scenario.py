from rollslope_quant.application.dto.decision_context_dto import DecisionContextDTO
from rollslope_quant.application.agents.plutus_router_agent import RollSlopeRouterAgent
from rollslope_quant.domain.entities.account_state import AccountState
from rollslope_quant.domain.enums.trade_action import TradeAction
from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes


def test_v_reversal_scenario_returns_buy() -> None:
    df = generate_v_reversal_market_data(seed=7, n_each=30)
    result = calculate_dynamic_slopes(df.index.to_numpy(dtype=float), df["close"].to_numpy(dtype=float))
    context = DecisionContextDTO(
        slope_result=result,
        account_state=AccountState(equity=1_000_000, peak_equity=1_000_000),
        previous_t3=0.8,
        var_95=0.01,
    )
    signal = RollSlopeRouterAgent().decide(context)
    assert signal.action == TradeAction.BUY
