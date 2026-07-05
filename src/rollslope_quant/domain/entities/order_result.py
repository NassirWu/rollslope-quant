from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class OrderResult:
    """券商委託回報的中立結果模型。"""

    broker_order_id: str
    status: str
    message: str
    raw: dict[str, Any] = field(default_factory=dict)
