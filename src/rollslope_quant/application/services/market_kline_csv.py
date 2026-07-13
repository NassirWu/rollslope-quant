from __future__ import annotations

import pandas as pd


def prepare_market_kline_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    驗證並整理市場 K 線 CSV（datetime, open, high, low, close, volume）。

    - close 欄位必填，不分大小寫辨識，標準化欄名為小寫 close，並轉成 numeric。
    - datetime 欄位選填，不分大小寫辨識，標準化欄名為小寫 datetime；若存在則依時間
      升冪排序（穩定排序）後重設列順序；若不存在則保留原始列順序。
    - open / high / low / volume 目前保留但不驗證、不使用。
    - 不產生任何交易訊號，僅整理資料供斜率模型使用。
    """
    column_lookup = {col.lower(): col for col in df.columns}

    close_col = column_lookup.get("close")
    if close_col is None:
        raise ValueError("找不到 close 欄位，請確認 CSV 是否包含 close 欄位。")

    result = df.rename(columns={close_col: "close"})

    result["close"] = pd.to_numeric(result["close"], errors="coerce")
    if result["close"].isna().any():
        raise ValueError("close 欄位含有空白或無法轉成數字的內容，請檢查資料。")
    if result["close"].nunique() == 1:
        raise ValueError("close 欄位數值全部相同，無法計算斜率，請確認資料是否正確。")

    datetime_col = column_lookup.get("datetime")
    if datetime_col is not None:
        result = result.rename(columns={datetime_col: "datetime"})
        result["datetime"] = pd.to_datetime(result["datetime"], errors="coerce")
        if result["datetime"].isna().any():
            raise ValueError("datetime 欄位有無法辨識的時間格式，請檢查資料。")
        result = result.sort_values("datetime", kind="stable").reset_index(drop=True)
    else:
        result = result.reset_index(drop=True)

    return result
