from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MOBILE_APP_PY = PROJECT_ROOT / "src" / "rollslope_quant" / "interfaces" / "web" / "mobile_app.py"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_mode_market_kline_constant_exists() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert 'MODE_MARKET_KLINE = "上傳市場 K 線 CSV"' in text


def test_render_market_kline_mode_function_exists() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "def _render_market_kline_mode() -> None:" in text


def test_main_radio_options_include_market_kline_mode() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert 'st.radio("選擇模式", [MODE_DEMO, MODE_MANUAL, MODE_CSV, MODE_MARKET_KLINE])' in text


def test_imports_prepare_market_kline_dataframe() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "from rollslope_quant.application.services.market_kline_csv import (" in text
    assert "prepare_market_kline_dataframe" in text


def test_market_kline_mode_calls_render_result_and_render_chart() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    start = text.index("def _render_market_kline_mode() -> None:")
    end = text.index("def _render_usage_guide() -> None:")
    body = text[start:end]
    assert "_render_result(" in body
    assert "_render_chart(" in body


def test_existing_csv_mode_function_still_exists() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "def _render_csv_mode() -> None:" in text


def test_existing_core_functions_still_exist() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    for required_def in [
        "def _validate_inputs(",
        "def _render_demo_mode() -> None:",
        "def _render_manual_mode() -> None:",
        "def _render_result(table: pd.DataFrame) -> None:",
        "def _render_chart(",
    ]:
        assert required_def in text


def test_mobile_app_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(MOBILE_APP_PY)
