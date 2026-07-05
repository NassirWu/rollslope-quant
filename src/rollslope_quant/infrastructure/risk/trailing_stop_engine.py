from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrailingStopEngine:
    """動態追蹤止損計算器。"""

    default_stop_loss_pct: float = 0.03
    tightened_stop_loss_pct: float = 0.015

    def calculate_long_stop(self, highest_price: float, tightened: bool = False) -> float:
        """
        多單追蹤止損。

        Formula:
            stop = highest_price * (1 - stop_loss_pct)
        """
        pct = self.tightened_stop_loss_pct if tightened else self.default_stop_loss_pct
        return highest_price * (1.0 - pct)

    def calculate_short_stop(self, lowest_price: float, tightened: bool = False) -> float:
        """
        空單追蹤止損。

        Formula:
            stop = lowest_price * (1 + stop_loss_pct)
        """
        pct = self.tightened_stop_loss_pct if tightened else self.default_stop_loss_pct
        return lowest_price * (1.0 + pct)
