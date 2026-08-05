@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Notes App - Start Backend Server
echo ========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

cd /d "%~dp0backend"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Backend server failed to start.
    pause
)
endlocal
