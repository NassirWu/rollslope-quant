from __future__ import annotations

from typing import Protocol

from rollslope_quant.domain.entities.order_request import OrderRequest
from rollslope_quant.domain.entities.order_result import OrderResult


class BrokerPort(Protocol):
    """
    券商下單抽象介面。

    Application Layer 只依賴 BrokerPort，不依賴 Shioaji SDK。
    因此 PaperTradingBroker、ShioajiStockBroker、IBBroker 都可以替換。
    """

    async def connect(self) -> None:
        """登入或初始化券商連線。"""
        ...

    async def disconnect(self) -> None:
        """登出或釋放券商連線。"""
        ...

    async def submit_order(self, request: OrderRequest) -> OrderResult:
        """送出標準化委託。"""
        ...

    async def submit_market_order(self, symbol: str, side: str, quantity: float) -> str:
        """向後相容的簡化市價單介面。"""
        ...
