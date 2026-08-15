@echo off
REM ============================================================
REM VaaniSetu — Stop Server
REM ============================================================
setlocal
cd /d "%~dp0\.."

echo.
echo ============================================================
echo   Stopping VaaniSetu Server...
echo ============================================================
echo.

REM --- Kill processes running on port 8765 or named uvicorn ---
taskkill /F /IM uvicorn.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq VaaniSetu*" /IM python.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq *uvicorn*" /IM python.exe 2>nul

for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8765 " 2^>nul') do (
    taskkill /F /PID %%p 2>nul
)

echo   VaaniSetu server processes stopped.
echo.
pause
