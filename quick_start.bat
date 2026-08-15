@echo off
REM ============================================================================
REM 🌱 VaaniSetu — 1-Click Launch & Auto-Installer
REM Double-click this file to set up and start VaaniSetu instantly!
REM ============================================================================
setlocal enabledelayedexpansion
title VaaniSetu - AI Translation Platform for BAIF
color 0A

echo.
echo ============================================================================
echo   🌱 VaaniSetu — 100%% Offline AI Translation Platform
echo   Bharatiya Agro Industries Foundation (BAIF)
echo ============================================================================
echo.

REM --- 1. Python Check ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.10+ from https://www.python.org and re-run.
    echo.
    pause
    exit /b 1
)

REM --- 2. Directory Initialization ---
set BASE_DIR=C:\VaaniSetu
if not exist "%BASE_DIR%" (
    echo [1/3] Initializing local directories at %BASE_DIR%...
    mkdir "%BASE_DIR%" 2>nul
    mkdir "%BASE_DIR%\models" 2>nul
    mkdir "%BASE_DIR%\workspace" 2>nul
    mkdir "%BASE_DIR%\outputs" 2>nul
    mkdir "%BASE_DIR%\uploads" 2>nul
    mkdir "%BASE_DIR%\logs" 2>nul
    echo       Done.
)

REM --- 3. Frontend Bundle Check ---
if not exist "frontend\dist\index.html" (
    echo [2/3] Building Web UI production bundle (one-time step)...
    cd frontend
    call npm install --silent
    call npm run build
    cd ..
    echo       Done.
)

REM --- 4. Launch Server & Open Browser ---
echo.
echo [3/3] Starting VaaniSetu Server on port 8765...
echo ============================================================================
echo   SERVER STATUS: ONLINE
echo   Local Web Access: http://localhost:8765
echo   Office WiFi LAN:  http://0.0.0.0:8765
echo.
echo   Press Ctrl+C in this terminal window to stop the server.
echo ============================================================================
echo.

REM Open browser in 2 seconds in background
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8765"

REM Start FastAPI uvicorn ASGI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 --log-level info
