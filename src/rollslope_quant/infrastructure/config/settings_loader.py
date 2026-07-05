from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CONFIGS_DIR = PROJECT_ROOT / "configs"


# ---------------------------------------------------------------------------
# StrategyConfig
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SlopeThresholdsConfig:
    strong_up: float = 1.0
    strong_down: float = -1.0
    flat_abs: float = 0.5


@dataclass(frozen=True, slots=True)
class ModelConfig:
    n_segments: int = 3
    min_r_squared: float = 0.70


@dataclass(frozen=True, slots=True)
class RollingConfig:
    window_size: int = 90
    cycle_minutes: int = 60


@dataclass(frozen=True, slots=True)
class StrategyConfig:
    slope_thresholds: SlopeThresholdsConfig = field(default_factory=SlopeThresholdsConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    rolling: RollingConfig = field(default_factory=RollingConfig)


# ---------------------------------------------------------------------------
# RiskConfig
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RiskConfig:
    max_drawdown: float = 0.15
    max_var_95: float = 0.035
    kelly_cap: float = 0.25
    default_stop_loss_pct: float = 0.03
    extreme_slope_multiplier: float = 2.0


# ---------------------------------------------------------------------------
# BrokerConfig
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ShioajiSafetyConfig:
    allow_live_trading: bool = False
    max_lots_per_order: int = 1
    require_ca_for_live: bool = True


@dataclass(frozen=True, slots=True)
class ShioajiConfig:
    simulation: bool = True
    default_exchange: str = "TSE"
    fetch_contract: bool = True
    contracts_timeout: int = 30_000
    receive_window: int = 30_000
    safety: ShioajiSafetyConfig = field(default_factory=ShioajiSafetyConfig)


@dataclass(frozen=True, slots=True)
class StockOrderDefaultsConfig:
    order_kind: str = "MARKET"
    order_type: str = "IOC"
    order_lot: str = "Common"
    order_cond: str = "Cash"
    custom_field: str = "RSQ001"


@dataclass(frozen=True, slots=True)
class OrderDefaultsConfig:
    stock: StockOrderDefaultsConfig = field(default_factory=StockOrderDefaultsConfig)


@dataclass(frozen=True, slots=True)
class BrokerConfig:
    broker: str = "shioaji"
    shioaji: ShioajiConfig = field(default_factory=ShioajiConfig)
    order_defaults: OrderDefaultsConfig = field(default_factory=OrderDefaultsConfig)


# ---------------------------------------------------------------------------
# RollSlopeSettings
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RollSlopeSettings:
    strategy: StrategyConfig
    risk: RiskConfig
    broker: BrokerConfig


# ---------------------------------------------------------------------------
# YAML parsing helpers
# ---------------------------------------------------------------------------


def _load_yaml_dict(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {path}: {exc}") from exc
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(
            f"expected top-level mapping in {path}, got {type(raw).__name__}"
        )
    return raw


def _as_section(section: dict[str, Any], key: str, *, field_path: str) -> dict[str, Any]:
    value = section.get(key)
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_path} must be a mapping, got {type(value).__name__}")
    return value


def _as_float(section: dict[str, Any], key: str, default: float, *, field_path: str) -> float:
    if key not in section or section[key] is None:
        return default
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_path} must be a number, got {value!r}")
    return float(value)


def _as_int(section: dict[str, Any], key: str, default: int, *, field_path: str) -> int:
    if key not in section or section[key] is None:
        return default
    value = section[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_path} must be an integer, got {value!r}")
    return value


def _as_bool(section: dict[str, Any], key: str, default: bool, *, field_path: str) -> bool:
    if key not in section or section[key] is None:
        return default
    value = section[key]
    if not isinstance(value, bool):
        raise ValueError(f"{field_path} must be a boolean, got {value!r}")
    return value


def _as_str(section: dict[str, Any], key: str, default: str, *, field_path: str) -> str:
    if key not in section or section[key] is None:
        return default
    value = section[key]
    if not isinstance(value, str):
        raise ValueError(f"{field_path} must be a string, got {value!r}")
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# ---------------------------------------------------------------------------
# Section parsers
# ---------------------------------------------------------------------------


