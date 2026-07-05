from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class OrderRequest:
    """
    交易委託請求。

    Clean Architecture 用途：
        Domain/Application 只認識這個中立委託模型，不直接依賴 Shioaji、IB、
        PaperBroker 或任何實際券商 SDK。

    quantity 說明：
        台股整股下單時，Shioaji 的 quantity 代表「張數」，1 = 1000 股。
        若使用盤中零股，才會依券商 API 對應股數語義處理。
    """

    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: int
    price: float = 0.0
    order_kind: Literal["MARKET", "LIMIT"] = "MARKET"
    exchange: Literal["TSE", "OTC"] = "TSE"
    order_type: Literal["ROD", "IOC", "FOK"] = "IOC"
    order_lot: Literal["Common", "IntradayOdd", "Odd", "Fixing"] = "Common"
    order_cond: Literal["Cash", "MarginTrading", "ShortSelling"] = "Cash"
    daytrade_short: bool = False
    custom_field: str = "RSQ001"

    def __post_init__(self) -> None:
        if not self.symbol.strip():
            raise ValueError("symbol must not be empty")
        if self.side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.order_kind == "LIMIT" and self.price <= 0:
            raise ValueError("LIMIT order requires positive price")
        if len(self.custom_field) > 6 or not self.custom_field.isalnum():
            raise ValueError("custom_field must be alphanumeric and <= 6 characters")
