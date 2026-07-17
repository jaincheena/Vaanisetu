@echo off
REM ============================================================
REM VaaniSetu — Backup Database & Outputs
REM Copies DB + outputs to a dated folder on external drive.
REM ============================================================
setlocal enabledelayedexpansion
set SOURCE=C:\VaaniSetu
set /p DEST=Enter backup drive/path (e.g. E:\VaaniSetu_Backup): 

echo.
echo ========================================
echo   VaaniSetu Backup
echo ========================================

REM --- Timestamp ---
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE_STR=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME_STR=%%a%%b
set BACKUP_DIR=%DEST%\backup_%DATE_STR%_%TIME_STR%

echo   Source: %SOURCE%
echo   Destination: %BACKUP_DIR%
echo.

mkdir "%BACKUP_DIR%" 2>nul

REM --- Database ---
echo [1/3] Backing up database...
copy "%SOURCE%\vaanisetu.db" "%BACKUP_DIR%\vaanisetu.db" /y
if %errorlevel% neq 0 echo [WARN] DB backup may have failed (server running?)

REM --- Outputs ---
echo [2/3] Backing up outputs...
xcopy "%SOURCE%\outputs\*" "%BACKUP_DIR%\outputs\" /E /I /Q /Y

REM --- Workspace (optional, large) ---
echo [3/3] Backing up workspace (may be large)...
xcopy "%SOURCE%\workspace\*" "%BACKUP_DIR%\workspace\" /E /I /Q /Y

echo.
echo ========================================
echo   Backup complete: %BACKUP_DIR%
echo ========================================
for /f "tokens=*" %%s in ('du -sh "%BACKUP_DIR%" 2^>nul') do echo   Size: %%s
echo.
pause