def _parse_strategy_config(data: dict[str, Any]) -> StrategyConfig:
    thresholds_raw = _as_section(data, "slope_thresholds", field_path="slope_thresholds")
    model_raw = _as_section(data, "model", field_path="model")
    rolling_raw = _as_section(data, "rolling", field_path="rolling")

    strong_up = _as_float(thresholds_raw, "strong_up", 1.0, field_path="slope_thresholds.strong_up")
    strong_down = _as_float(thresholds_raw, "strong_down", -1.0, field_path="slope_thresholds.strong_down")
    flat_abs = _as_float(thresholds_raw, "flat_abs", 0.5, field_path="slope_thresholds.flat_abs")

    n_segments = _as_int(model_raw, "n_segments", 3, field_path="model.n_segments")
    min_r_squared = _as_float(model_raw, "min_r_squared", 0.70, field_path="model.min_r_squared")
    _require(n_segments >= 1, f"model.n_segments must be >= 1, got {n_segments}")
    _require(
        0.0 <= min_r_squared <= 1.0,
        f"model.min_r_squared must be within [0, 1], got {min_r_squared}",
    )

    window_size = _as_int(rolling_raw, "window_size", 90, field_path="rolling.window_size")
    cycle_minutes = _as_int(rolling_raw, "cycle_minutes", 60, field_path="rolling.cycle_minutes")
    _require(window_size > 0, f"rolling.window_size must be > 0, got {window_size}")
    _require(cycle_minutes > 0, f"rolling.cycle_minutes must be > 0, got {cycle_minutes}")

    return StrategyConfig(
        slope_thresholds=SlopeThresholdsConfig(
            strong_up=strong_up, strong_down=strong_down, flat_abs=flat_abs
        ),
        model=ModelConfig(n_segments=n_segments, min_r_squared=min_r_squared),
        rolling=RollingConfig(window_size=window_size, cycle_minutes=cycle_minutes),
    )


def _parse_risk_config(data: dict[str, Any]) -> RiskConfig:
    risk_raw = _as_section(data, "risk", field_path="risk")

    max_drawdown = _as_float(risk_raw, "max_drawdown", 0.15, field_path="risk.max_drawdown")
    max_var_95 = _as_float(risk_raw, "max_var_95", 0.035, field_path="risk.max_var_95")
    kelly_cap = _as_float(risk_raw, "kelly_cap", 0.25, field_path="risk.kelly_cap")
    default_stop_loss_pct = _as_float(
        risk_raw, "default_stop_loss_pct", 0.03, field_path="risk.default_stop_loss_pct"
    )
    extreme_slope_multiplier = _as_float(
        risk_raw, "extreme_slope_multiplier", 2.0, field_path="risk.extreme_slope_multiplier"
    )

    _require(0.0 <= max_drawdown <= 1.0, f"risk.max_drawdown must be within [0, 1], got {max_drawdown}")
    _require(max_var_95 >= 0.0, f"risk.max_var_95 must be >= 0, got {max_var_95}")
    _require(0.0 <= kelly_cap <= 1.0, f"risk.kelly_cap must be within [0, 1], got {kelly_cap}")
    _require(
        0.0 <= default_stop_loss_pct <= 1.0,
        f"risk.default_stop_loss_pct must be within [0, 1], got {default_stop_loss_pct}",
    )
    _require(
        extreme_slope_multiplier > 0.0,
        f"risk.extreme_slope_multiplier must be > 0, got {extreme_slope_multiplier}",
    )

    return RiskConfig(
        max_drawdown=max_drawdown,
        max_var_95=max_var_95,
        kelly_cap=kelly_cap,
        default_stop_loss_pct=default_stop_loss_pct,
        extreme_slope_multiplier=extreme_slope_multiplier,
    )


