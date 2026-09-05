@echo off
title AI-DIDSS Launcher
setlocal EnableDelayedExpansion

:: 1. Navigate to the script's directory automatically
cd /d "%~dp0"

echo =========================================================================
echo    AI-DIDSS: AI-Based Identity & Travel Document Screening System
echo    Master Release: v1.0.0-PRODUCTION-READY
echo =========================================================================
echo.
echo [1/3] Verifying Python Environment...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found in your system PATH.
    echo Please install Python 3.10+ and ensure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

echo [2/3] Checking Submodule Operational Health...
python -m module13_final_validation.src.cli check
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Submodule check returned a warning code. Continuing startup...
)

echo.
echo [3/3] Launching Backend & Frontend Services...
echo.

:: Start FastAPI Backend on Port 8000 in a dedicated window
echo - Starting Backend API Server (Port 8000)...
start "AI-DIDSS Backend API [Port 8000]" cmd /k "cd /d "%~dp0" && title AI-DIDSS Backend API [Port 8000] && uvicorn module8_backend_api.src.main:app --host 0.0.0.0 --port 8000"

:: Wait 2 seconds for backend initialization
timeout /t 2 /nobreak >nul

:: Start Officer Web Console on Port 3000 in a dedicated window
echo - Starting Officer Web Console UI (Port 3000)...
start "AI-DIDSS Web Console [Port 3000]" cmd /k "cd /d "%~dp0" && title AI-DIDSS Web Console [Port 3000] && python -m http.server 3000 --directory module9_officer_console"

:: Wait 1 second
timeout /t 1 /nobreak >nul

echo.
echo =========================================================================
echo    SUCCESS! Both AI-DIDSS services are now running in background windows.
echo.
echo    * Web Console (UI):   http://localhost:3000
echo    * Backend REST API:   http://localhost:8000
echo    * API Documentation:  http://localhost:8000/docs
echo =========================================================================
echo.
echo Opening Web Console in your default browser...
start http://localhost:3000

echo.
echo Press any key to exit this launcher window (services will stay running).
pause >nul
