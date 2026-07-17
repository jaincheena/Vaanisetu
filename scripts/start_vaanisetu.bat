@echo off
REM ============================================================
REM VaaniSetu — Start Server
REM ============================================================
setlocal
set REPO=%~dp0..
set PORT=8765
set MAX_WAIT=120

echo.
echo ========================================
echo   Starting VaaniSetu...
echo ========================================
echo.

REM --- Start uvicorn in background ---
cd /d "%REPO%"
start "VaaniSetu Server" /b python -m uvicorn backend.main:app --host 0.0.0.0 --port %PORT% --workers 1

echo Waiting for server to be ready (models loading, may take 2-5 min)...
set /a WAITED=0

:wait_loop
timeout /t 5 /nobreak >nul
curl -s http://localhost:%PORT%/api/health >nul 2>&1
if %errorlevel%==0 goto :server_ready
set /a WAITED=%WAITED%+5
if %WAITED% GEQ %MAX_WAIT% (
    echo [ERROR] Server did not respond within %MAX_WAIT% seconds.
    echo Check for errors in the server window.
    pause
    exit /b 1
)
echo   Still loading... (%WAITED%s elapsed)
goto :wait_loop

:server_ready
echo.
echo ========================================
echo   VaaniSetu is READY!
echo ========================================

REM --- Get LAN IP ---
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r "IPv4.*192\. IPv4.*10\. IPv4.*172\."') do (
    set LAN_IP=%%a
    set LAN_IP=!LAN_IP: =!
    goto :got_ip
)
set LAN_IP=localhost
:got_ip

echo.
echo   Local:   http://localhost:%PORT%
echo   LAN:     http://%LAN_IP%:%PORT%
echo.
echo   Share the LAN address with office devices.
echo.

REM --- Open browser ---
start "" http://localhost:%PORT%

echo   Server is running. Close this window to stop.
echo   Or run stop_vaanisetu.bat to stop gracefully.
echo.
pause
