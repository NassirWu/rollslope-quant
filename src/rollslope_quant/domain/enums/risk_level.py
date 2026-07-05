from enum import Enum


class RiskLevel(str, Enum):
    """風險等級。"""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
