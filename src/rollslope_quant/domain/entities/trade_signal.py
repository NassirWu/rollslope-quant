from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rollslope_quant.domain.enums.trade_action import TradeAction
from rollslope_quant.domain.enums.risk_level import RiskLevel


@dataclass(frozen=True, slots=True)
class TradeSignal:
    """Plutus 產出的交易決策。"""

    action: TradeAction
    reason: str
    confidence: float = 0.0
    position_fraction: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    route_to: str = "PlutusRouterAgent"
    metadata: dict[str, Any] = field(default_factory=dict)
