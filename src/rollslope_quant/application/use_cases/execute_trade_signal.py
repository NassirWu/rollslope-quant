from __future__ import annotations

from dataclasses import dataclass

from rollslope_quant.domain.entities.order_request import OrderRequest
from rollslope_quant.domain.entities.order_result import OrderResult
from rollslope_quant.domain.entities.trade_signal import TradeSignal
from rollslope_quant.domain.enums.trade_action import TradeAction
from rollslope_quant.domain.ports.broker_port import BrokerPort


@dataclass(frozen=True, slots=True)
class ExecutionPolicy:
    """
    訊號轉委託政策。

    max_quantity:
        單次最大張數限制。避免 Kelly 或模型異常時送出過大委託。
    min_quantity:
        最小張數限制。低於此數量則不送單。
    allow_short:
        台股現股預設不開放放空。倒 V 頂 SELL 預設視為減倉/賣出既有持股。
    """

    max_quantity: int = 1
    min_quantity: int = 1
    allow_short: bool = False
    default_exchange: str = "TSE"
    order_kind: str = "MARKET"
    order_type: str = "IOC"


def signal_to_order_request(
    signal: TradeSignal,
    symbol: str,
    latest_price: float,
    account_equity: float,
    policy: ExecutionPolicy | None = None,
) -> OrderRequest | None:
    """
    將 Plutus 的 TradeSignal 轉換為券商委託。

    Position sizing:
        target_notional = equity * position_fraction
        raw_lots = target_notional / (latest_price * 1000)
        quantity = floor(raw_lots)

    台股整股 quantity 語義：
        1 張 = 1000 股。
    """
    policy = policy or ExecutionPolicy()
    if signal.action not in {TradeAction.BUY, TradeAction.SELL}:
        return None
    if latest_price <= 0:
        raise ValueError("latest_price must be positive")
    if account_equity <= 0:
        raise ValueError("account_equity must be positive")

    side = "BUY" if signal.action == TradeAction.BUY else "SELL"
    if side == "SELL" and not policy.allow_short:
        # 在台股現股模式下，SELL 只代表賣出既有部位；實際持倉檢查由上層風控/帳務模組負責。
        pass

    target_notional = account_equity * signal.position_fraction
    raw_lots = int(target_notional // (latest_price * 1000))
    quantity = min(policy.max_quantity, raw_lots)
    if quantity < policy.min_quantity:
        return None

    return OrderRequest(
        symbol=symbol,
        side=side,  # type: ignore[arg-type]
        quantity=quantity,
        price=0.0 if policy.order_kind == "MARKET" else latest_price,
        order_kind=policy.order_kind,  # type: ignore[arg-type]
        exchange=policy.default_exchange,  # type: ignore[arg-type]
        order_type=policy.order_type,  # type: ignore[arg-type]
    )


async def execute_trade_signal(
    broker: BrokerPort,
    signal: TradeSignal,
    symbol: str,
    latest_price: float,
    account_equity: float,
    policy: ExecutionPolicy | None = None,
) -> OrderResult | None:
    """根據 Plutus 訊號送單。非 BUY/SELL 或張數不足時回傳 None。"""
    request = signal_to_order_request(
        signal=signal,
        symbol=symbol,
        latest_price=latest_price,
        account_equity=account_equity,
        policy=policy,
    )
    if request is None:
        return None
    await broker.connect()
    return await broker.submit_order(request)
