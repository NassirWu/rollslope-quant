from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from rollslope_quant.infrastructure.data.mock_market_data import generate_inverted_v_market_data  # noqa: E402
from rollslope_quant.infrastructure.model.pwlf_slope_model import calculate_dynamic_slopes  # noqa: E402
from rollslope_quant.interfaces.visualization.slope_visualizer import plot_from_dataframe  # noqa: E402

OUTPUT_PATH = PROJECT_ROOT / "reports" / "demo_inverted_v.png"


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = generate_inverted_v_market_data(seed=11, n_each=30)
    x = df.index.to_numpy(dtype=float)
    y = df["close"].to_numpy(dtype=float)

    slope_result = calculate_dynamic_slopes(x, y)

    plot_from_dataframe(
        df,
        slope_result=slope_result,
        show=False,
        save_path=str(OUTPUT_PATH),
    )

    print("=" * 72)
    print("RollSlope Quant / Dynamic Slope Engine - Inverted-V Visualization Demo")
    print("=" * 72)
    print(f"model_name  : {slope_result.model_name}")
    print(f"t1          : {slope_result.t1:.4f}")
    print(f"t2          : {slope_result.t2:.4f}")
    print(f"t3          : {slope_result.t3:.4f}")
    print(f"breakpoints : {tuple(round(v, 4) for v in slope_result.breakpoints)}")
    print(f"r_squared   : {slope_result.r_squared:.4f}")
    print(f"output_path : {OUTPUT_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()
