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

REM --- RAM Check (>= 8 GB minimum, 16 GB recommended) ---
for /f "usebackq" %%a in (`powershell -command "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)"`) do set RAM_GB=%%a
if !RAM_GB! GEQ 14 (
    echo [PASS] RAM: !RAM_GB! GB ^(Recommended 16 GB+^)
    set /a PASS+=1
    goto :ram_done
)
if !RAM_GB! GEQ 7 (
    echo [PASS] RAM: !RAM_GB! GB ^(Minimum 8 GB - Enable Resource Saver Mode^)
    set /a PASS+=1
    goto :ram_done
)
echo [FAIL] RAM: !RAM_GB! GB - Need at least 8 GB
set /a FAIL+=1

:ram_done

REM --- Disk Check (>= 15 GB free on C:) ---
for /f "usebackq" %%a in (`powershell -command "[math]::Round((Get-PSDrive C).Free / 1GB)"`) do set DISK_GB=%%a
if !DISK_GB! GEQ 15 (
    echo [PASS] Disk C: Free: !DISK_GB! GB ^(minimum 15 GB^)
    set /a PASS+=1
) else (
    echo [WARN] Disk C: Free: !DISK_GB! GB - Recommend at least 15 GB free for model storage
)

REM --- Python 3.10+ ---
python --version 2>nul | findstr "3.10 3.11 3.12 3.13" >nul
if %errorlevel%==0 (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [PASS] Python %%v
    set /a PASS+=1
) else (
    echo [FAIL] Python 3.10+ not found. Install from https://python.org
    set /a FAIL+=1
)

REM --- Node.js 18+ (Optional if dist already built) ---
node --version 2>nul | findstr "v18 v19 v20 v21 v22 v23 v24" >nul
if %errorlevel%==0 (
    for /f %%v in ('node --version 2^>^&1') do echo [PASS] Node.js %%v
    set /a PASS+=1
) else if exist "%~dp0..\frontend\dist\index.html" (
    echo [PASS] Web UI bundle already pre-built in frontend\dist
    set /a PASS+=1
) else (
    echo [WARN] Node.js 18+ not found. ^(Required only if rebuilding frontend^)
)

REM --- FFmpeg Check (System PATH or Bundled) ---
ffmpeg -version >nul 2>&1
if %errorlevel%==0 (
    echo [PASS] FFmpeg found in system PATH
    set /a PASS+=1
) else if exist "%~dp0..\ffmpeg-8.1.2-essentials_build\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe" (
    echo [PASS] Bundled FFmpeg 8.1.2 found in repository
    set /a PASS+=1
) else (
    echo [WARN] FFmpeg not found in PATH or repo. Required for video dubbing.
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
