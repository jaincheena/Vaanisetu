@echo off
REM ============================================================
REM VaaniSetu — Hardware & Software Prerequisite Check
REM ============================================================
setlocal enabledelayedexpansion
set PASS=0
set FAIL=0
echo.
echo ========================================
echo   VaaniSetu Hardware Check
echo ========================================
echo.

REM --- RAM Check (>= 16 GB) ---
for /f "usebackq" %%a in (`powershell -command "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)"`) do set RAM_GB=%%a
if !RAM_GB! GEQ 16 (
    echo [PASS] RAM: !RAM_GB! GB ^(minimum 16 GB^)
    set /a PASS+=1
) else (
    echo [FAIL] RAM: !RAM_GB! GB - Need at least 16 GB
    set /a FAIL+=1
)

REM --- Disk Check (>= 200 GB free on C:) ---
for /f "usebackq" %%a in (`powershell -command "[math]::Round((Get-PSDrive C).Free / 1GB)"`) do set DISK_GB=%%a
if !DISK_GB! GEQ 200 (
    echo [PASS] Disk C: Free: !DISK_GB! GB ^(minimum 200 GB^)
    set /a PASS+=1
) else (
    echo [WARN] Disk C: Free: !DISK_GB! GB - Recommend at least 200 GB free
)

REM --- Python 3.11+ ---
python --version 2>nul | findstr "3.11 3.12 3.13" >nul
if %errorlevel%==0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [PASS] Python %%v
    set /a PASS+=1
) else (
    echo [FAIL] Python 3.11+ not found. Install from https://python.org
    set /a FAIL+=1
)

REM --- Node.js 18+ ---
node --version 2>nul | findstr "v18 v19 v20 v21 v22 v23 v24" >nul
if %errorlevel%==0 (
    for /f %%v in ('node --version 2^>^&1') do echo [PASS] Node.js %%v
    set /a PASS+=1
) else (
    echo [FAIL] Node.js 18+ not found. Install from https://nodejs.org
    set /a FAIL+=1
)

REM --- FFmpeg ---
ffmpeg -version 2>nul | findstr "ffmpeg version" >nul
if %errorlevel%==0 (
    echo [PASS] FFmpeg found
    set /a PASS+=1
) else (
    echo [FAIL] FFmpeg not found. Download from https://ffmpeg.org/download.html and add to PATH
    set /a FAIL+=1
)

REM --- Summary ---
echo.
echo ========================================
echo   Results: %PASS% passed, %FAIL% failed
echo ========================================
if %FAIL%==0 (
    echo   System is ready for VaaniSetu setup!
) else (
    echo   Please fix the above issues before running setup.bat
)
echo.
pause
