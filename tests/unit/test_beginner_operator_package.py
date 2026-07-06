from __future__ import annotations

import csv
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RUN_DEMO_BAT = PROJECT_ROOT / "run_demo.bat"
RUN_MANUAL_XY_BAT = PROJECT_ROOT / "run_manual_xy.bat"
TEMPLATE_CSV = PROJECT_ROOT / "templates" / "manual_xy_template.csv"
GUIDE_MD = PROJECT_ROOT / "docs" / "beginner_operator_guide.md"

BLACKLIST_SUBSTRINGS = ["shioaji", "place_order", "api key"]
BLACKLIST_WORDS = ["buy", "sell"]


def _assert_no_blacklisted_content(path: Path) -> None:
    text = path.read_text(encoding="utf-8").lower()
    for term in BLACKLIST_SUBSTRINGS:
        assert term not in text, f"{path.name} must not contain '{term}'"
    for word in BLACKLIST_WORDS:
        assert not re.search(rf"\b{word}\b", text), f"{path.name} must not contain the English word '{word}'"


def test_run_demo_bat_exists() -> None:
    assert RUN_DEMO_BAT.exists()


def test_run_manual_xy_bat_exists() -> None:
    assert RUN_MANUAL_XY_BAT.exists()


def test_manual_xy_template_csv_exists() -> None:
    assert TEMPLATE_CSV.exists()


def test_beginner_operator_guide_exists() -> None:
    assert GUIDE_MD.exists()


def test_manual_xy_template_has_expected_columns() -> None:
    with TEMPLATE_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    header, data_rows = rows[0], rows[1:]
    assert header == ["x", "y"]
    assert len(data_rows) >= 6
    for row in data_rows:
        assert row, "manual_xy_template.csv must not contain blank rows"
        x_val, y_val = row
        float(x_val)
        float(y_val)


def test_run_demo_bat_contains_required_steps() -> None:
    text = RUN_DEMO_BAT.read_text(encoding="utf-8").lower()
    for required in [
        "generate_sample_v_reversal_csv.py",
        "export_rolling_slope_table.py",
        "plot_v_reversal_demo.py",
        "plot_inverted_v_demo.py",
        "pause",
    ]:
        assert required in text
    assert "errorlevel" in text or "if errorlevel" in text


def test_run_manual_xy_bat_contains_required_steps() -> None:
    text = RUN_MANUAL_XY_BAT.read_text(encoding="utf-8").lower()
    for required in [
        "manual_xy_template.csv",
        "--x-col x",
        "--price-col y",
        "--window-size 6",
        "pause",
    ]:
        assert required in text
    assert "errorlevel" in text or "if errorlevel" in text


def test_run_demo_bat_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(RUN_DEMO_BAT)


def test_run_manual_xy_bat_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(RUN_MANUAL_XY_BAT)


def test_beginner_operator_guide_has_no_blacklisted_content() -> None:
    _assert_no_blacklisted_content(GUIDE_MD)
