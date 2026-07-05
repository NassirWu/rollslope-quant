from __future__ import annotations

import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rollslope_quant.infrastructure.broker.shioaji_config import ShioajiBrokerConfig  # noqa: E402
from rollslope_quant.infrastructure.broker.shioaji_stock_broker import ShioajiStockBroker  # noqa: E402


async def main() -> None:
    broker = ShioajiStockBroker(ShioajiBrokerConfig.from_env())
    await broker.connect()
    print("Shioaji login succeeded.")
    await broker.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
