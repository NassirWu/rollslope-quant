from __future__ import annotations

import pytest

from rollslope_quant.application.use_cases.execute_trade_signal import (
    ExecutionPolicy,
    execute_trade_signal,
    signal_to_order_request,
)
from rollslope_quant.domain.entities.trade_signal import TradeSignal
from rollslope_quant.domain.enums.trade_action import TradeAction
from rollslope_quant.infrastructure.broker.paper_trading_broker import PaperTradingBroker


def test_signal_to_order_request_buy_market_lot() -> None:
    signal = TradeSignal(
        action=TradeAction.BUY,
        reason="test",
        position_fraction=0.25,
    )
    request = signal_to_order_request(
        signal=signal,
        symbol="2330",
        latest_price=100.0,
        account_equity=1_000_000,
        policy=ExecutionPolicy(max_quantity=10),
    )

    assert request is not None
    assert request.symbol == "2330"
    assert request.side == "BUY"
    assert request.quantity == 2
    assert request.order_kind == "MARKET"
    assert request.order_type == "IOC"


def test_signal_to_order_request_returns_none_when_qty_too_small() -> None:
    signal = TradeSignal(
        action=TradeAction.BUY,
        reason="test",
        position_fraction=0.01,
    )
    request = signal_to_order_request(
        signal=signal,
        symbol="2330",
        latest_price=1000.0,
        account_equity=100_000,
        policy=ExecutionPolicy(max_quantity=10),
    )

    assert request is None


@pytest.mark.asyncio
async def test_execute_trade_signal_with_paper_broker() -> None:
    signal = TradeSignal(
        action=TradeAction.BUY,
        reason="test",
        position_fraction=0.25,
    )
    result = await execute_trade_signal(
        broker=PaperTradingBroker(),
        signal=signal,
        symbol="2330",
        latest_price=100.0,
        account_equity=1_000_000,
        policy=ExecutionPolicy(max_quantity=1),
    )

    assert result is not None
    assert result.status == "SIMULATED_ACCEPTED"
    assert result.broker_order_id.startswith("paper-2330-BUY")
