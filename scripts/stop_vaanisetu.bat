@echo off
REM ============================================================
REM VaaniSetu — Stop Server
REM ============================================================
setlocal

echo.
echo ========================================
echo   Stopping VaaniSetu...
echo ========================================

REM --- Check for active jobs ---
curl -s http://localhost:8765/api/health 2>nul | findstr "queue_depth" >nul
if %errorlevel%==0 (
    for /f "tokens=*" %%q in ('curl -s http://localhost:8765/api/health 2^>nul') do (
        echo   Server response: %%q
    )
    echo.
    echo   WARNING: Check that no jobs are currently processing!
    echo   If a job is running, stopping now may corrupt that output.
    echo.
    choice /c YN /m "Stop anyway?"
    if errorlevel 2 (
        echo   Aborted. Server still running.
        pause
        exit /b 0
    )
)

REM --- Kill python processes running uvicorn ---
taskkill /f /fi "WINDOWTITLE eq VaaniSetu Server" /im python.exe 2>nul
taskkill /f /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq VaaniSetu*" 2>nul

REM Fallback: kill by port
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8765 " 2^>nul') do (
    taskkill /f /pid %%p 2>nul
)

echo   VaaniSetu stopped.
echo.
pause
