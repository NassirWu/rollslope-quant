from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rollslope_quant.application.use_cases.execute_trade_signal import (  # noqa: E402
    ExecutionPolicy,
    execute_trade_signal,
)
from rollslope_quant.application.use_cases.run_rollslope_cycle import run_rollslope_cycle  # noqa: E402
from rollslope_quant.domain.entities.account_state import AccountState  # noqa: E402
from rollslope_quant.domain.enums.trade_action import TradeAction  # noqa: E402
from rollslope_quant.infrastructure.broker.paper_trading_broker import PaperTradingBroker  # noqa: E402
from rollslope_quant.infrastructure.broker.shioaji_config import ShioajiBrokerConfig  # noqa: E402
from rollslope_quant.infrastructure.broker.shioaji_stock_broker import ShioajiStockBroker  # noqa: E402
from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data  # noqa: E402


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run one RollSlope signal and optionally execute via Shioaji.")
    parser.add_argument("--symbol", default=os.getenv("ROLLSLOPE_SYMBOL", "2330"))
    parser.add_argument("--equity", type=float, default=float(os.getenv("ROLLSLOPE_EQUITY", "1000000")))
    parser.add_argument("--peak-equity", type=float, default=float(os.getenv("ROLLSLOPE_PEAK_EQUITY", "1000000")))
    parser.add_argument("--max-lots", type=int, default=int(os.getenv("ROLLSLOPE_MAX_LOTS", "1")))
    parser.add_argument(
        "--broker",
        choices=["paper", "shioaji"],
        default=os.getenv("ROLLSLOPE_BROKER", "paper"),
        help="Use paper until simulation has been validated.",
    )
    args = parser.parse_args()

    market_df = generate_v_reversal_market_data()
    latest_price = float(market_df["close"].iloc[-1])
    account_state = AccountState(
        equity=args.equity,
        peak_equity=args.peak_equity,
        cash=args.equity,
    )
    signal = run_rollslope_cycle(market_df=market_df, account_state=account_state)

    print("=" * 72)
    print("RollSlope Quant / Plutus -> Broker Execution Preview")
    print("=" * 72)
    print(f"Symbol       : {args.symbol}")
    print(f"Latest Price : {latest_price:.2f}")
    print(f"Action       : {signal.action.value}")
    print(f"Reason       : {signal.reason}")
    print(f"Position Fr. : {signal.position_fraction:.4f}")
    print(f"Broker       : {args.broker}")
    print("-" * 72)

    if signal.action not in {TradeAction.BUY, TradeAction.SELL}:
        print("No executable order because signal is not BUY/SELL.")
        return

    broker = (
        ShioajiStockBroker(ShioajiBrokerConfig.from_env())
        if args.broker == "shioaji"
        else PaperTradingBroker()
    )
    policy = ExecutionPolicy(max_quantity=args.max_lots)
    result = await execute_trade_signal(
        broker=broker,
        signal=signal,
        symbol=args.symbol,
        latest_price=latest_price,
        account_equity=args.equity,
        policy=policy,
    )
    if result is None:
        print("No order submitted: calculated quantity is below min_quantity.")
    else:
        print(f"Order ID     : {result.broker_order_id}")
        print(f"Status       : {result.status}")
        print(f"Message      : {result.message}")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
