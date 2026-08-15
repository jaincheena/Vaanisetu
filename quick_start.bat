@echo off
REM ============================================================================
REM 🌱 VaaniSetu — 1-Click Interactive Onboarding & Startup Wizard
REM Designed for fresh laptops, field officers, and new installations.
REM ============================================================================
setlocal enabledelayedexpansion
title VaaniSetu - AI Translation Platform for BAIF
color 0A

cd /d "%~dp0"

echo.
echo ============================================================================
echo   🌱 VaaniSetu — 100%% Offline AI Translation Platform
echo   Bharatiya Agro Industries Foundation (BAIF)
echo ============================================================================
echo   Welcome! This wizard will verify your PC and start the platform.
echo ============================================================================
echo.

:check_python
REM --- 1. Python Environment Check ---
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo ============================================================================
    echo   [!] Python is not installed or not added to your system PATH.
    echo ============================================================================
    echo   VaaniSetu requires Python 3.10 or higher to run offline AI models.
    echo.
    echo   Choose an option:
    echo     [1] Automatically download and launch Python 3.11 64-bit Installer
    echo     [2] Open the official Python download page in your browser
    echo     [3] Exit setup
    echo.
    set /p PY_CHOICE="Enter your choice (1, 2, or 3) [Default: 1]: "
    if "!PY_CHOICE!"=="" set PY_CHOICE=1
    
    if "!PY_CHOICE!"=="1" (
        echo.
        echo   Downloading official Python 3.11.9 Windows 64-bit installer...
        powershell -command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', 'python_installer.exe')"
        if exist "python_installer.exe" (
            echo.
            echo ============================================================================
            echo   [IMPORTANT] In the Python installer window, MAKE SURE TO CHECK:
            echo               [v] "Add python.exe to PATH" (At the bottom of the window)
            echo ============================================================================
            echo.
            start /wait python_installer.exe
            del python_installer.exe 2>nul
            echo.
            echo   Please restart this quick_start.bat window after Python installation!
            echo.
            pause
            exit /b 0
        ) else (
            echo   [ERROR] Automatic download failed. Opening browser...
            start https://www.python.org/downloads/
            pause
            exit /b 1
        )
    ) else if "!PY_CHOICE!"=="2" (
        start https://www.python.org/downloads/
        echo   Please install Python (remember to check "Add to PATH") and re-run quick_start.bat.
        pause
        exit /b 0
    ) else (
        echo Setup aborted.
        pause
        exit /b 0
    )
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo       Found: %%v [PASS]

REM --- 2. Base Directory Initialization ---
echo.
echo [2/5] Initializing local directories on C:\VaaniSetu...
set BASE_DIR=C:\VaaniSetu
mkdir "%BASE_DIR%" 2>nul
mkdir "%BASE_DIR%\models" 2>nul
mkdir "%BASE_DIR%\workspace" 2>nul
mkdir "%BASE_DIR%\outputs" 2>nul
mkdir "%BASE_DIR%\uploads" 2>nul
mkdir "%BASE_DIR%\logs" 2>nul
echo       Workspace and logging directories ready [PASS]

REM --- 3. Package Dependencies Check ---
echo.
echo [3/5] Checking required Python packages...
python -c "import fastapi, uvicorn" >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo   [!] Required AI and web packages are not yet installed.
    echo       Would you like to install them now from requirements.txt?
    echo       (This takes about 3-5 minutes on standard broadband)
    echo.
    set /p PKG_CHOICE="Install dependencies now? (Y/N) [Default: Y]: "
    if "!PKG_CHOICE!"=="" set PKG_CHOICE=Y
    if /i "!PKG_CHOICE!"=="Y" (
        echo.
        echo   Installing packages via pip...
        pip install -r requirements.txt
        if %errorlevel% neq 0 (
            color 0C
            echo.
            echo [ERROR] Package installation failed. Please check internet connection.
            echo.
            pause
            exit /b 1
        )
        echo   Dependencies installed successfully [PASS]
        color 0A
    )
) else (
    echo       Core Python libraries verified [PASS]
)

REM --- 4. AI Model Weights Check ---
echo.
echo [4/5] Checking AI model assets in %BASE_DIR%\models...
set MODEL_MISSING=0
if not exist "%BASE_DIR%\models\whisper" set MODEL_MISSING=1
if not exist "%BASE_DIR%\models\indictrans2-en-indic" set MODEL_MISSING=1

if %MODEL_MISSING%==1 (
    echo       Note: Offline model weights (~5GB) not fully detected in %BASE_DIR%\models.
    echo       Options:
    echo         [1] Download lightweight Piper TTS voices (~100MB, Fast, Recommended)
    echo         [2] Download complete offline AI model suite (Whisper + IndicTrans2, ~5GB)
    echo         [3] Continue anyway (Use existing weights or mock/test pipeline)
    echo.
    set /p MODEL_OPT="Select option (1, 2, or 3) [Default: 3]: "
    if "!MODEL_OPT!"=="" set MODEL_OPT=3

    if "!MODEL_OPT!"=="1" (
        echo.
        echo   Downloading Piper TTS Indic voices...
        python scripts\download_piper_voices.py
    ) else if "!MODEL_OPT!"=="2" (
        echo.
        echo   Starting complete model download suite...
        call scripts\download_models.bat
        python scripts\download_piper_voices.py
    ) else (
        echo       Skipping model download. Proceeding to startup.
    )
) else (
    echo       AI model assets ready [PASS]
)

REM --- 5. Frontend Production Bundle Check ---
echo.
echo [5/5] Checking Web UI production bundle...
if not exist "frontend\dist\index.html" (
    echo       Building React web interface (one-time step)...
    cd frontend
    call npm install --silent
    call npm run build
    cd ..
    echo       Web UI build complete [PASS]
) else (
    echo       Pre-compiled Web UI bundle ready [PASS]
)

REM --- 6. Launch Server & Open Browser ---
echo.
echo ============================================================================
echo   🚀 Starting VaaniSetu Server...
echo ============================================================================
echo   Local Web Access: http://localhost:8765
echo   Office WiFi LAN:  http://0.0.0.0:8765
echo.
echo   Opening browser in 2 seconds...
echo   Press Ctrl+C in this window at any time to stop the server.
echo ============================================================================
echo.

REM Automatically open default browser when server starts
start "" python -c "import time, webbrowser; time.sleep(2.0); webbrowser.open('http://localhost:8765')" 2>nul

REM Run uvicorn server in foreground
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8765 --log-level info

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ============================================================================
    echo [ERROR] The server stopped with code %errorlevel%.
    echo Check logs in C:\VaaniSetu\logs\vaanisetu.log or run scripts\health_check.bat
    echo ============================================================================
    echo.
    pause
)
