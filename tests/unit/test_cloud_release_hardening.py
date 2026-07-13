from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

VERSION_PY = PROJECT_ROOT / "src" / "rollslope_quant" / "interfaces" / "web" / "version.py"
MOBILE_APP_PY = PROJECT_ROOT / "src" / "rollslope_quant" / "interfaces" / "web" / "mobile_app.py"
RELEASE_UPDATE_GUIDE_MD = PROJECT_ROOT / "docs" / "release_update_guide.md"
CLOUD_RELEASE_CHECKLIST_MD = PROJECT_ROOT / "docs" / "cloud_release_checklist.md"
CLOUD_REQUIREMENTS_TXT = PROJECT_ROOT / "cloud" / "requirements.txt"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]

EXPECTED_CLOUD_REQUIREMENTS = (
    "streamlit>=1.30\n"
    "pandas>=2.0\n"
    "numpy>=1.24\n"
    "pwlf>=2.2.1\n"
    "scipy>=1.10\n"
)


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_version_py_exists() -> None:
    assert VERSION_PY.exists()


def test_version_py_has_valid_version_string() -> None:
    text = VERSION_PY.read_text(encoding="utf-8")
    match = re.search(r'CLOUD_APP_VERSION\s*=\s*"(v\d+\.\d+\.\d+)"', text)
    assert match is not None, "CLOUD_APP_VERSION must be defined as a v<major>.<minor>.<patch> string"


def test_version_py_does_not_import_streamlit_or_git_or_env() -> None:
    text = VERSION_PY.read_text(encoding="utf-8").lower()
    assert "streamlit" not in text
    assert "subprocess" not in text
    assert "git" not in text
    assert "os.environ" not in text
    assert "getenv" not in text


def test_mobile_app_imports_cloud_app_version() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "from rollslope_quant.interfaces.web.version import CLOUD_APP_VERSION" in text


def test_mobile_app_displays_version() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "st.caption" in text
    assert "CLOUD_APP_VERSION" in text


def test_mobile_app_has_usage_and_result_expanders() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    assert "st.expander" in text
    assert "使用說明" in text
    assert "結果解讀" in text


def test_mobile_app_does_not_modify_core_render_or_validation_functions() -> None:
    text = MOBILE_APP_PY.read_text(encoding="utf-8")
    for required_def in [
        "def _validate_inputs(",
        "def _render_demo_mode() -> None:",
        "def _render_manual_mode() -> None:",
        "def _render_csv_mode() -> None:",
        "def _render_result(table: pd.DataFrame) -> None:",
    ]:
        assert required_def in text


def test_release_update_guide_exists() -> None:
    assert RELEASE_UPDATE_GUIDE_MD.exists()


def test_cloud_release_checklist_exists() -> None:
    assert CLOUD_RELEASE_CHECKLIST_MD.exists()


def test_release_update_guide_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(RELEASE_UPDATE_GUIDE_MD)


def test_cloud_release_checklist_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(CLOUD_RELEASE_CHECKLIST_MD)


def test_mobile_app_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(MOBILE_APP_PY)


def test_release_update_guide_describes_update_flow() -> None:
    text = RELEASE_UPDATE_GUIDE_MD.read_text(encoding="utf-8")
    for required in ["版本號", "pytest", "commit", "push", "Streamlit Cloud"]:
        assert required in text
    assert "Secrets" in text


def test_cloud_requirements_txt_unchanged() -> None:
    text = CLOUD_REQUIREMENTS_TXT.read_text(encoding="utf-8")
    assert text == EXPECTED_CLOUD_REQUIREMENTS
