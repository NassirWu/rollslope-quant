from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from rollslope_quant.infrastructure.config.settings_loader import (
    BrokerConfig,
    RiskConfig,
    RollSlopeSettings,
    StrategyConfig,
    load_all_settings,
    load_broker_config,
    load_risk_config,
    load_strategy_config,
)


def _write_yaml(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# StrategyConfig
# ---------------------------------------------------------------------------


def test_load_strategy_config_success(tmp_path: Path) -> None:
    path = _write_yaml(
        tmp_path / "strategy.yaml",
        """
slope_thresholds:
  strong_up: 1.2
  strong_down: -1.2
  flat_abs: 0.4
model:
  n_segments: 4
  min_r_squared: 0.8
rolling:
  window_size: 120
  cycle_minutes: 30
""",
    )

    config = load_strategy_config(path)

    assert config.slope_thresholds.strong_up == 1.2
    assert config.slope_thresholds.strong_down == -1.2
    assert config.slope_thresholds.flat_abs == 0.4
    assert config.model.n_segments == 4
    assert config.model.min_r_squared == 0.8
    assert config.rolling.window_size == 120
    assert config.rolling.cycle_minutes == 30


def test_load_strategy_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_strategy_config(tmp_path / "does_not_exist.yaml")


def test_load_strategy_config_empty_file_uses_defaults(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "strategy.yaml", "")

    config = load_strategy_config(path)

    assert config == StrategyConfig()


def test_load_strategy_config_missing_keys_use_defaults(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "strategy.yaml", "model:\n  n_segments: 5\n")

    config = load_strategy_config(path)

    assert config.model.n_segments == 5
    assert config.model.min_r_squared == 0.70
    assert config.slope_thresholds.strong_up == 1.0
    assert config.rolling.window_size == 90
    assert config.rolling.cycle_minutes == 60


def test_load_strategy_config_ignores_unknown_keys(tmp_path: Path) -> None:
    path = _write_yaml(
        tmp_path / "strategy.yaml",
        """
model:
  n_segments: 3
  min_r_squared: 0.7
  unknown_field: 999
totally_unknown_section:
  foo: bar
""",
    )

    config = load_strategy_config(path)

    assert config.model.n_segments == 3
    assert config.model.min_r_squared == 0.7


def test_load_strategy_config_malformed_yaml_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "strategy.yaml", "model: [unclosed")

    with pytest.raises(ValueError):
        load_strategy_config(path)


def test_load_strategy_config_type_error_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "strategy.yaml", 'model:\n  n_segments: "three"\n')

    with pytest.raises(ValueError):
        load_strategy_config(path)


def test_load_strategy_config_range_error_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "strategy.yaml", "model:\n  min_r_squared: 1.5\n")

    with pytest.raises(ValueError):
        load_strategy_config(path)


def test_load_strategy_config_non_positive_window_size_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "strategy.yaml", "rolling:\n  window_size: 0\n")

    with pytest.raises(ValueError):
        load_strategy_config(path)


def test_strategy_config_is_frozen() -> None:
    config = StrategyConfig()

    with pytest.raises(FrozenInstanceError):
        config.model = None  # type: ignore[misc]


# ---------------------------------------------------------------------------
# RiskConfig
# ---------------------------------------------------------------------------


def test_load_risk_config_success(tmp_path: Path) -> None:
    path = _write_yaml(
        tmp_path / "risk.yaml",
        """
risk:
  max_drawdown: 0.2
  max_var_95: 0.05
  kelly_cap: 0.3
  default_stop_loss_pct: 0.02
  extreme_slope_multiplier: 3.0
""",
    )

    config = load_risk_config(path)

    assert config.max_drawdown == 0.2
    assert config.max_var_95 == 0.05
    assert config.kelly_cap == 0.3
    assert config.default_stop_loss_pct == 0.02
    assert config.extreme_slope_multiplier == 3.0


def test_load_risk_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_risk_config(tmp_path / "does_not_exist.yaml")


def test_load_risk_config_missing_risk_key_uses_defaults(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "risk.yaml", "unrelated_key: 123\n")

    config = load_risk_config(path)

    assert config == RiskConfig()


def test_load_risk_config_type_error_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "risk.yaml", "risk:\n  max_drawdown: \"high\"\n")

    with pytest.raises(ValueError):
        load_risk_config(path)


