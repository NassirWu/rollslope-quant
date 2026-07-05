from __future__ import annotations

from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data
from rollslope_quant.application.use_cases.run_rollslope_cycle import run_rollslope_cycle
from rollslope_quant.domain.entities.account_state import AccountState


def main() -> None:
    df = generate_v_reversal_market_data()
    signal = run_rollslope_cycle(
        market_df=df,
        account_state=AccountState(equity=1_000_000, peak_equity=1_000_000),
        previous_t3=0.8,
    )
    print(signal)


if __name__ == "__main__":
    main()
