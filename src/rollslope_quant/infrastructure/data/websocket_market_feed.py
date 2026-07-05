from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator


class WebSocketMarketFeed:
    """WebSocket 行情接收器骨架。正式環境接交易所或券商 WebSocket。"""

    def __init__(self, url: str) -> None:
        self.url = url
        self.connected = False

    async def connect(self) -> None:
        self.connected = True

    async def reconnect(self) -> None:
        self.connected = False
        await asyncio.sleep(0.1)
        await self.connect()

    async def stream(self) -> AsyncIterator[dict[str, float | str]]:
        if not self.connected:
            await self.connect()
        while self.connected:
            await asyncio.sleep(1)
            yield {}
