from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Any

from rollslope_quant.domain.entities.order_request import OrderRequest
from rollslope_quant.domain.entities.order_result import OrderResult
from rollslope_quant.infrastructure.broker.shioaji_config import ShioajiBrokerConfig


class ShioajiDependencyError(RuntimeError):
    """shioaji 套件尚未安裝時丟出。"""


class ShioajiStockBroker:
    """
    永豐金證券 Shioaji 台股下單 Adapter。

    Clean Architecture 邊界：
        Application Layer -> BrokerPort -> ShioajiStockBroker -> shioaji SDK

    支援：
        - simulation=True 模擬環境登入
        - 證券整股現股委託
        - 市價 / 限價
        - ROD / IOC / FOK
        - Common / IntradayOdd / Odd / Fixing lot enum 映射

    注意：
        正式環境下單前須完成永豐 API 簽署、測試、CA 憑證啟用與帳戶權限確認。
    """

    def __init__(self, config: ShioajiBrokerConfig | None = None) -> None:
        self.config = config or ShioajiBrokerConfig.from_env()
        self._sj: Any | None = None
        self._api: Any | None = None
        self._connected = False

    async def connect(self) -> None:
        self.config.validate_for_login()
        await asyncio.to_thread(self._connect_sync)

    def _connect_sync(self) -> None:
        try:
            import shioaji as sj  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            raise ShioajiDependencyError(
                "shioaji is not installed. Run: pip install shioaji"
            ) from exc

        self._sj = sj
        self._api = sj.Shioaji(simulation=self.config.simulation)
        self._api.login(
            api_key=self.config.api_key,
            secret_key=self.config.secret_key,
            fetch_contract=self.config.fetch_contract,
            contracts_timeout=self.config.contracts_timeout,
            receive_window=self.config.receive_window,
        )
        self._activate_ca_if_configured()
        self._connected = True

    def _activate_ca_if_configured(self) -> None:
        if not self.config.ca_path:
            return
        if not self.config.ca_password or not self.config.person_id:
            raise ValueError(
                "SHIOAJI_CA_PASSWORD and SHIOAJI_PERSON_ID are required when SHIOAJI_CA_PATH is set"
            )
        assert self._api is not None
        self._api.activate_ca(
            ca_path=self.config.ca_path,
            ca_passwd=self.config.ca_password,
            person_id=self.config.person_id,
        )

    async def disconnect(self) -> None:
        if self._api is None:
            return
        await asyncio.to_thread(self._disconnect_sync)

    def _disconnect_sync(self) -> None:
        if self._api is not None:
            logout = getattr(self._api, "logout", None)
            if callable(logout):
                logout()
        self._connected = False

    async def submit_order(self, request: OrderRequest) -> OrderResult:
        if not self._connected:
            await self.connect()
        return await asyncio.to_thread(self._submit_order_sync, request)

    async def submit_market_order(self, symbol: str, side: str, quantity: float) -> str:
        request = OrderRequest(
            symbol=symbol,
            side=side.upper(),  # type: ignore[arg-type]
            quantity=int(quantity),
            order_kind="MARKET",
            exchange=self.config.default_exchange,  # type: ignore[arg-type]
            order_type="IOC",
        )
        result = await self.submit_order(request)
        return result.broker_order_id

    def _submit_order_sync(self, request: OrderRequest) -> OrderResult:
        if self._api is None or self._sj is None:
            raise RuntimeError("Shioaji broker is not connected")
        if not self.config.simulation and not self.config.allow_live_trading:
            raise PermissionError("Live trading is blocked by ALLOW_LIVE_TRADING=false")

        contract = self._resolve_stock_contract(request.symbol, request.exchange)
        order = self._build_stock_order(request)
        trade = self._api.place_order(contract, order)
        return self._trade_to_order_result(trade)

    def _resolve_stock_contract(self, symbol: str, exchange: str) -> Any:
        """依台股代碼取得 Shioaji Contract，支援 TSE/OTC 常見路徑。"""
        assert self._api is not None
        code = symbol.strip().upper()
        exchange = exchange.strip().upper()
        stocks = self._api.Contracts.Stocks

        candidates: list[Any] = []
        market = getattr(stocks, exchange, None)
        if market is not None:
            candidates.extend(
                [
                    getattr(market, f"{exchange}{code}", None),
                    getattr(market, code, None),
                ]
            )
            try:
                candidates.append(market[code])
            except Exception:
                pass
            try:
                candidates.append(market[f"{exchange}{code}"])
            except Exception:
                pass

        try:
            candidates.append(stocks[code])
        except Exception:
            pass

        for contract in candidates:
            if contract is not None:
                return contract
        raise LookupError(f"Unable to resolve stock contract: exchange={exchange}, symbol={code}")

    def _build_stock_order(self, request: OrderRequest) -> Any:
        assert self._api is not None and self._sj is not None
        sj = self._sj

        action = sj.Action.Buy if request.side == "BUY" else sj.Action.Sell
        price_type = (
            sj.StockPriceType.MKT if request.order_kind == "MARKET" else sj.StockPriceType.LMT
        )
        price = 0 if request.order_kind == "MARKET" else request.price
        order_type = getattr(sj.OrderType, request.order_type)
        order_lot = getattr(sj.StockOrderLot, request.order_lot)
        order_cond = getattr(sj.StockOrderCond, request.order_cond)

        return sj.StockOrder(
            action=action,
            price=price,
            quantity=request.quantity,
            price_type=price_type,
            order_type=order_type,
            order_lot=order_lot,
            order_cond=order_cond,
            daytrade_short=request.daytrade_short,
            custom_field=request.custom_field,
            account=self._api.stock_account,
        )

    def _trade_to_order_result(self, trade: Any) -> OrderResult:
        status = getattr(trade, "status", None)
        order = getattr(trade, "order", None)

        broker_order_id = str(
            getattr(status, "id", None)
            or getattr(order, "id", None)
            or getattr(order, "ordno", None)
            or "UNKNOWN"
        )
        status_name = str(getattr(status, "status", "UNKNOWN"))
        message = str(getattr(status, "msg", ""))

        raw = {
            "trade_repr": repr(trade),
            "broker_order_id": broker_order_id,
            "status": status_name,
            "message": message,
        }
        return OrderResult(
            broker_order_id=broker_order_id,
            status=status_name,
            message=message,
            raw=raw,
        )
