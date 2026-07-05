from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ShioajiBrokerConfig:
    """
    永豐 Shioaji Broker Adapter 設定。

    安全原則：
        - 預設 simulation=True。
        - 若 simulation=False，必須同時設定 allow_live_trading=True，否則拒絕送單。
        - API key、secret key、CA 密碼不得寫入程式碼或 Git。
    """

    api_key: str
    secret_key: str
    simulation: bool = True
    ca_path: str | None = None
    ca_password: str | None = None
    person_id: str | None = None
    default_exchange: str = "TSE"
    allow_live_trading: bool = False
    fetch_contract: bool = True
    contracts_timeout: int = 30_000
    receive_window: int = 30_000

    @classmethod
    def from_env(cls) -> "ShioajiBrokerConfig":
        simulation = os.getenv("SHIOAJI_SIMULATION", "true").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }
        allow_live_trading = os.getenv("ALLOW_LIVE_TRADING", "false").strip().lower() in {
            "1",
            "true",
            "yes",
            "y",
        }
        api_key = os.getenv("SHIOAJI_API_KEY", "")
        secret_key = os.getenv("SHIOAJI_SECRET_KEY", "")
        return cls(
            api_key=api_key,
            secret_key=secret_key,
            simulation=simulation,
            ca_path=os.getenv("SHIOAJI_CA_PATH") or None,
            ca_password=os.getenv("SHIOAJI_CA_PASSWORD") or None,
            person_id=os.getenv("SHIOAJI_PERSON_ID") or None,
            default_exchange=os.getenv("SHIOAJI_DEFAULT_EXCHANGE", "TSE").upper(),
            allow_live_trading=allow_live_trading,
            fetch_contract=os.getenv("SHIOAJI_FETCH_CONTRACT", "true").strip().lower()
            in {"1", "true", "yes", "y"},
            contracts_timeout=int(os.getenv("SHIOAJI_CONTRACTS_TIMEOUT", "30000")),
            receive_window=int(os.getenv("SHIOAJI_RECEIVE_WINDOW", "30000")),
        )

    def validate_for_login(self) -> None:
        if not self.api_key or not self.secret_key:
            raise ValueError("SHIOAJI_API_KEY and SHIOAJI_SECRET_KEY are required")
        if not self.simulation and not self.allow_live_trading:
            raise PermissionError(
                "Live trading is blocked. Set ALLOW_LIVE_TRADING=true only after paper/simulation validation."
            )
        if self.ca_path and not Path(self.ca_path).exists():
            raise FileNotFoundError(f"CA file not found: {self.ca_path}")
