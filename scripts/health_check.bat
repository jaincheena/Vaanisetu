@echo off
REM ============================================================
REM VaaniSetu — Operational Health and Pre-Flight Check Script
REM ============================================================
setlocal
set REPO=%~dp0..

echo.
echo ============================================================
echo   VaaniSetu — Operational Readiness and Health Check
echo ============================================================
echo.

cd /d "%REPO%"
python scripts\preflight_check.py

echo.
echo Checking Live Server Status (http://localhost:8765/api/health)...
python -c "import urllib.request, json; resp=urllib.request.urlopen('http://localhost:8765/api/health', timeout=2); data=json.loads(resp.read().decode()); print('Live Server Response: ONLINE | RAM free:', round(data.get('ram_available_gb',0),1), 'GB | GPU:', data.get('device','cpu'))" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Live server is not currently running. Run scripts\start_vaanisetu.bat to start.
)

echo.
pause
