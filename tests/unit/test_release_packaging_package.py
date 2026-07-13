from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PACKAGE_SCRIPT = PROJECT_ROOT / "scripts" / "package_release.ps1"
RELEASE_PACKAGING_GUIDE_MD = PROJECT_ROOT / "docs" / "release_packaging_guide.md"
RELEASE_NOTES_MD = PROJECT_ROOT / "docs" / "release_notes_v0.10.0.md"
WORD_GITKEEP = PROJECT_ROOT / "release_inputs" / "word" / ".gitkeep"
GITIGNORE = PROJECT_ROOT / ".gitignore"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]

PROTECTED_PATH_KEYWORDS = [
    ".git",
    "src",
    "tests",
    "docs",
    "templates",
    "scripts",
    "cloud",
    ".streamlit",
    "requirements.txt",
    "run_demo.bat",
    "run_manual_xy.bat",
    "run_mobile_web.bat",
    ".gitignore",
    "readme.md",
]


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_package_release_script_exists() -> None:
    assert PACKAGE_SCRIPT.exists()


def test_word_gitkeep_exists() -> None:
    assert WORD_GITKEEP.exists()


def test_release_packaging_guide_exists() -> None:
    assert RELEASE_PACKAGING_GUIDE_MD.exists()


def test_release_notes_exists() -> None:
    assert RELEASE_NOTES_MD.exists()


def test_gitignore_excludes_release_and_word_docx() -> None:
    text = GITIGNORE.read_text(encoding="utf-8")
    assert "release/" in text
    assert "release_inputs/word/*.docx" in text


def test_package_release_script_declares_required_parameters() -> None:
    text = PACKAGE_SCRIPT.read_text(encoding="utf-8")
    for required in ["$Version", "$SourceRef", "$BeginnerDocxPath", "$TechnicalDocxPath"]:
        assert required in text


def test_package_release_script_uses_git_archive() -> None:
    text = PACKAGE_SCRIPT.read_text(encoding="utf-8")
    assert "git archive" in text


def test_package_release_script_uses_compress_archive() -> None:
    text = PACKAGE_SCRIPT.read_text(encoding="utf-8")
    assert "Compress-Archive" in text


def test_package_release_script_errors_when_word_docs_missing() -> None:
    text = PACKAGE_SCRIPT.read_text(encoding="utf-8")
    assert "Write-Error" in text
    assert "exit 1" in text
    assert "Test-Path $BeginnerDocxPath" in text
    assert "Test-Path $TechnicalDocxPath" in text


def test_package_release_script_does_not_delete_protected_paths() -> None:
    text = PACKAGE_SCRIPT.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Remove-Item" not in line:
            continue
        lowered = line.lower()
        for keyword in PROTECTED_PATH_KEYWORDS:
            assert keyword not in lowered, f"Dangerous Remove-Item line references protected path '{keyword}': {line}"


def test_release_notes_mentions_version_and_known_limitations() -> None:
    text = RELEASE_NOTES_MD.read_text(encoding="utf-8")
    assert "v0.10.0" in text
    assert "997c1103dbac2da2e65d9aef259401c2d9ebd0fb" in text
    assert "rollslope-quant-mvp.streamlit.app" in text
    for term in ["券商", "下單", "金鑰", "買賣"]:
        assert term in text


def test_release_packaging_guide_mentions_word_input_folder() -> None:
    text = RELEASE_PACKAGING_GUIDE_MD.read_text(encoding="utf-8")
    assert "release_inputs/word" in text


def test_package_release_script_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(PACKAGE_SCRIPT)


def test_release_packaging_guide_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(RELEASE_PACKAGING_GUIDE_MD)


def test_release_notes_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(RELEASE_NOTES_MD)
