from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True, slots=True)
class SlopeResult:
    """
    三段分段線性擬合結果。

    數學模型：
        給定時間序列點集 (x_i, y_i)，尋找 4 個節點
        b_0 < b_1 < b_2 < b_3，形成 3 個線性區間：

            y = a_j + t_j x,  j ∈ {1, 2, 3}

        其中：
            t_1 = 前期斜率
            t_2 = 中期斜率
            t_3 = 當前最新斜率

        轉折點：
            breakpoints = [b_1, b_2]

        擬合優度：
            R² = 1 - SS_res / SS_tot

    注意：
        t_3 是交易判斷中最重要的「當前趨勢動能」。
    """

    t1: float
    t2: float
    t3: float
    breakpoints: tuple[float, float]
    r_squared: float
    fitted_y: tuple[float, ...] = field(default_factory=tuple)
    model_name: str = "unknown"

    @property
    def slopes(self) -> tuple[float, float, float]:
        return (self.t1, self.t2, self.t3)

    @classmethod
    def from_sequence(
        cls,
        slopes: Sequence[float],
        breakpoints: Sequence[float],
        r_squared: float,
        fitted_y: Sequence[float] | None = None,
        model_name: str = "unknown",
    ) -> "SlopeResult":
        if len(slopes) != 3:
            raise ValueError(f"expected 3 slopes, got {len(slopes)}")
        if len(breakpoints) != 2:
            raise ValueError(f"expected 2 internal breakpoints, got {len(breakpoints)}")
        return cls(
            t1=float(slopes[0]),
            t2=float(slopes[1]),
            t3=float(slopes[2]),
            breakpoints=(float(breakpoints[0]), float(breakpoints[1])),
            r_squared=float(r_squared),
            fitted_y=tuple(float(v) for v in fitted_y) if fitted_y is not None else tuple(),
            model_name=model_name,
        )
