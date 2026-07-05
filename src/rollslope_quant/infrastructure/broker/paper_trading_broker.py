from __future__ import annotations

import uuid
from dataclasses import asdict

from rollslope_quant.domain.entities.order_request import OrderRequest
from rollslope_quant.domain.entities.order_result import OrderResult


class PaperTradingBroker:
    """紙上交易券商 Adapter。"""

    async def connect(self) -> None:
        return None

    async def disconnect(self) -> None:
        return None

    async def submit_order(self, request: OrderRequest) -> OrderResult:
        broker_order_id = f"paper-{request.symbol}-{request.side}-{uuid.uuid4().hex[:12]}"
        return OrderResult(
            broker_order_id=broker_order_id,
            status="SIMULATED_ACCEPTED",
            message="Paper order accepted.",
            raw=asdict(request),
        )

    async def submit_market_order(self, symbol: str, side: str, quantity: float) -> str:
        request = OrderRequest(
            symbol=symbol,
            side=side.upper(),  # type: ignore[arg-type]
            quantity=int(quantity),
            order_kind="MARKET",
        )
        result = await self.submit_order(request)
        return result.broker_order_id
