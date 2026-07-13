from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_sample_market_kline_csv.py"
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "sample_market_kline.csv"


@pytest.fixture(scope="module")
def script_result() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        check=True,
    )


def test_script_executes_successfully(script_result: subprocess.CompletedProcess[str]) -> None:
    assert script_result.returncode == 0


def test_script_creates_sample_csv(script_result: subprocess.CompletedProcess[str]) -> None:
    assert OUTPUT_PATH.exists()


def test_output_file_size_greater_than_zero(script_result: subprocess.CompletedProcess[str]) -> None:
    assert OUTPUT_PATH.stat().st_size > 0


def test_output_csv_contains_expected_columns(script_result: subprocess.CompletedProcess[str]) -> None:
    df = pd.read_csv(OUTPUT_PATH)
    for col in ["datetime", "open", "high", "low", "close", "volume"]:
        assert col in df.columns


def test_output_csv_has_rows(script_result: subprocess.CompletedProcess[str]) -> None:
    df = pd.read_csv(OUTPUT_PATH)
    assert len(df) > 0


def test_stdout_contains_required_fields(script_result: subprocess.CompletedProcess[str]) -> None:
    stdout = script_result.stdout

    assert "output_path" in stdout
    assert "rows" in stdout
    assert "columns" in stdout
    assert str(OUTPUT_PATH) in stdout


def test_script_source_does_not_reference_broker_shioaji_or_plutus() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8").lower()

    assert "shioaji" not in source
    assert "broker" not in source
    assert "plutus" not in source


def test_stdout_does_not_contain_trade_signal_keywords(script_result: subprocess.CompletedProcess[str]) -> None:
    stdout = script_result.stdout

    assert "BUY" not in stdout
    assert "SELL" not in stdout
