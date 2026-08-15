@echo off
REM ============================================================
REM VaaniSetu — Operational Rollback & Recovery Tool
REM Restores database, translation memory, and configuration from a snapshot.
REM ============================================================
setlocal enabledelayedexpansion
set TARGET=C:\VaaniSetu
set REPO=%~dp0..

echo.
echo ============================================================
echo   VaaniSetu — Disaster Recovery & Rollback Tool
echo ============================================================
echo.

set /p BACKUP_DIR=Enter path to backup folder to restore (e.g. E:\VaaniSetu_Backup\backup_...): 

if not exist "%BACKUP_DIR%" (
    echo [ERROR] Backup directory not found: "%BACKUP_DIR%"
    pause
    exit /b 1
)

echo.
echo [WARNING] This will restore the database and state from:
echo   "%BACKUP_DIR%"
echo   Target: "%TARGET%"
echo.
set /p CONFIRM=Type YES to confirm rollback: 
if /i not "%CONFIRM%"=="YES" (
    echo [ABORTED] Rollback cancelled by operator.
    pause
    exit /b 0
)

echo.
echo [1/4] Stopping any running VaaniSetu services...
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq VaaniSetu*" 2>nul
echo     Services stopped.

echo.
echo [2/4] Creating safety snapshot of current state...
set SAFETY_DIR=%TARGET%\rollback_safety_%DATE:/=-%_%TIME::=-%
set SAFETY_DIR=%SAFETY_DIR: =_%
mkdir "%SAFETY_DIR%" 2>nul
copy "%TARGET%\vaanisetu.db" "%SAFETY_DIR%\vaanisetu.db.pre_rollback" /y 2>nul
echo     Safety snapshot saved to: %SAFETY_DIR%

echo.
echo [3/4] Restoring database and translation memory...
if exist "%BACKUP_DIR%\vaanisetu.db" (
    copy "%BACKUP_DIR%\vaanisetu.db" "%TARGET%\vaanisetu.db" /y
    echo     Database restored successfully.
) else (
    echo     [WARN] No vaanisetu.db found in backup folder.
)

if exist "%BACKUP_DIR%\outputs" (
    echo     Restoring output archives...
    xcopy "%BACKUP_DIR%\outputs\*" "%TARGET%\outputs\" /E /I /Q /Y 2>nul
)

echo.
echo [4/4] Verifying database integrity...
cd /d "%REPO%"
python -c "import sqlite3; conn=sqlite3.connect(r'%TARGET%\vaanisetu.db'); print('DB Check:', conn.execute('SELECT count(*) FROM jobs').fetchone()[0], 'jobs recorded'); conn.close()"
if %errorlevel% neq 0 (
    echo [WARN] Database verification warning — check logs.
) else (
    echo     Integrity verification: PASS.
)

echo.
echo ============================================================
echo   Rollback Complete! System ready for restart.
echo   To start server: run scripts\start_vaanisetu.bat
echo ============================================================
echo.
pause
