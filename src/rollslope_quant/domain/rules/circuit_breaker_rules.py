def should_trigger_drawdown_breaker(drawdown: float, max_drawdown: float) -> bool:
    """帳戶回撤達到上限時啟動斷路器。"""
    return drawdown >= max_drawdown


def should_trigger_var_guard(var_95: float, max_var_95: float) -> bool:
    """VaR 超過上限時禁止新倉。"""
    return var_95 >= max_var_95
