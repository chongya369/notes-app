@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo Notes App - Start Backend + Web UI
echo ========================================
echo.
echo Web UI URL:   http://127.0.0.1:8000/web
echo API Docs URL: http://127.0.0.1:8000/docs
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python and add it to PATH.
    pause
    exit /b 1
)

cd /d "%~dp0backend"
python main.py --web
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Backend server failed to start.
    pause
)
endlocal
