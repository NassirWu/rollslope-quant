from rollslope_quant.domain.entities.slope_result import SlopeResult
from rollslope_quant.domain.rules.slope_pattern_rules import is_inverted_v_top, is_v_reversal


def test_v_reversal_rule() -> None:
    result = SlopeResult(t1=-2.0, t2=0.1, t3=2.2, breakpoints=(30, 60), r_squared=0.95)
    assert is_v_reversal(result)


def test_inverted_v_rule() -> None:
    result = SlopeResult(t1=2.0, t2=0.1, t3=-2.2, breakpoints=(30, 60), r_squared=0.95)
    assert is_inverted_v_top(result)
