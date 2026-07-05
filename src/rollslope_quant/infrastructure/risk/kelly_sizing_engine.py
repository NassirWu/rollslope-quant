from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KellySizingEngine:
    """
    Kelly Criterion 部位管理。

    Formula:
        f* = p - (1 - p) / b

    where:
        f* = optimal capital fraction
        p  = win probability
        b  = win/loss payoff ratio

    實務限制：
        為避免 Kelly 過度槓桿，本系統使用 cap 截斷。
    """

    cap: float = 0.25

    def calculate_fraction(self, win_probability: float, win_loss_ratio: float) -> float:
        if not 0 <= win_probability <= 1:
            raise ValueError("win_probability must be in [0, 1]")
        if win_loss_ratio <= 0:
            raise ValueError("win_loss_ratio must be positive")

        raw_fraction = win_probability - (1.0 - win_probability) / win_loss_ratio
        return max(0.0, min(float(raw_fraction), self.cap))
