@echo off
REM ============================================================================
REM VaaniSetu - 1-Click Launch and Startup Wizard
REM ============================================================================
setlocal enabledelayedexpansion
title VaaniSetu - AI Translation Platform for BAIF
color 0A

cd /d "%~dp0"

echo.
echo ============================================================================
echo   VaaniSetu - 100%% Offline AI Translation Platform
echo   Bharatiya Agro Industries Foundation (BAIF)
echo ============================================================================
echo.

REM --- 1. Python Check ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo [!] Python is not installed or not in your system PATH.
    echo.
    echo Options:
    echo   [1] Automatically download Python 3.11 64-bit installer
    echo   [2] Open python.org in web browser
    echo   [3] Exit
    echo.
    set /p PY_OPT="Enter choice (1, 2, or 3) [Default: 1]: "
    if "!PY_OPT!"=="" set PY_OPT=1

    if "!PY_OPT!"=="1" (
        echo.
        echo Downloading Python 3.11.9 installer...
        powershell -command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', 'python_installer.exe')"
        if exist "python_installer.exe" (
            echo.
            echo ============================================================================
            echo [IMPORTANT] In the Python installer, MAKE SURE TO CHECK:
            echo             [X] Add python.exe to PATH (at the bottom)
            echo ============================================================================
            echo.
            start /wait python_installer.exe
            del python_installer.exe 2>nul
            echo.
            echo Python installation complete. Please re-run quick_start.bat!
            echo.
            pause
            exit /b 0
        ) else (
            echo Download failed. Opening browser...
            start https://www.python.org/downloads/
            pause
            exit /b 1
        )
    ) else if "!PY_OPT!"=="2" (
        start https://www.python.org/downloads/
        echo Please install Python (check Add to PATH) and re-run quick_start.bat.
        pause
        exit /b 0
    ) else (
        echo Setup cancelled.
        pause
        exit /b 0
    )
)

REM --- 2. Run Python Interactive Launcher ---
python launcher.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ============================================================================
    echo [ERROR] Process exited with code %errorlevel%.
    echo Check logs in C:\VaaniSetu\logs\vaanisetu.log
    echo ============================================================================
    echo.
    pause
)
