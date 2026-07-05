# RollSlope Quant — 斜率模型 Quick Start

## 系統定位

- 只做數學斜率模型（分段線性擬合 t1/t2/t3、breakpoints、R²）
- 只做人工判斷輔助（圖表與 CSV 匯出，供人工複查）
- 不做自動交易
- 不接實盤下單

下單 / Shioaji / Plutus 相關流程請見 `README.md`，本文件不涵蓋。

## 完整流程

### A. 安裝依賴

```powershell
python -m venv .venv
.venv\Scripts\pip.exe install -r requirements.txt
```

### B. 跑 pytest

```powershell
.venv\Scripts\python.exe -m pytest -q
```

### C. 產生 V 轉圖

```powershell
.venv\Scripts\python.exe scripts\plot_v_reversal_demo.py
```

### D. 產生倒 V 圖

```powershell
.venv\Scripts\python.exe scripts\plot_inverted_v_demo.py
```

### E. 產生 sample CSV

```powershell
.venv\Scripts\python.exe scripts\generate_sample_v_reversal_csv.py
```

### F. 匯出 rolling_slope_table.csv

```powershell
.venv\Scripts\python.exe scripts\export_rolling_slope_table.py `
  --input data\raw\sample_v_reversal.csv `
  --output reports\rolling_slope_table.csv `
  --price-col close `
  --window-size 30 `
  --step-size 1 `
  --min-r-squared 0.7
```

## 輸出欄位說明

- `t1` / `t2` / `t3`：工程命名（早期 / 中期 / 近期斜率）
- `z1` / `z2` / `z3`：使用者手寫模型命名，`z1 = t1`、`z2 = t2`、`z3 = t3`
- `breakpoint_1` / `breakpoint_2`：兩個轉折點
- `r_squared`：擬合品質
- `is_valid`：僅在指定 `--min-r-squared` 時才會出現，代表是否通過門檻
- `error`：單一 window 擬合失敗時的錯誤訊息；失敗時其餘數值欄位為 NaN

## 注意事項

- 不要 commit `data/raw/*.csv`（已被 `.gitignore` 忽略）
- 不要 commit `reports/*.csv` / `reports/*.png`（已被 `.gitignore` 忽略）
- `.venv` 不要傳給別人（屬本機虛擬環境，不應納入版本控制或分享）
