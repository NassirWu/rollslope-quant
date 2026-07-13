from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CLOUD_APP_PY = PROJECT_ROOT / "cloud" / "app.py"
CLOUD_REQUIREMENTS_TXT = PROJECT_ROOT / "cloud" / "requirements.txt"
STREAMLIT_CONFIG_TOML = PROJECT_ROOT / ".streamlit" / "config.toml"
GUIDE_MD = PROJECT_ROOT / "docs" / "cloud_operator_guide.md"

RUN_DEMO_BAT = PROJECT_ROOT / "run_demo.bat"
RUN_MANUAL_XY_BAT = PROJECT_ROOT / "run_manual_xy.bat"
RUN_MOBILE_WEB_BAT = PROJECT_ROOT / "run_mobile_web.bat"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]

CONFIG_BLACKLIST_SUBSTRINGS = ["secrets", "token", "api_key", "api key"]


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_cloud_app_py_exists() -> None:
    assert CLOUD_APP_PY.exists()


def test_cloud_requirements_txt_exists() -> None:
    assert CLOUD_REQUIREMENTS_TXT.exists()


def test_streamlit_config_toml_exists() -> None:
    assert STREAMLIT_CONFIG_TOML.exists()


def test_cloud_operator_guide_exists() -> None:
    assert GUIDE_MD.exists()


def test_cloud_app_py_contains_required_steps() -> None:
    text = CLOUD_APP_PY.read_text(encoding="utf-8")
    for required in [
        "sys.path",
        "SRC_DIR",
        "from rollslope_quant.interfaces.web.mobile_app import main",
        'if __name__ == "__main__":',
        "main()",
    ]:
        assert required in text


def test_cloud_app_py_does_not_run_ui_on_import() -> None:
    text = CLOUD_APP_PY.read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in text
    lines = text.splitlines()
    guard_index = next(i for i, line in enumerate(lines) if line.startswith('if __name__ == "__main__":'))
    top_level_lines = [line for line in lines[:guard_index] if line and not line.startswith((" ", "\t"))]
    assert not any(line.startswith("main(") for line in top_level_lines)


def test_cloud_requirements_does_not_contain_shioaji_or_pytest_or_matplotlib() -> None:
    text = CLOUD_REQUIREMENTS_TXT.read_text(encoding="utf-8").lower()
    assert "shioaji" not in text
    assert "pytest" not in text
    assert "matplotlib" not in text


def test_cloud_requirements_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(CLOUD_REQUIREMENTS_TXT)


def test_cloud_requirements_contains_expected_dependencies() -> None:
    text = CLOUD_REQUIREMENTS_TXT.read_text(encoding="utf-8").lower()
    for required in ["streamlit", "pandas", "numpy", "pwlf", "scipy"]:
        assert required in text


def test_streamlit_config_has_no_secrets_or_server_address() -> None:
    text = STREAMLIT_CONFIG_TOML.read_text(encoding="utf-8").lower()
    for term in CONFIG_BLACKLIST_SUBSTRINGS:
        assert term not in text, f"config.toml must not contain '{term}'"
    assert "server.address" not in text
    assert "address" not in text
    assert "port" not in text


def test_streamlit_config_contains_required_settings() -> None:
    text = STREAMLIT_CONFIG_TOML.read_text(encoding="utf-8")
    assert "[browser]" in text
    assert "gatherUsageStats = false" in text
    assert "[server]" in text
    assert "headless = true" in text


def test_cloud_operator_guide_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(GUIDE_MD)


def test_cloud_operator_guide_mentions_main_file_path() -> None:
    text = GUIDE_MD.read_text(encoding="utf-8")
    assert "cloud/app.py" in text


def test_existing_local_bat_files_untouched() -> None:
    for bat_path in [RUN_DEMO_BAT, RUN_MANUAL_XY_BAT, RUN_MOBILE_WEB_BAT]:
        assert bat_path.exists()
        text = bat_path.read_text(encoding="utf-8").lower()
        assert "cloud" not in text
        assert "streamlit cloud" not in text
        assert "share.streamlit.io" not in text
