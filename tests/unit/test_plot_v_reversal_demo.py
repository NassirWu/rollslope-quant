from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "plot_v_reversal_demo.py"
OUTPUT_PATH = PROJECT_ROOT / "reports" / "demo_v_reversal.png"


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


def test_script_creates_reports_directory(script_result: subprocess.CompletedProcess[str]) -> None:
    assert (PROJECT_ROOT / "reports").is_dir()


def test_script_outputs_png_file(script_result: subprocess.CompletedProcess[str]) -> None:
    assert OUTPUT_PATH.exists()


def test_output_file_size_greater_than_zero(script_result: subprocess.CompletedProcess[str]) -> None:
    assert OUTPUT_PATH.stat().st_size > 0


def test_stdout_contains_required_fields(script_result: subprocess.CompletedProcess[str]) -> None:
    stdout = script_result.stdout

    assert "t1" in stdout
    assert "t2" in stdout
    assert "t3" in stdout
    assert "breakpoints" in stdout
    assert "r_squared" in stdout
    assert "output_path" in stdout
    assert str(OUTPUT_PATH) in stdout


def test_script_source_does_not_reference_broker_or_shioaji() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8").lower()

    assert "shioaji" not in source
    assert "broker" not in source
