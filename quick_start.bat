@echo off
REM ============================================================================
REM VaaniSetu - 1-Click Launch and Startup Wizard
REM ============================================================================
setlocal
cd /d "%~dp0"
title VaaniSetu - AI Translation Platform for BAIF
color 0A

where python >nul 2>&1
if %errorlevel% neq 0 goto :no_python

python launcher.py
if %errorlevel% neq 0 goto :error
exit /b 0

:no_python
color 0E
echo ============================================================================
echo [!] Python is not installed or not in your system PATH.
echo ============================================================================
echo.
echo Options:
echo   1. Automatically download and launch Python 3.11 64-bit installer
echo   2. Open python.org in web browser
echo   3. Exit
echo.
set /p PY_OPT="Enter choice 1, 2, or 3 [Default 1]: "
if "%PY_OPT%"=="" set PY_OPT=1

if "%PY_OPT%"=="1" goto :dl_python
if "%PY_OPT%"=="2" goto :open_python_web
goto :exit_clean

:dl_python
echo.
echo Downloading Python 3.11.9 installer...
powershell -command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', 'python_installer.exe')"
if not exist "python_installer.exe" goto :dl_fail
echo.
echo ============================================================================
echo [IMPORTANT] In the installer window, MAKE SURE to check:
echo             Add python.exe to PATH (at the bottom of the installer window)
echo ============================================================================
echo.
start /wait python_installer.exe
del python_installer.exe 2>nul
echo.
echo Installation complete. Please re-run quick_start.bat!
echo.
pause
exit /b 0

:dl_fail
echo Download failed. Opening browser...
start https://www.python.org/downloads/
pause
exit /b 1

:open_python_web
start https://www.python.org/downloads/
echo Please install Python (check Add to PATH) and re-run quick_start.bat.
pause
exit /b 0

:exit_clean
echo Setup cancelled.
pause
exit /b 0

:error
color 0C
echo.
echo ============================================================================
echo [ERROR] Process exited with code %errorlevel%.
echo Check logs in C:\VaaniSetu\logs\vaanisetu.log
echo ============================================================================
echo.
pause
exit /b %errorlevel%
