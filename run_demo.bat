@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================================
echo RollSlope Quant MVP - Demo Runner
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo 找不到 .venv\Scripts\python.exe
    echo 請先請工程人員執行安裝流程：
    echo   python -m venv .venv
    echo   .venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

if not exist "scripts\generate_sample_v_reversal_csv.py" (
    echo 找不到 scripts\generate_sample_v_reversal_csv.py
    echo 這個檔案是專案的一部分，請確認專案是否完整。
    echo.
    pause
    exit /b 1
)

if not exist "scripts\export_rolling_slope_table.py" (
    echo 找不到 scripts\export_rolling_slope_table.py
    echo 這個檔案是專案的一部分，請確認專案是否完整。
    echo.
    pause
    exit /b 1
)

if not exist "scripts\plot_v_reversal_demo.py" (
    echo 找不到 scripts\plot_v_reversal_demo.py
    echo 這個檔案是專案的一部分，請確認專案是否完整。
    echo.
    pause
    exit /b 1
)

if not exist "scripts\plot_inverted_v_demo.py" (
    echo 找不到 scripts\plot_inverted_v_demo.py
    echo 這個檔案是專案的一部分，請確認專案是否完整。
    echo.
    pause
    exit /b 1
)

if not exist "reports" (
    mkdir "reports"
)

echo [1/4] 產生 sample V-reversal CSV ...
".venv\Scripts\python.exe" "scripts\generate_sample_v_reversal_csv.py"
if errorlevel 1 (
    echo.
    echo 第 1 步失敗：產生 sample V-reversal CSV 時發生錯誤。
    echo.
    pause
    exit /b 1
)
echo.

echo [2/4] 匯出 rolling_slope_table.csv ...
".venv\Scripts\python.exe" "scripts\export_rolling_slope_table.py" --input "data\raw\sample_v_reversal.csv" --output "reports\rolling_slope_table.csv" --price-col close --window-size 30 --step-size 1 --min-r-squared 0.7
if errorlevel 1 (
    echo.
    echo 第 2 步失敗：匯出 rolling_slope_table.csv 時發生錯誤。
    echo.
    pause
    exit /b 1
)
echo.

echo [3/4] 產生 V 轉圖 ...
".venv\Scripts\python.exe" "scripts\plot_v_reversal_demo.py"
if errorlevel 1 (
    echo.
    echo 第 3 步失敗：產生 V 轉圖時發生錯誤。
    echo.
    pause
    exit /b 1
)
echo.

echo [4/4] 產生倒 V 圖 ...
".venv\Scripts\python.exe" "scripts\plot_inverted_v_demo.py"
if errorlevel 1 (
    echo.
    echo 第 4 步失敗：產生倒 V 圖時發生錯誤。
    echo.
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Demo completed successfully.
echo 請打開 reports 資料夾查看：
echo   - rolling_slope_table.csv
echo   - demo_v_reversal.png
echo   - demo_inverted_v.png
echo ============================================================
echo.

pause
endlocal
