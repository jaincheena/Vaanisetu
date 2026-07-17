@echo off
REM ============================================================
REM VaaniSetu — Offline USB Installation
REM Zero internet required. All packages on USB.
REM Run from: USB:\VaaniSetu_USB_Install\install_from_usb.bat
REM
REM Expected USB structure:
REM   USB:\
REM     packages\         <- pip wheel files (.whl)
REM     node_modules_zip\ <- pre-built frontend zip
REM     models\           <- Whisper + IndicTrans2 model files
REM     installers\
REM       python-3.11.x-amd64.exe
REM       node-v20.x-x64.msi
REM       ffmpeg-release-essentials.zip
REM     repo\             <- VaaniSetu repo folder
REM ============================================================
setlocal enabledelayedexpansion
set USB=%~dp0
set INSTALL_ROOT=C:\VaaniSetu
set REPO_DEST=C:\VaaniSetu\repo

echo.
echo ========================================
echo   VaaniSetu Offline USB Installation
echo ========================================
echo   USB path: %USB%
echo.

REM --- Step 1: Install Python (silent) ---
echo [1/6] Installing Python 3.11...
if exist "%USB%installers\python-3.11.*-amd64.exe" (
    for %%f in ("%USB%installers\python-3.11.*-amd64.exe") do (
        "%%f" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    )
    echo   Python installed.
) else (
    echo   [SKIP] Python installer not found on USB. Assuming already installed.
)

REM --- Step 2: Install Node.js (silent) ---
echo [2/6] Installing Node.js 20...
if exist "%USB%installers\node-v20.*-x64.msi" (
    for %%f in ("%USB%installers\node-v20.*-x64.msi") do (
        msiexec /i "%%f" /quiet /norestart
    )
    echo   Node.js installed.
) else (
    echo   [SKIP] Node installer not found. Assuming already installed.
)

REM --- Step 3: Install FFmpeg ---
echo [3/6] Installing FFmpeg...
if exist "%USB%installers\ffmpeg-release-essentials.zip" (
    powershell -command "Expand-Archive '%USB%installers\ffmpeg-release-essentials.zip' -DestinationPath 'C:\ffmpeg' -Force"
    setx PATH "C:\ffmpeg\bin;%PATH%" /M
    echo   FFmpeg installed.
) else (
    echo   [SKIP] FFmpeg archive not found. Assuming already installed.
)

REM --- Step 4: Copy repo ---
echo [4/6] Copying VaaniSetu application files...
if exist "%USB%repo" (
    xcopy "%USB%repo\*" "%REPO_DEST%\" /E /I /Q /Y
) else (
    echo   [ERROR] repo folder not found on USB.
    pause
    exit /b 1
)

REM --- Step 5: Install Python packages from USB (no index) ---
echo [5/6] Installing Python packages from USB (offline)...
pip install --no-index --find-links="%USB%packages" -r "%REPO_DEST%\requirements.txt"
if %errorlevel% neq 0 (
    echo   [ERROR] Package install failed. Check USB\packages\ content.
    pause
    exit /b 1
)

REM --- Step 6: Build frontend (or extract pre-built) ---
echo [6/6] Setting up frontend...
if exist "%USB%frontend_dist.zip" (
    powershell -command "Expand-Archive '%USB%frontend_dist.zip' -DestinationPath '%REPO_DEST%\frontend\dist' -Force"
    echo   Frontend extracted from pre-built ZIP.
) else (
    cd /d "%REPO_DEST%\frontend"
    call npm install --offline
    call npm run build
)

REM --- Copy models ---
echo Copying AI model files (this may take a few minutes)...
xcopy "%USB%models\*" "%INSTALL_ROOT%\models\" /E /I /Q /Y

REM --- Create desktop shortcut ---
echo Creating desktop shortcut...
powershell -command "$s=(New-Object -COM WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\VaaniSetu.lnk'); $s.TargetPath='%REPO_DEST%\scripts\start_vaanisetu.bat'; $s.WorkingDirectory='%REPO_DEST%'; $s.IconLocation='%SystemRoot%\System32\SHELL32.dll,23'; $s.Description='Start VaaniSetu Translation Platform'; $s.Save()"

echo.
echo ========================================
echo   USB Installation Complete!
echo   Double-click VaaniSetu on your Desktop
echo   to start the application.
echo ========================================
echo.
pause
