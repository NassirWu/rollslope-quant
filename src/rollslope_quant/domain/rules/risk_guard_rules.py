def should_force_no_trade_by_r2(r_squared: float, min_r_squared: float = 0.70) -> bool:
    """
    若分段線性模型 R² 過低，代表價格型態不符合趨勢結構，強制觀望。
    """
    return r_squared < min_r_squared


def is_extreme_slope_expansion(
    current_t3: float,
    previous_t3: float | None,
    multiplier: float = 2.0,
    epsilon: float = 1e-12,
) -> bool:
    """
    判斷 t3 是否出現極端放大。

    Rule:
        |t3_current| > multiplier * |t3_previous|

    用途：
        觸發 trailing stop 或調緊止損。
    """
    if previous_t3 is None:
        return False
    return abs(current_t3) > multiplier * max(abs(previous_t3), epsilon)