def test_load_risk_config_range_error_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "risk.yaml", "risk:\n  kelly_cap: 1.5\n")

    with pytest.raises(ValueError):
        load_risk_config(path)


def test_load_risk_config_negative_var_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "risk.yaml", "risk:\n  max_var_95: -0.01\n")

    with pytest.raises(ValueError):
        load_risk_config(path)


def test_risk_config_is_frozen() -> None:
    config = RiskConfig()

    with pytest.raises(FrozenInstanceError):
        config.kelly_cap = 0.1  # type: ignore[misc]


# ---------------------------------------------------------------------------
# BrokerConfig
# ---------------------------------------------------------------------------


def test_load_broker_config_success(tmp_path: Path) -> None:
    path = _write_yaml(
        tmp_path / "broker.yaml",
        """
broker: shioaji
shioaji:
  simulation: false
  default_exchange: OTC
  fetch_contract: false
  contracts_timeout: 5000
  receive_window: 6000
  safety:
    allow_live_trading: true
    max_lots_per_order: 3
    require_ca_for_live: false
order_defaults:
  stock:
    order_kind: LIMIT
    order_type: ROD
    order_lot: Odd
    order_cond: MarginTrading
    custom_field: TEST001
""",
    )

    config = load_broker_config(path)

    assert config.broker == "shioaji"
    assert config.shioaji.simulation is False
    assert config.shioaji.default_exchange == "OTC"
    assert config.shioaji.fetch_contract is False
    assert config.shioaji.contracts_timeout == 5000
    assert config.shioaji.receive_window == 6000
    assert config.shioaji.safety.allow_live_trading is True
    assert config.shioaji.safety.max_lots_per_order == 3
    assert config.shioaji.safety.require_ca_for_live is False
    assert config.order_defaults.stock.order_kind == "LIMIT"
    assert config.order_defaults.stock.order_type == "ROD"
    assert config.order_defaults.stock.order_lot == "Odd"
    assert config.order_defaults.stock.order_cond == "MarginTrading"
    assert config.order_defaults.stock.custom_field == "TEST001"


def test_load_broker_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_broker_config(tmp_path / "does_not_exist.yaml")


def test_load_broker_config_empty_file_uses_defaults(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "broker.yaml", "")

    config = load_broker_config(path)

    assert config == BrokerConfig()


def test_load_broker_config_type_error_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "broker.yaml", "shioaji:\n  simulation: \"yes\"\n")

    with pytest.raises(ValueError):
        load_broker_config(path)


def test_load_broker_config_range_error_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(
        tmp_path / "broker.yaml", "shioaji:\n  safety:\n    max_lots_per_order: 0\n"
    )

    with pytest.raises(ValueError):
        load_broker_config(path)


def test_load_broker_config_non_positive_timeout_raises_value_error(tmp_path: Path) -> None:
    path = _write_yaml(tmp_path / "broker.yaml", "shioaji:\n  contracts_timeout: 0\n")

    with pytest.raises(ValueError):
        load_broker_config(path)


def test_broker_config_is_frozen() -> None:
    config = BrokerConfig()

    with pytest.raises(FrozenInstanceError):
        config.broker = "other"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# load_all_settings
# ---------------------------------------------------------------------------


def test_load_all_settings_returns_rollslope_settings(tmp_path: Path) -> None:
    _write_yaml(tmp_path / "strategy.yaml", "model:\n  n_segments: 3\n")
    _write_yaml(tmp_path / "risk.yaml", "risk:\n  kelly_cap: 0.2\n")
    _write_yaml(tmp_path / "broker.yaml", "broker: shioaji\n")

    settings = load_all_settings(tmp_path)

    assert isinstance(settings, RollSlopeSettings)
    assert isinstance(settings.strategy, StrategyConfig)
    assert isinstance(settings.risk, RiskConfig)
    assert isinstance(settings.broker, BrokerConfig)
    assert settings.strategy.model.n_segments == 3
    assert settings.risk.kelly_cap == 0.2
    assert settings.broker.broker == "shioaji"


def test_load_all_settings_reads_real_configs_directory() -> None:
    settings = load_all_settings()

    assert isinstance(settings, RollSlopeSettings)
    assert isinstance(settings.strategy, StrategyConfig)
    assert isinstance(settings.risk, RiskConfig)
    assert isinstance(settings.broker, BrokerConfig)
