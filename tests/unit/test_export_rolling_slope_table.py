from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "export_rolling_slope_table.py"

EXPECTED_COLUMNS = (
    "window_start",
    "window_end",
    "x_start",
    "x_end",
    "t1",
    "t2",
    "t3",
    "z1",
    "z2",
    "z3",
    "breakpoint_1",
    "breakpoint_2",
    "r_squared",
    "model_name",
    "error",
)


def _make_sample_csv(tmp_path: Path, n: int = 40, with_time_index: bool = False) -> Path:
    rng = np.random.default_rng(3)
    x = np.arange(n, dtype=float)
    close = 100.0 + 2.0 * x + rng.normal(0, 0.3, n)

    data = {"close": close}
    if with_time_index:
        data["time_index"] = 1000.0 + x * 10.0

    df = pd.DataFrame(data)
    csv_path = tmp_path / "sample.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )


def test_script_executes_successfully_and_creates_parent_dir(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "out" / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--price-col",
            "close",
            "--window-size",
            "10",
            "--step-size",
            "5",
        ]
    )

    assert result.returncode == 0
    assert output_csv.exists()
    assert output_csv.stat().st_size > 0


def test_output_contains_expected_columns(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--window-size",
            "10",
            "--step-size",
            "5",
        ]
    )

    assert result.returncode == 0
    df_out = pd.read_csv(output_csv)
    for col in EXPECTED_COLUMNS:
        assert col in df_out.columns


def test_min_r_squared_adds_is_valid_column(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--window-size",
            "10",
            "--step-size",
            "5",
            "--min-r-squared",
            "0.5",
        ]
    )

    assert result.returncode == 0
    df_out = pd.read_csv(output_csv)
    assert "is_valid" in df_out.columns


def test_without_min_r_squared_no_is_valid_column(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--window-size",
            "10",
            "--step-size",
            "5",
        ]
    )

    assert result.returncode == 0
    df_out = pd.read_csv(output_csv)
    assert "is_valid" not in df_out.columns


def test_missing_price_col_returns_nonzero(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--price-col",
            "not_exist",
            "--window-size",
            "10",
        ]
    )

    assert result.returncode != 0


def test_missing_input_file_returns_nonzero(tmp_path: Path) -> None:
    missing_input = tmp_path / "does_not_exist.csv"
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(missing_input),
            "--output",
            str(output_csv),
            "--window-size",
            "10",
        ]
    )

    assert result.returncode != 0


def test_stdout_contains_required_fields(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--window-size",
            "10",
            "--step-size",
            "5",
        ]
    )

    assert result.returncode == 0
    stdout = result.stdout
    assert "input_path" in stdout
    assert "output_path" in stdout
    assert "rows" in stdout
    assert "window_size" in stdout
    assert "step_size" in stdout


def test_x_col_used_instead_of_dataframe_index(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path, with_time_index=True)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--x-col",
            "time_index",
            "--window-size",
            "10",
            "--step-size",
            "5",
        ]
    )

    assert result.returncode == 0

    df_in = pd.read_csv(input_csv)
    df_out = pd.read_csv(output_csv)

    for _, row in df_out.iterrows():
        expected_x_start = df_in["time_index"].iloc[int(row["window_start"])]
        expected_x_end = df_in["time_index"].iloc[int(row["window_end"])]
        assert row["x_start"] == pytest.approx(expected_x_start)
        assert row["x_end"] == pytest.approx(expected_x_end)
        # DataFrame index (0..n-1) must not have been used instead of time_index
        assert row["x_start"] != row["window_start"]


def test_x_col_not_found_returns_nonzero(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--x-col",
            "not_exist",
            "--window-size",
            "10",
        ]
    )

    assert result.returncode != 0


def test_script_source_does_not_reference_broker_shioaji_or_plutus() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8").lower()

    assert "shioaji" not in source
    assert "broker" not in source
    assert "plutus" not in source


def test_output_csv_has_no_trade_signal_columns(tmp_path: Path) -> None:
    input_csv = _make_sample_csv(tmp_path)
    output_csv = tmp_path / "rolling_slope_table.csv"

    result = _run(
        [
            "--input",
            str(input_csv),
            "--output",
            str(output_csv),
            "--window-size",
            "10",
            "--step-size",
            "5",
        ]
    )

    assert result.returncode == 0
    df_out = pd.read_csv(output_csv)
    forbidden = {"signal", "action", "buy", "sell"}
    assert forbidden.isdisjoint(set(df_out.columns))