def _parse_broker_config(data: dict[str, Any]) -> BrokerConfig:
    broker = _as_str(data, "broker", "shioaji", field_path="broker")

    shioaji_raw = _as_section(data, "shioaji", field_path="shioaji")
    safety_raw = _as_section(shioaji_raw, "safety", field_path="shioaji.safety")

    simulation = _as_bool(shioaji_raw, "simulation", True, field_path="shioaji.simulation")
    default_exchange = _as_str(
        shioaji_raw, "default_exchange", "TSE", field_path="shioaji.default_exchange"
    )
    fetch_contract = _as_bool(shioaji_raw, "fetch_contract", True, field_path="shioaji.fetch_contract")
    contracts_timeout = _as_int(
        shioaji_raw, "contracts_timeout", 30_000, field_path="shioaji.contracts_timeout"
    )
    receive_window = _as_int(
        shioaji_raw, "receive_window", 30_000, field_path="shioaji.receive_window"
    )
    _require(contracts_timeout > 0, f"shioaji.contracts_timeout must be > 0, got {contracts_timeout}")
    _require(receive_window > 0, f"shioaji.receive_window must be > 0, got {receive_window}")

    allow_live_trading = _as_bool(
        safety_raw, "allow_live_trading", False, field_path="shioaji.safety.allow_live_trading"
    )
    max_lots_per_order = _as_int(
        safety_raw, "max_lots_per_order", 1, field_path="shioaji.safety.max_lots_per_order"
    )
    require_ca_for_live = _as_bool(
        safety_raw, "require_ca_for_live", True, field_path="shioaji.safety.require_ca_for_live"
    )
    _require(
        max_lots_per_order >= 1,
        f"shioaji.safety.max_lots_per_order must be >= 1, got {max_lots_per_order}",
    )

    order_defaults_raw = _as_section(data, "order_defaults", field_path="order_defaults")
    stock_raw = _as_section(order_defaults_raw, "stock", field_path="order_defaults.stock")

    order_kind = _as_str(stock_raw, "order_kind", "MARKET", field_path="order_defaults.stock.order_kind")
    order_type = _as_str(stock_raw, "order_type", "IOC", field_path="order_defaults.stock.order_type")
    order_lot = _as_str(stock_raw, "order_lot", "Common", field_path="order_defaults.stock.order_lot")
    order_cond = _as_str(stock_raw, "order_cond", "Cash", field_path="order_defaults.stock.order_cond")
    custom_field = _as_str(
        stock_raw, "custom_field", "RSQ001", field_path="order_defaults.stock.custom_field"
    )

    return BrokerConfig(
        broker=broker,
        shioaji=ShioajiConfig(
            simulation=simulation,
            default_exchange=default_exchange,
            fetch_contract=fetch_contract,
            contracts_timeout=contracts_timeout,
            receive_window=receive_window,
            safety=ShioajiSafetyConfig(
                allow_live_trading=allow_live_trading,
                max_lots_per_order=max_lots_per_order,
                require_ca_for_live=require_ca_for_live,
            ),
        ),
        order_defaults=OrderDefaultsConfig(
            stock=StockOrderDefaultsConfig(
                order_kind=order_kind,
                order_type=order_type,
                order_lot=order_lot,
                order_cond=order_cond,
                custom_field=custom_field,
            )
        ),
    )


# ---------------------------------------------------------------------------
# Public loaders
# ---------------------------------------------------------------------------


def load_strategy_config(path: Path | str | None = None) -> StrategyConfig:
    resolved = Path(path) if path is not None else DEFAULT_CONFIGS_DIR / "strategy.yaml"
    return _parse_strategy_config(_load_yaml_dict(resolved))


def load_risk_config(path: Path | str | None = None) -> RiskConfig:
    resolved = Path(path) if path is not None else DEFAULT_CONFIGS_DIR / "risk.yaml"
    return _parse_risk_config(_load_yaml_dict(resolved))


def load_broker_config(path: Path | str | None = None) -> BrokerConfig:
    resolved = Path(path) if path is not None else DEFAULT_CONFIGS_DIR / "broker.yaml"
    return _parse_broker_config(_load_yaml_dict(resolved))


def load_all_settings(config_dir: Path | str = DEFAULT_CONFIGS_DIR) -> RollSlopeSettings:
    base = Path(config_dir)
    return RollSlopeSettings(
        strategy=load_strategy_config(base / "strategy.yaml"),
        risk=load_risk_config(base / "risk.yaml"),
        broker=load_broker_config(base / "broker.yaml"),
    )
