from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import pandas as pd  # noqa: E402

from rollslope_quant.application.services.rolling_slope_table import (  # noqa: E402
    calculate_rolling_slope_table_from_dataframe,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export rolling slope table (z1/z2/z3) from CSV price data to CSV. "
            "Does not produce trading signals."
        )
    )
    parser.add_argument("--input", required=True, type=Path, help="Input CSV file path")
    parser.add_argument("--output", required=True, type=Path, help="Output CSV file path")
    parser.add_argument("--price-col", default="close", help="Price column name (default: close)")
    parser.add_argument(
        "--x-col",
        default=None,
        help="X-axis column name; defaults to using the DataFrame index",
    )
    parser.add_argument("--window-size", required=True, type=int, help="Rolling window size (>= 6)")
    parser.add_argument("--step-size", type=int, default=1, help="Rolling step size (default: 1)")
    parser.add_argument(
        "--min-r-squared",
        type=float,
        default=None,
        help="Optional minimum R-squared threshold; adds an is_valid column",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()

    if not args.input.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(args.input)
    except Exception as exc:  # noqa: BLE001 - surface any CSV parsing failure as a clean CLI error
        print(f"Error: failed to read input CSV {args.input}: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        table = calculate_rolling_slope_table_from_dataframe(
            df,
            price_col=args.price_col,
            x_col=args.x_col,
            window_size=args.window_size,
            step_size=args.step_size,
            min_r_squared=args.min_r_squared,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)

    print("=" * 72)
    print("RollSlope Quant / Rolling Slope Table CSV Export")
    print("=" * 72)
    print(f"input_path     : {args.input}")
    print(f"output_path    : {args.output}")
    print(f"rows           : {len(table)}")
    print(f"window_size    : {args.window_size}")
    print(f"step_size      : {args.step_size}")
    print(f"price_col      : {args.price_col}")
    print(f"x_col          : {args.x_col}")
    print(f"min_r_squared  : {args.min_r_squared}")
    print("=" * 72)


if __name__ == "__main__":
    main()
