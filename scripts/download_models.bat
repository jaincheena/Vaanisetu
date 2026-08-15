@echo off
setlocal

set MODELS=C:\VaaniSetu\models
if not exist "%MODELS%" mkdir "%MODELS%"

echo.
echo ========================================
echo   VaaniSetu - Download AI Models
echo ========================================
echo   This will download offline AI models:
echo   - Whisper Speech-to-Text
echo   - IndicTrans2 EN-Indic & Indic-EN
echo   - Piper Indic ONNX Voices
echo   - Coqui XTTS v2 Voice Cloning (Optional)
echo ========================================
echo.

set HF_TOKEN=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
set HUGGING_FACE_HUB_TOKEN=%HF_TOKEN%

echo [1/4] Downloading Whisper...
python scripts\download_helper.py whisper
if %errorlevel% neq 0 (
    echo [ERROR] Whisper download failed.
    pause
    exit /b 1
)

echo.
echo [2/4] Downloading IndicTrans2 en-indic...
python scripts\download_helper.py en-indic
if %errorlevel% neq 0 (
    echo [ERROR] IndicTrans2 en-indic download failed.
    pause
    exit /b 1
)

echo.
echo [3/4] Downloading IndicTrans2 indic-en...
python scripts\download_helper.py indic-en
if %errorlevel% neq 0 (
    echo [ERROR] IndicTrans2 indic-en download failed.
    pause
    exit /b 1
)

echo.
echo [4/4] Downloading Piper TTS & XTTS Voice Models...
python scripts\download_helper.py piper
python scripts\download_helper.py tts

echo.
echo ========================================
echo All models downloaded successfully!
echo Models saved under:
echo %MODELS%
echo ========================================
pause