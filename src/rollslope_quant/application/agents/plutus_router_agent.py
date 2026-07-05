from __future__ import annotations

from dataclasses import dataclass

from rollslope_quant.application.dto.decision_context_dto import DecisionContextDTO
from rollslope_quant.domain.entities.trade_signal import TradeSignal
from rollslope_quant.domain.enums.risk_level import RiskLevel
from rollslope_quant.domain.enums.trade_action import TradeAction
from rollslope_quant.domain.rules.circuit_breaker_rules import (
    should_trigger_drawdown_breaker,
    should_trigger_var_guard,
)
from rollslope_quant.domain.rules.risk_guard_rules import (
    is_extreme_slope_expansion,
    should_force_no_trade_by_r2,
)
from rollslope_quant.domain.rules.slope_pattern_rules import (
    is_inverted_v_top,
    is_v_reversal,
)
from rollslope_quant.infrastructure.risk.kelly_sizing_engine import KellySizingEngine


@dataclass(slots=True)
class RollSlopeRouterAgent:
    """
    Plutus：RollSlope Quant 的 AI 輔助決策路由器。

    職責：
        1. 讀取 Model Layer 的斜率結果：t1, t2, t3, breakpoints, R²。
        2. 讀取 Risk Layer 的 VaR、Drawdown、previous_t3。
        3. 根據狀態機將任務路由至 DataAgent / TraderAgent / RiskAgent。
        4. 輸出 TradeSignal。

    核心策略：
        V 轉買入：
            t1 < -1.0 and -0.5 <= t2 <= 0.5 and t3 > 1.0

        倒 V 頂賣出：
            t1 > 1.0 and -0.5 <= t2 <= 0.5 and t3 < -1.0

        隨機洗盤過濾：
            R² < 0.70 -> NO_TRADE

        黑天鵝風控：
            drawdown >= max_drawdown -> CIRCUIT_BREAKER
            VaR_95 >= max_var_95 -> NO_TRADE

        極端行情保護：
            |t3_current| > 2 * |t3_previous| -> tighten trailing stop
    """

    min_r_squared: float = 0.70
    extreme_slope_multiplier: float = 2.0

    def decide(self, context: DecisionContextDTO) -> TradeSignal:
        result = context.slope_result

        trailing_stop_required = is_extreme_slope_expansion(
            current_t3=result.t3,
            previous_t3=context.previous_t3,
            multiplier=self.extreme_slope_multiplier,
        )

        base_metadata = {
            "t1": result.t1,
            "t2": result.t2,
            "t3": result.t3,
            "breakpoints": result.breakpoints,
            "r_squared": result.r_squared,
            "model_name": result.model_name,
            "drawdown": context.account_state.drawdown,
            "var_95": context.var_95,
            "trailing_stop_required": trailing_stop_required,
            "market_regime": context.market_regime.value,
        }

        if context.connection_lost:
            return TradeSignal(
                action=TradeAction.RECONNECT_DATA,
                reason="行情連線中斷，路由至 DataAgent 重新連線。",
                confidence=1.0,
                risk_level=RiskLevel.HIGH,
                route_to="DataAgent.reconnect",
                metadata=base_metadata,
            )

        if should_trigger_drawdown_breaker(context.account_state.drawdown, context.max_drawdown):
            return TradeSignal(
                action=TradeAction.CIRCUIT_BREAKER,
                reason="帳戶回撤觸及上限，強制啟動斷路停損與減倉流程。",
                confidence=1.0,
                risk_level=RiskLevel.CRITICAL,
                route_to="RiskAgent.force_reduce_position",
                metadata=base_metadata,
            )

        if should_trigger_var_guard(context.var_95, context.max_var_95):
            return TradeSignal(
                action=TradeAction.NO_TRADE,
                reason="VaR_95 超過允許上限，禁止新增部位。",
                confidence=0.95,
                risk_level=RiskLevel.HIGH,
                route_to="RiskAgent.block_new_position",
                metadata=base_metadata,
            )

        if should_force_no_trade_by_r2(result.r_squared, self.min_r_squared):
            return TradeSignal(
                action=TradeAction.NO_TRADE,
                reason="模型 R² 低於 0.70，判定為隨機洗盤或低可信結構，強制觀望。",
                confidence=1.0 - max(0.0, result.r_squared),
                risk_level=RiskLevel.MEDIUM,
                route_to="QuantAgent.reject_low_quality_fit",
                metadata=base_metadata,
            )

        kelly = KellySizingEngine(cap=context.kelly_cap)
        fraction = kelly.calculate_fraction(
            win_probability=context.win_probability,
            win_loss_ratio=context.win_loss_ratio,
        )

        if is_v_reversal(result):
            return TradeSignal(
                action=TradeAction.BUY,
                reason="偵測到 V 轉結構：急跌 -> 盤整 -> 多頭斜率確認。",
                confidence=min(1.0, result.r_squared),
                position_fraction=fraction,
                risk_level=RiskLevel.MEDIUM if trailing_stop_required else RiskLevel.LOW,
                route_to="TraderAgent.open_long",
                metadata=base_metadata,
            )

        if is_inverted_v_top(result):
            return TradeSignal(
                action=TradeAction.SELL,
                reason="偵測到倒 V 頂結構：急漲 -> 高檔橫盤 -> 空頭斜率確認。",
                confidence=min(1.0, result.r_squared),
                position_fraction=fraction,
                risk_level=RiskLevel.MEDIUM if trailing_stop_required else RiskLevel.LOW,
                route_to="TraderAgent.open_short_or_reduce_long",
                metadata=base_metadata,
            )

        if trailing_stop_required and context.account_state.current_position_qty != 0:
            return TradeSignal(
                action=TradeAction.TIGHTEN_TRAILING_STOP,
                reason="t3 斜率絕對值較前次放大超過 2 倍，已有部位需調緊追蹤止損。",
                confidence=0.90,
                risk_level=RiskLevel.HIGH,
                route_to="RiskAgent.tighten_trailing_stop",
                metadata=base_metadata,
            )

        return TradeSignal(
            action=TradeAction.HOLD,
            reason="未偵測到可交易斜率型態，維持觀察。",
            confidence=0.50,
            risk_level=RiskLevel.LOW,
            route_to="PlutusRouterAgent.observe",
            metadata=base_metadata,
        )
