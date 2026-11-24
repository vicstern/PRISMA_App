@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "MODEL_DIR=models"
set "FILE_4B=PRISMA-Core-Qwen3.5-4B-HauhauCS-Q4_K_M.gguf"
set "FILE_9B=PRISMA-Core-Qwen3.5-9B-HauhauCS-Q4_K_M.gguf"
set "URL_4B=https://huggingface.co/vicstern/PRISMA-Models/resolve/main/%FILE_4B%"
set "URL_9B=https://huggingface.co/vicstern/PRISMA-Models/resolve/main/%FILE_9B%"
set "BASE_4B=prisma-engine-4b"
set "BASE_9B=prisma-engine-9b"

echo ============================================================
echo   Aula Viva(R) - PRISMA(TM) (Offline Edge-AI Installer)
echo ============================================================

where python >nul 2>&1 || (echo [ERROR] Python 3 not found. Install from https://www.python.org/downloads/ & pause & exit /b 1)
where ollama >nul 2>&1 || (echo [ERROR] Ollama not found. Install from https://ollama.com/download & pause & exit /b 1)

if not exist ".venv" (
    echo Creating isolated virtual environment ^(.venv^)...
    python -m venv .venv
    .venv\Scripts\pip install --upgrade pip >nul 2>&1
    .venv\Scripts\pip install -r requirements.txt
) else (
    .venv\Scripts\python -c "import docx" >nul 2>&1 || .venv\Scripts\pip install -r requirements.txt
)

set "FORCE_MENU=0"
if /i "%~1"=="--models" set "FORCE_MENU=1"

set "HAS_4B=0"
set "HAS_9B=0"
ollama list 2>nul | findstr /b /c:"%BASE_4B%-es:" >nul && ollama list 2>nul | findstr /b /c:"%BASE_4B%-en:" >nul && set "HAS_4B=1"
ollama list 2>nul | findstr /b /c:"%BASE_9B%-es:" >nul && ollama list 2>nul | findstr /b /c:"%BASE_9B%-en:" >nul && set "HAS_9B=1"

if "%FORCE_MENU%"=="1" goto :choose_model
if "%HAS_4B%"=="0" if "%HAS_9B%"=="0" goto :choose_model
goto :launch_app

:choose_model
for /f "usebackq delims=" %%R in (`powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)"`) do set "RAM_GB=%%R"
if "%RAM_GB%"=="" set "RAM_GB=8"

echo.
echo Detected RAM: %RAM_GB% GB
if %RAM_GB% LEQ 12 (
    set "REC=1"
    echo Recommended: [1] PRISMA 4B ^(~2.71 GB^)
) else (
    set "REC=2"
    echo Recommended: [2] PRISMA 9B ^(~5.63 GB^)
)
echo.
echo Choose local engine ^(compiles ES + EN without duplicating disk space^):
echo   [1] PRISMA 4B  ^(^<16 GB RAM · PRISMA-Core Qwen3.5-4B · ~2.71 GB^)
echo   [2] PRISMA 9B  ^(^>=16 GB RAM · PRISMA-Core Qwen3.5-9B · ~5.63 GB^)
echo   [3] Both       ^(4B + 9B · ~8.34 GB^)
echo.
set "CHOICE="
set /p "CHOICE=Option [1/2/3] (Enter = %REC%): "
if "%CHOICE%"=="" set "CHOICE=%REC%"

if "%CHOICE%"=="1" call :compile_dual "%BASE_4B%" "%FILE_4B%" "%URL_4B%"
if "%CHOICE%"=="2" call :compile_dual "%BASE_9B%" "%FILE_9B%" "%URL_9B%"
if "%CHOICE%"=="3" (
    call :compile_dual "%BASE_4B%" "%FILE_4B%" "%URL_4B%"
    call :compile_dual "%BASE_9B%" "%FILE_9B%" "%URL_9B%"
)
goto :launch_app

:compile_dual
set "BNAME=%~1"
set "FNAME=%~2"
set "FURL=%~3"
if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
if not exist "%MODEL_DIR%\%FNAME%" (
    echo Downloading %FNAME% from vicstern/PRISMA-Models...
    curl -L --fail --progress-bar -o "%MODEL_DIR%\%FNAME%.part" "%FURL%"
    move /y "%MODEL_DIR%\%FNAME%.part" "%MODEL_DIR%\%FNAME%" >nul
)
for %%L in (es en) do (
    set "MFSRC=Modelfile.%%L"
    if not exist "!MFSRC!" set "MFSRC=Modelfile"
    set "TMP_MF=.Modelfile.tmp"
    powershell -NoProfile -Command "$l = Get-Content '!MFSRC!' -Encoding UTF8; $l[0] = 'FROM ./models/%FNAME%'; Set-Content '!TMP_MF!' $l -Encoding UTF8"
    echo Compiling %BNAME%-%%L in Ollama...
    ollama create "%BNAME%-%%L" -f "!TMP_MF!"
    del /f /q "!TMP_MF!" 2>nul
)
exit /b 0

:launch_app
echo.
echo Launching PRISMA(TM) at http://localhost:8501 ...
.venv\Scripts\streamlit run app.py
