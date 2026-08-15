@echo off
setlocal

set MODELS=C:\VaaniSetu\models

echo.
echo ========================================
echo   VaaniSetu - Download AI Models
echo ========================================
echo   This will download approximately 6-8 GB.
echo ========================================
echo.

REM =====================================================
REM Hugging Face Token (replace with your actual token)
REM =====================================================
set HF_TOKEN=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
set HUGGING_FACE_HUB_TOKEN=%HF_TOKEN%



if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Hugging Face login failed.
    pause
    exit /b 1
)

REM =====================================================
REM Whisper
REM =====================================================

echo.
echo [1/4] Downloading Whisper...

python -c "import whisper; whisper.load_model('large-v3-turbo', download_root=r'%MODELS%\whisper'); print('Whisper OK')"

if %errorlevel% neq 0 (
    echo [ERROR] Whisper download failed.
    pause
    exit /b 1
)

REM =====================================================
REM IndicTrans2 EN -> INDIC
REM =====================================================

echo.
echo [2/4] Downloading IndicTrans2 en-indic...

python -c "from transformers import AutoTokenizer,AutoModelForSeq2SeqLM; model='ai4bharat/indictrans2-en-indic-dist-200M'; tokenizer=AutoTokenizer.from_pretrained(model,trust_remote_code=True,token='%HF_TOKEN%'); model_obj=AutoModelForSeq2SeqLM.from_pretrained(model,trust_remote_code=True,token='%HF_TOKEN%'); model_obj.save_pretrained(r'%MODELS%\indictrans2-en-indic'); tokenizer.save_pretrained(r'%MODELS%\indictrans2-en-indic'); print('en-indic OK')"

if %errorlevel% neq 0 (
    echo [ERROR] IndicTrans2 en-indic download failed.
    pause
    exit /b 1
)

REM =====================================================
REM IndicTrans2 INDIC -> EN
REM =====================================================

echo.
echo [3/4] Downloading IndicTrans2 indic-en...

python -c "from transformers import AutoTokenizer,AutoModelForSeq2SeqLM; model='ai4bharat/indictrans2-indic-en-dist-200M'; tokenizer=AutoTokenizer.from_pretrained(model,trust_remote_code=True,token='%HF_TOKEN%'); model_obj=AutoModelForSeq2SeqLM.from_pretrained(model,trust_remote_code=True,token='%HF_TOKEN%'); model_obj.save_pretrained(r'%MODELS%\indictrans2-indic-en'); tokenizer.save_pretrained(r'%MODELS%\indictrans2-indic-en'); print('indic-en OK')"

if %errorlevel% neq 0 (
    echo [ERROR] IndicTrans2 indic-en download failed.
    pause
    exit /b 1
)

REM =====================================================
REM XTTS
REM =====================================================

echo.
echo [4/4] Downloading XTTS...

python -c "from TTS.utils.manage import ModelManager; mm = ModelManager(models_file=None, output_prefix=r'%MODELS%'); model_path, _, _ = mm.download_model('tts_models/multilingual/multi-dataset/xtts_v2'); mm.unpack_model(model_path); print('XTTS OK')"

if %errorlevel% neq 0 (
    echo [ERROR] XTTS download failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo All models downloaded successfully!
echo Models saved under:
echo %MODELS%
echo ========================================
pause