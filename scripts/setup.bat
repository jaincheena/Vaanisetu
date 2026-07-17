@echo off
REM ============================================================
REM VaaniSetu — First-Time Setup Script
REM Run once after check_hardware.bat passes.
REM ============================================================
setlocal
set ROOT=C:\VaaniSetu
set REPO=%~dp0..

echo.
echo ========================================
echo   VaaniSetu Setup
echo ========================================
echo.

REM --- Create directory structure ---
echo [1/4] Creating directories...
mkdir "%ROOT%"            2>nul
mkdir "%ROOT%\models"     2>nul
mkdir "%ROOT%\models\whisper" 2>nul
mkdir "%ROOT%\models\indictrans2-en-indic" 2>nul
mkdir "%ROOT%\models\indictrans2-indic-en" 2>nul
mkdir "%ROOT%\models\coqui_xtts" 2>nul
mkdir "%ROOT%\workspace"  2>nul
mkdir "%ROOT%\outputs"    2>nul
mkdir "%ROOT%\uploads"    2>nul
echo     Done.

REM --- Python dependencies ---
echo.
echo [2/4] Installing Python packages...
echo     This may take 10-20 minutes (PyTorch is large).
cd /d "%REPO%"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Check your internet connection.
    pause
    exit /b 1
)
echo     Done.

REM --- Frontend build ---
echo.
echo [3/4] Installing frontend dependencies...
cd /d "%REPO%\frontend"
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] npm install failed.
    pause
    exit /b 1
)
echo     Building React app...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] npm run build failed.
    pause
    exit /b 1
)
echo     Done.

REM --- Verify ---
echo.
echo [4/4] Verifying setup...
cd /d "%REPO%"
python -c "import fastapi, whisper, transformers, torch; print('Core packages OK')"
if %errorlevel% neq 0 (
    echo [WARN] Some packages not verified — check manually.
)

echo.
echo ========================================
echo   Setup Complete!
echo   Next step: run download_models.bat
echo ========================================
echo.
pause
