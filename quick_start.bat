@echo off
REM ============================================================================
REM 🌱 VaaniSetu — 1-Click Launch & Auto-Installer
REM Double-click this file to set up and start VaaniSetu instantly!
REM ============================================================================
setlocal enabledelayedexpansion
title VaaniSetu - AI Translation Platform for BAIF
color 0A

REM Ensure working directory is the folder where this batch file lives
cd /d "%~dp0"

echo.
echo ============================================================================
echo   🌱 VaaniSetu — 100%% Offline AI Translation Platform
echo   Bharatiya Agro Industries Foundation (BAIF)
echo ============================================================================
echo.

REM --- 1. Python Environment Check ---
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.10+ from https://www.python.org and check "Add to PATH".
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo       Found: %%v

REM --- 2. Base Directory Initialization ---
set BASE_DIR=C:\VaaniSetu
echo [2/4] Initializing local directories at %BASE_DIR%...
mkdir "%BASE_DIR%" 2>nul
mkdir "%BASE_DIR%\models" 2>nul
mkdir "%BASE_DIR%\workspace" 2>nul
mkdir "%BASE_DIR%\outputs" 2>nul
mkdir "%BASE_DIR%\uploads" 2>nul
mkdir "%BASE_DIR%\logs" 2>nul
echo       Directories verified.

REM --- 3. Dependency Verification ---
echo [3/4] Verifying core packages...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    echo       Installing required dependencies from requirements.txt...
    echo       (This may take a few minutes on first run)
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo [ERROR] Dependency installation encountered an issue.
        echo Check internet connection or review requirements.txt.
        echo.
        pause
        exit /b 1
    )
)
echo       Core packages ready.

REM --- 4. Frontend Web UI Verification ---
if not exist "frontend\dist\index.html" (
    echo       Building React web interface (one-time step)...
    cd frontend
    call npm install --silent
    call npm run build
    cd ..
    echo       Web interface compiled.
)

REM --- 5. Start Browser in Background ---
echo [4/4] Starting server on port 8765...
echo ============================================================================
echo   SERVER STATUS: ONLINE
echo   Local Web Access: http://localhost:8765
echo   Office WiFi LAN:  http://0.0.0.0:8765
echo.
echo   Press Ctrl+C in this terminal window to stop the server.
echo ============================================================================
echo.

REM Automatically open default browser when server starts
start "" python -c "import time, webbrowser; time.sleep(1.8); webbrowser.open('http://localhost:8765')" 2>nul

REM Start the server in foreground so logs are visible
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 --log-level info

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ============================================================================
    echo [ERROR] The server exited with error code %errorlevel%.
    echo Check logs in C:\VaaniSetu\logs\vaanisetu.log or run scripts\health_check.bat
    echo ============================================================================
    echo.
    pause
)
