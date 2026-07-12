@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================================
echo RollSlope Quant MVP - Mobile Web Runner
echo ============================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Not found: .venv\Scripts\python.exe
    echo Please ask an engineer to run the following first:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip.exe install -r requirements.txt
    echo.
    pause
    exit /b 1
)

if not exist "scripts\run_mobile_web.py" (
    echo Not found: scripts\run_mobile_web.py
    echo This file is part of the project. Please check the project is complete.
    echo.
    pause
    exit /b 1
)

if not exist "src\rollslope_quant\interfaces\web\mobile_app.py" (
    echo Not found: src\rollslope_quant\interfaces\web\mobile_app.py
    echo This file is part of the project. Please check the project is complete.
    echo.
    pause
    exit /b 1
)

echo After it starts, look for the Network URL shown below.
echo Your phone and computer must be on the same Wi-Fi.
echo Open that Network URL in your phone browser to use it.
echo.

".venv\Scripts\python.exe" -m streamlit run scripts\run_mobile_web.py --server.address 0.0.0.0 --server.headless true --browser.gatherUsageStats false
if errorlevel 1 (
    echo.
    echo Startup failed. Please check the error message above.
    echo.
    pause
    exit /b 1
)

pause
endlocal
