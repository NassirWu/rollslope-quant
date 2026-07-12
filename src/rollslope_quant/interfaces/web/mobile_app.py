from __future__ import annotations

import pandas as pd
import streamlit as st

from rollslope_quant.application.services.rolling_slope_table import (
    calculate_rolling_slope_table_from_dataframe,
)
from rollslope_quant.infrastructure.data.mock_market_data import (
    generate_v_reversal_market_data,
)

PAGE_TITLE = "RollSlope Quant MVP — Mobile Web Operator"

MODE_DEMO = "跑 Demo 範例資料"
MODE_MANUAL = "手動輸入 X/Y"
MODE_CSV = "上傳 CSV"

DEMO_WINDOW_SIZE = 30
DEMO_STEP_SIZE = 1
DEMO_MIN_R_SQUARED = 0.7

MANUAL_WINDOW_SIZE_DEFAULT = 6
MANUAL_STEP_SIZE_DEFAULT = 1
MANUAL_MIN_R_SQUARED_DEFAULT = 0.7

CSV_WINDOW_SIZE_DEFAULT = 30
CSV_STEP_SIZE_DEFAULT = 1
CSV_MIN_R_SQUARED_DEFAULT = 0.7

SUMMARY_FIELDS = [
    "t1",
    "t2",
    "t3",
    "z1",
    "z2",
    "z3",
    "breakpoint_1",
    "breakpoint_2",
    "r_squared",
    "is_valid",
]

DEFAULT_MANUAL_XY = pd.DataFrame(
    {
        "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0],
        "y": [100.0, 98.0, 95.0, 93.0, 94.0, 97.0, 101.0, 106.0, 110.0, 114.0, 118.0, 122.0],
    }
)

CSV_NO_X_COL_LABEL = "使用資料列順序"
CSV_NO_Y_COL_LABEL = "請選擇"


def _validate_inputs(
    df: pd.DataFrame,
    *,
    x_col: str | None,
    y_col: str | None,
    window_size: int,
    step_size: int,
) -> None:
    if df.empty or len(df.columns) == 0:
        raise ValueError("這份資料沒有任何欄位，請確認資料內容。")
    if not y_col:
        raise ValueError("請選擇 Y 欄位。")
    if x_col is not None and x_col == y_col:
        raise ValueError("X 欄位和 Y 欄位不能選一樣的。")
    if window_size < 6:
        raise ValueError("window_size 至少要 6。")
    if step_size < 1:
        raise ValueError("step_size 至少要 1。")
    if len(df) < window_size:
        raise ValueError(f"資料列數（{len(df)}）不夠，至少要有 {window_size} 列。")

    for col in [c for c in (x_col, y_col) if c is not None]:
        if df[col].isna().any():
            raise ValueError(f"「{col}」欄位裡有空白的內容，請檢查資料。")
        if pd.to_numeric(df[col], errors="coerce").isna().any():
            raise ValueError(f"「{col}」欄位裡有無法轉成數字的內容，請檢查資料。")


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")


def _render_warning_banner() -> None:
    st.info(
        "本工具只做斜率模型計算\n\n"
        "不會自動下單\n\n"
        "不會操作真實資金\n\n"
        "不需要金鑰\n\n"
        "不需要券商憑證"
    )


def _render_result(table: pd.DataFrame) -> None:
    st.dataframe(table)

    st.subheader("最後一列重點")
    last = table.iloc[-1]
    columns = st.columns(5)
    for i, field in enumerate(SUMMARY_FIELDS):
        columns[i % 5].metric(field, str(last.get(field)))

    st.download_button(
        "下載結果 CSV",
        data=_to_csv_bytes(table),
        file_name="rolling_slope_result.csv",
        mime="text/csv",
    )


