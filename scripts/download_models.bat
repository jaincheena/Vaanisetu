@echo off
REM ============================================================
REM VaaniSetu — Model Download Script
REM Downloads Whisper + IndicTrans2 models (~6-8 GB total).
REM Requires internet. Run once before going offline.
REM ============================================================
setlocal
set MODELS=C:\VaaniSetu\models

echo.
echo ========================================
echo   VaaniSetu — Download AI Models
echo ========================================
echo   This will download approximately 6-8 GB.
echo   Ensure stable internet. Do NOT interrupt.
echo ========================================
echo.
pause

REM --- Whisper large-v3-turbo ---
echo [1/3] Downloading Whisper large-v3-turbo (~3 GB)...
python -c "import whisper; whisper.load_model('large-v3-turbo', download_root=r'%MODELS%\whisper'); print('Whisper OK')"
if %errorlevel% neq 0 (
    echo [ERROR] Whisper download failed.
    pause
    exit /b 1
)

REM --- IndicTrans2 en-indic ---
echo.
echo [2/3] Downloading IndicTrans2 en-indic (~1.5 GB)...
python -c "from transformers import AutoModelForSeq2SeqLM, AutoTokenizer; m=AutoModelForSeq2SeqLM.from_pretrained('ai4bharat/indictrans2-en-indic-dist-200M',trust_remote_code=True); t=AutoTokenizer.from_pretrained('ai4bharat/indictrans2-en-indic-dist-200M',trust_remote_code=True); m.save_pretrained(r'%MODELS%\indictrans2-en-indic'); t.save_pretrained(r'%MODELS%\indictrans2-en-indic'); print('en-indic OK')"
if %errorlevel% neq 0 (
    echo [ERROR] IndicTrans2 en-indic download failed.
    pause
    exit /b 1
)

REM --- IndicTrans2 indic-en ---
echo.
echo [3/3] Downloading IndicTrans2 indic-en (~1.5 GB)...
python -c "from transformers import AutoModelForSeq2SeqLM, AutoTokenizer; m=AutoModelForSeq2SeqLM.from_pretrained('ai4bharat/indictrans2-indic-en-dist-200M',trust_remote_code=True); t=AutoTokenizer.from_pretrained('ai4bharat/indictrans2-indic-en-dist-200M',trust_remote_code=True); m.save_pretrained(r'%MODELS%\indictrans2-indic-en'); t.save_pretrained(r'%MODELS%\indictrans2-indic-en'); print('indic-en OK')"
if %errorlevel% neq 0 (
    echo [ERROR] IndicTrans2 indic-en download failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   All models downloaded successfully!
echo   Total size: check C:\VaaniSetu\models
echo   Next: run start_vaanisetu.bat
echo ========================================
echo.
pause
