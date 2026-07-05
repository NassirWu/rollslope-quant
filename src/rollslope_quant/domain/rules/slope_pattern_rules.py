from rollslope_quant.domain.entities.slope_result import SlopeResult


def is_v_reversal(
    result: SlopeResult,
    strong_down: float = -1.0,
    flat_abs: float = 0.5,
    strong_up: float = 1.0,
) -> bool:
    """
    V 轉買入型態。

    Rule:
        t1 < -1.0        急跌
        -0.5 <= t2 <= 0.5 打底盤整
        t3 > 1.0         多頭確認
    """
    return result.t1 < strong_down and abs(result.t2) <= flat_abs and result.t3 > strong_up


def is_inverted_v_top(
    result: SlopeResult,
    strong_up: float = 1.0,
    flat_abs: float = 0.5,
    strong_down: float = -1.0,
) -> bool:
    """
    倒 V 頂賣出型態。

    Rule:
        t1 > 1.0          急漲
        -0.5 <= t2 <= 0.5 高檔橫盤
        t3 < -1.0         空頭確認
    """
    return result.t1 > strong_up and abs(result.t2) <= flat_abs and result.t3 < strong_down