def _render_demo_mode() -> None:
    st.write("使用內建範例資料：先急跌、再盤整、後急漲。")
    if st.button("計算", key="demo_calc"):
        df = generate_v_reversal_market_data(seed=7, n_each=30)
        _validate_inputs(
            df,
            x_col=None,
            y_col="close",
            window_size=DEMO_WINDOW_SIZE,
            step_size=DEMO_STEP_SIZE,
        )
        table = calculate_rolling_slope_table_from_dataframe(
            df,
            price_col="close",
            x_col=None,
            window_size=DEMO_WINDOW_SIZE,
            step_size=DEMO_STEP_SIZE,
            min_r_squared=DEMO_MIN_R_SQUARED,
        )
        _render_result(table)


def _render_manual_mode() -> None:
    st.write("可直接編輯下方表格的 X / Y 數值。")
    edited = st.data_editor(DEFAULT_MANUAL_XY, num_rows="dynamic", key="manual_xy_editor")
    window_size = st.number_input(
        "window_size", min_value=6, value=MANUAL_WINDOW_SIZE_DEFAULT, step=1, key="manual_window_size"
    )

    if st.button("計算", key="manual_calc"):
        df = edited.dropna(how="all").reset_index(drop=True)
        _validate_inputs(
            df,
            x_col="x",
            y_col="y",
            window_size=int(window_size),
            step_size=MANUAL_STEP_SIZE_DEFAULT,
        )
        table = calculate_rolling_slope_table_from_dataframe(
            df,
            price_col="y",
            x_col="x",
            window_size=int(window_size),
            step_size=MANUAL_STEP_SIZE_DEFAULT,
            min_r_squared=MANUAL_MIN_R_SQUARED_DEFAULT,
        )
        _render_result(table)


def _render_csv_mode() -> None:
    uploaded = st.file_uploader("上傳 CSV 檔案", type=["csv"])
    if uploaded is None:
        st.write("請選擇一個 CSV 檔案。")
        return

    df = pd.read_csv(uploaded)
    if df.empty or len(df.columns) == 0:
        st.error("這份 CSV 檔案沒有任何欄位，請確認檔案內容。")
        return

    columns = list(df.columns)
    y_col_choice = st.selectbox("Y 欄位（必選）", options=[CSV_NO_Y_COL_LABEL] + columns)
    x_col_choice = st.selectbox("X 欄位（可選）", options=[CSV_NO_X_COL_LABEL] + columns)

    window_size = st.number_input("window_size", min_value=6, value=CSV_WINDOW_SIZE_DEFAULT, step=1)
    step_size = st.number_input("step_size", min_value=1, value=CSV_STEP_SIZE_DEFAULT, step=1)
    min_r_squared = st.number_input(
        "min_r_squared", min_value=0.0, max_value=1.0, value=CSV_MIN_R_SQUARED_DEFAULT, step=0.05
    )

    if st.button("計算", key="csv_calc"):
        y_col = None if y_col_choice == CSV_NO_Y_COL_LABEL else y_col_choice
        x_col = None if x_col_choice == CSV_NO_X_COL_LABEL else x_col_choice
        _validate_inputs(
            df,
            x_col=x_col,
            y_col=y_col,
            window_size=int(window_size),
            step_size=int(step_size),
        )
        table = calculate_rolling_slope_table_from_dataframe(
            df,
            price_col=y_col,
            x_col=x_col,
            window_size=int(window_size),
            step_size=int(step_size),
            min_r_squared=float(min_r_squared),
        )
        _render_result(table)


def main() -> None:
    st.set_page_config(page_title=PAGE_TITLE)
    st.title(PAGE_TITLE)
    _render_warning_banner()

    mode = st.radio("選擇模式", [MODE_DEMO, MODE_MANUAL, MODE_CSV])

    try:
        if mode == MODE_DEMO:
            _render_demo_mode()
        elif mode == MODE_MANUAL:
            _render_manual_mode()
        else:
            _render_csv_mode()
    except Exception as exc:  # noqa: BLE001 - 任何計算錯誤都要用白話訊息顯示，不能讓頁面崩潰
        st.error(f"計算失敗：{exc}")


if __name__ == "__main__":
    main()
