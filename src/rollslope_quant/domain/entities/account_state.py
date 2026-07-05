from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AccountState:
    """交易帳戶狀態。"""

    equity: float
    peak_equity: float
    cash: float = 0.0
    current_position_qty: float = 0.0
    current_position_value: float = 0.0

    @property
    def drawdown(self) -> float:
        """
        帳戶回撤比例。

        Formula:
            drawdown = (peak_equity - equity) / peak_equity
        """
        if self.peak_equity <= 0:
            return 0.0
        return max(0.0, (self.peak_equity - self.equity) / self.peak_equity)
