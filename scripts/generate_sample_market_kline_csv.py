from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rollslope_quant.infrastructure.data.mock_market_data import generate_v_reversal_market_data  # noqa: E402

OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "sample_market_kline.csv"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = generate_v_reversal_market_data(seed=7, n_each=30)
    df = df.rename(columns={"timestamp": "datetime"})
    df.to_csv(OUTPUT_PATH, index=False)

    print("=" * 72)
    print("RollSlope Quant / Sample Market K-line CSV Generator")
    print("=" * 72)
    print(f"output_path : {OUTPUT_PATH}")
    print(f"rows        : {len(df)}")
    print(f"columns     : {list(df.columns)}")
    print("=" * 72)


if __name__ == "__main__":
    main()
