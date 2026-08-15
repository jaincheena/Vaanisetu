@echo off
REM ============================================================
REM VaaniSetu — Start Server (Production Launcher)
REM ============================================================
setlocal enabledelayedexpansion
title VaaniSetu Server - BAIF AI Localization
color 0A

cd /d "%~dp0\.."

set PORT=8765

echo.
echo ============================================================
echo   🌱 Starting VaaniSetu Server (Port %PORT%)...
echo ============================================================
echo.

REM --- 1. Python Check ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM --- 2. Ensure directories exist ---
if not exist "C:\VaaniSetu" (
    mkdir "C:\VaaniSetu\models" 2>nul
    mkdir "C:\VaaniSetu\workspace" 2>nul
    mkdir "C:\VaaniSetu\outputs" 2>nul
    mkdir "C:\VaaniSetu\uploads" 2>nul
    mkdir "C:\VaaniSetu\logs" 2>nul
)

REM --- 3. Get LAN IP for WiFi sharing ---
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r "IPv4.*192\. IPv4.*10\. IPv4.*172\."') do (
    set LAN_IP=%%a
    set LAN_IP=!LAN_IP: =!
    goto :got_ip
)
set LAN_IP=localhost
:got_ip

echo   Local Address: http://localhost:%PORT%
echo   Office WiFi:   http://%LAN_IP%:%PORT%
echo.
echo   Opening browser at http://localhost:%PORT% ...
echo   (Press Ctrl+C to stop the server)
echo ============================================================
echo.

REM Open browser automatically in background
start "" python -c "import time, webbrowser; time.sleep(1.8); webbrowser.open('http://localhost:%PORT%')" 2>nul

REM Run uvicorn in foreground
python -m uvicorn backend.main:app --host 0.0.0.0 --port %PORT% --log-level info

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] Server stopped with code %errorlevel%.
    echo Check logs in C:\VaaniSetu\logs\vaanisetu.log
    pause
)
