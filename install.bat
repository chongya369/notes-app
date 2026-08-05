@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Notes App - Install Dependencies
echo ========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo Python version: !PYTHON_VERSION!
echo.

echo [1/2] Installing backend dependencies...
cd /d "%~dp0backend"
if exist requirements.txt (
    echo Running: python -m pip install --prefer-binary -r requirements.txt
    python -m pip install --prefer-binary -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [WARNING] Failed with --prefer-binary, trying without...
        python -m pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo.
            echo [ERROR] Backend dependencies installation failed.
            echo.
            echo Possible solutions:
            echo   1. Update pip: python -m pip install --upgrade pip
            echo   2. Install Rust toolchain: https://www.rust-lang.org/tools/install
            echo   3. Install Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
            echo.
            pause
            exit /b 1
        )
    )
)
cd /d "%~dp0"

echo.
echo [2/2] Installing desktop client dependencies...
cd /d "%~dp0frontend_desktop"
if exist requirements.txt (
    echo Running: python -m pip install --prefer-binary -r requirements.txt
    python -m pip install --prefer-binary -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [WARNING] Failed with --prefer-binary, trying without...
        python -m pip install -r requirements.txt
        if %errorlevel% neq 0 (
            echo.
            echo [ERROR] Desktop client dependencies installation failed.
            pause
            exit /b 1
        )
    )
)
cd /d "%~dp0"

echo.
echo ========================================
echo Installation complete!
echo ========================================
echo.
echo Usage:
echo   Backend only:          python backend\main.py
echo   Backend + Web UI:      python backend\main.py --web
echo   Desktop client:        python frontend_desktop\main.py
echo.
echo Quick start (bat files):
echo   start_backend.bat      - Start backend API
echo   start_backend_web.bat  - Start backend + web frontend
echo   start_desktop.bat      - Start desktop client
echo.
pause
