@echo off
cd /d "%~dp0"
title Rimal X
set RIMALX_API_PORT=8765

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Install it from python.org
    echo and tick "Add python.exe to PATH" during setup.
    pause
    exit /b
)

python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
    echo Your Python version is too old. Install Python 3.10 or newer.
    python --version
    pause
    exit /b
)

if not exist ".installed" (
    echo Installing libraries for the first time, please wait...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installation failed. Check the internet connection and try again.
        pause
        exit /b
    )
    echo done > .installed
)

echo Starting the API in a separate window...
start "Rimal X API" cmd /k python -m uvicorn api:app --port %RIMALX_API_PORT%

timeout /t 4 /nobreak >nul

echo Starting the app... keep this window open while you use it.
python -m streamlit run app.py
pause
