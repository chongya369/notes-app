@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Notes App - Desktop Client
echo ========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

cd /d "%~dp0frontend_desktop"

python -c "import PyQt6, pystray, PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [INFO] Dependencies installed successfully.
    echo.
)

echo [INFO] Starting desktop client...
echo [INFO] The application will run in the system tray.
echo [INFO] Double-click the tray icon to show/hide notes.
echo.

python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Desktop client failed to start.
    pause
)

endlocal
