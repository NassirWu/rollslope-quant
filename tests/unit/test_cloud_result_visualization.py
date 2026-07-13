from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MOBILE_APP_PY = PROJECT_ROOT / "src" / "rollslope_quant" / "interfaces" / "web" / "mobile_app.py"
CLOUD_REQUIREMENTS_TXT = PROJECT_ROOT / "cloud" / "requirements.txt"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]

EXPECTED_CLOUD_REQUIREMENTS = (
    "streamlit>=1.30\n"
    "pandas>=2.0\n"
    "numpy>=1.24\n"
    "pwlf>=2.2.1\n"
    "scipy>=1.10\n"
    "matplotlib>=3.8\n"
)


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_mobile_app_imports_calculate_dynamic_slopes() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "calculate_dynamic_slopes" in text


def test_mobile_app_imports_plot_slope_fitting() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "plot_slope_fitting" in text


def test_mobile_app_uses_st_pyplot() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "st.pyplot" in text


def test_mobile_app_has_render_chart_function() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "def _render_chart(" in text


def test_all_three_modes_call_render_chart() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")

    def _body(func_name: str, next_func_name: str) -> str:
        start = text.index(f"def {func_name}(")
        end = text.index(f"def {next_func_name}(")
        return text[start:end]

    demo_body = _body("_render_demo_mode", "_render_manual_mode")
    manual_body = _body("_render_manual_mode", "_render_csv_mode")
    csv_body = _body("_render_csv_mode", "_render_usage_guide")

    assert "_render_chart(" in demo_body
    assert "_render_chart(" in manual_body
    assert "_render_chart(" in csv_body


def test_validate_inputs_and_render_result_still_exist() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "def _validate_inputs(" in text
    assert "def _render_result(table: pd.DataFrame) -> None:" in text


def test_cloud_requirements_txt_matches_expected_six_lines() -> None:
    text = CLOUD_REQUIREMENTS_TXT.read_text(encoding="utf-8")
    assert text == EXPECTED_CLOUD_REQUIREMENTS


def test_mobile_app_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(MOBILE_APP_PY)
