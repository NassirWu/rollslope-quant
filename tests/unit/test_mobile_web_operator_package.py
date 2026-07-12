from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MOBILE_APP_PY = PROJECT_ROOT / "src" / "rollslope_quant" / "interfaces" / "web" / "mobile_app.py"
RUN_MOBILE_WEB_PY = PROJECT_ROOT / "scripts" / "run_mobile_web.py"
RUN_MOBILE_WEB_BAT = PROJECT_ROOT / "run_mobile_web.bat"
GUIDE_MD = PROJECT_ROOT / "docs" / "mobile_operator_guide.md"
REQUIREMENTS_TXT = PROJECT_ROOT / "requirements.txt"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_mobile_app_py_exists() -> None:
    assert MOBILE_APP_PY.exists()


def test_run_mobile_web_script_exists() -> None:
    assert RUN_MOBILE_WEB_PY.exists()


def test_run_mobile_web_bat_exists() -> None:
    assert RUN_MOBILE_WEB_BAT.exists()


def test_mobile_operator_guide_exists() -> None:
    assert GUIDE_MD.exists()


def test_requirements_contains_streamlit() -> None:
    text = REQUIREMENTS_TXT.read_text(encoding="utf-8").lower()
    assert "streamlit" in text


def test_mobile_app_contains_required_symbols() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    for required in [
        "streamlit",
        "st.file_uploader",
        "st.download_button",
        "calculate_rolling_slope_table_from_dataframe",
        "generate_v_reversal_market_data",
        "t1",
        "t2",
        "t3",
        "z1",
        "z2",
        "z3",
    ]:
        assert required in text


def test_mobile_app_does_not_run_ui_on_import() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in text
    lines = text.splitlines()
    guard_index = next(i for i, line in enumerate(lines) if line.startswith('if __name__ == "__main__":'))
    top_level_lines = [line for line in lines[:guard_index] if line and not line.startswith((" ", "\t"))]
    assert not any(line.startswith("main(") for line in top_level_lines)


def test_run_mobile_web_script_contains_required_steps() -> None:
    text = RUN_MOBILE_WEB_PY.read_text(encoding="utf-8")
    for required in [
        "PROJECT_ROOT",
        "sys.path",
        "from rollslope_quant.interfaces.web.mobile_app import main",
        'if __name__ == "__main__":',
        "main()",
    ]:
        assert required in text


def test_run_mobile_web_bat_contains_required_steps() -> None:
    text = RUN_MOBILE_WEB_BAT.read_text(encoding="utf-8").lower()
    for required in [
        "chcp 65001",
        'cd /d "%~dp0"',
        "python.exe",
        "streamlit",
        "--server.address 0.0.0.0",
        "pause",
    ]:
        assert required in text
    assert "errorlevel" in text or "if errorlevel" in text


def test_run_mobile_web_bat_has_no_caret_continuation() -> None:
    text = RUN_MOBILE_WEB_BAT.read_text(encoding="utf-8")
    assert "^" not in text


def test_run_mobile_web_bat_is_crlf() -> None:
    raw = RUN_MOBILE_WEB_BAT.read_bytes()
    lines_with_lf = raw.count(b"\n")
    lines_with_crlf = raw.count(b"\r\n")
    assert lines_with_lf > 0
    assert lines_with_lf == lines_with_crlf


def test_run_mobile_web_bat_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(RUN_MOBILE_WEB_BAT)


def test_mobile_app_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(MOBILE_APP_PY)


def test_mobile_operator_guide_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(GUIDE_MD)
