@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================================
echo RollSlope Quant MVP - Manual X/Y Runner
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

if not exist "scripts\export_rolling_slope_table.py" (
    echo 找不到 scripts\export_rolling_slope_table.py
    echo 這個檔案是專案的一部分，請確認專案是否完整。
    echo.
    pause
    exit /b 1
)

if not exist "templates\manual_xy_template.csv" (
    echo 找不到 templates\manual_xy_template.csv
    echo 這個檔案是專案的一部分，請確認專案是否完整。
    echo.
    pause
    exit /b 1
)

if not exist "data\raw" (
    mkdir "data\raw"
)

if not exist "reports" (
    mkdir "reports"
)

if not exist "data\raw\manual_xy_template.csv" (
    copy /y "templates\manual_xy_template.csv" "data\raw\manual_xy_template.csv" >nul
    echo 已建立手動輸入模板：data\raw\manual_xy_template.csv
    echo 請用 Excel 打開它，填好 x,y 後存檔，再重新雙擊 run_manual_xy.bat
    echo.
    pause
    exit /b 0
)

echo 正在計算 data\raw\manual_xy_template.csv ...
".venv\Scripts\python.exe" "scripts\export_rolling_slope_table.py" --input "data\raw\manual_xy_template.csv" --output "reports\manual_xy_result.csv" --x-col x --price-col y --window-size 6 --step-size 1 --min-r-squared 0.7
if errorlevel 1 (
    echo.
    echo Manual X/Y calculation failed.
    echo 請確認：
    echo   - CSV 欄位名稱必須是 x,y
    echo   - x 欄位必須是數字
    echo   - y 欄位必須是數字
    echo   - 至少需要 6 筆資料
    echo   - 不要有空白列
    echo   - 檔案不要被 Excel 鎖住
    echo.
    pause
    exit /b 1
)
echo.

echo ============================================================
echo Manual X/Y calculation completed successfully.
echo 請打開 reports\manual_xy_result.csv 查看：
echo   - t1 / t2 / t3
echo   - z1 / z2 / z3
echo   - breakpoint_1 / breakpoint_2
echo   - r_squared
echo   - is_valid
echo ============================================================
echo.

pause
endlocal
