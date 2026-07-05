from __future__ import annotations

from typing import Protocol

import pandas as pd


class MarketDataPort(Protocol):
    """行情資料抽象介面。"""

    async def fetch_latest_bars(self, symbol: str, limit: int) -> pd.DataFrame:
        ...
