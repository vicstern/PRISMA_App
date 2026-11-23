@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "MODEL_DIR=models"
set "HF_BASE=https://huggingface.co/vicstern/PRISMA-Models/resolve/main"

set "FILE_4B=Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"
set "FILE_9B=Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"

set "NAME_4B=prisma-engine-4b"
set "NAME_9B=prisma-engine-9b"
set "NAME_LEGACY=prisma-engine"

set "FORCE_MENU=0"
if /I "%~1"=="--models" set "FORCE_MENU=1"
if /I "%~1"=="-m" set "FORCE_MENU=1"

echo ============================================================
echo   Aula Viva - PRISMA (Offline Edge-AI Installer ^& Launcher)
echo ============================================================

:: 1. Verificar Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 no esta instalado o no esta en el PATH.
    echo Descargalo desde: https://www.python.org/downloads/
    echo ^(Marca la casilla "Add Python to PATH" al instalar.^)
    pause
    exit /b 1
)

:: 2. Verificar Ollama
where ollama >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama no esta instalado.
    echo Descargalo desde: https://ollama.com/download
    echo Luego vuelve a abrir install_and_run.bat
    pause
    exit /b 1
)

:: 3. Levantar Ollama si no responde
curl.exe -sf http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Iniciando servicio local de Ollama...
    start "" /b ollama serve >nul 2>&1
    timeout /t 4 /nobreak >nul
)

curl.exe -sf http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se pudo conectar con Ollama en http://localhost:11434.
    echo Abre Ollama manualmente e intenta de nuevo.
    pause
    exit /b 1
)

:: 4. Crear entorno virtual e instalar/actualizar dependencias
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual aislado ^(.venv^)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -c "import streamlit, plotly, numpy, requests, docx" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias de Python ^(incluye exportacion .docx^)...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de dependencias.
        pause
        exit /b 1
    )
)

:: 5. Verificar motores instalados en Ollama
set "HAS_4B=0"
set "HAS_9B=0"
set "HAS_LEG=0"
ollama list 2>nul | findstr /B /C:"%NAME_4B%:" >nul && set "HAS_4B=1"
ollama list 2>nul | findstr /B /C:"%NAME_9B%:" >nul && set "HAS_9B=1"
ollama list 2>nul | findstr /B /C:"%NAME_LEGACY%:" >nul && set "HAS_LEG=1"

set "NEED_MENU=0"
if "%FORCE_MENU%"=="1" set "NEED_MENU=1"
if "%HAS_4B%"=="0" if "%HAS_9B%"=="0" if "%HAS_LEG%"=="0" set "NEED_MENU=1"

if "%NEED_MENU%"=="1" (
    set "RAM_GB=8"
    for /f "usebackq delims=" %%R in (`powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB)" 2^>nul`) do set "RAM_GB=%%R"

    if !RAM_GB! LEQ 8 (
        set "REC_OPT=1"
        set "REC_TXT=PRISMA 4B (~2.71 GB) - optimo para !RAM_GB! GB RAM"
    ) else (
        set "REC_OPT=2"
        set "REC_TXT=PRISMA 9B (~5.63 GB) - mayor profundidad analitica para !RAM_GB! GB RAM"
    )

    echo.
    echo Memoria RAM detectada / Detected RAM: !RAM_GB! GB
    echo Recomendacion / Recommended: [!REC_OPT!] !REC_TXT!
    echo.
    echo Selecciona el motor local a instalar / Choose local engine to install:
    echo   [1] PRISMA 4B  ^(Qwen3.5-4B - ~2.71 GB^)
    echo   [2] PRISMA 9B  ^(Qwen3.5-9B - ~5.63 GB^)
    echo   [3] Ambos / Both ^(4B + 9B - ~8.34 GB^)
    echo.
    set "CHOICE="
    set /p "CHOICE=Elige opcion [1/2/3] (Enter = !REC_OPT!): "
    if "!CHOICE!"=="" set "CHOICE=!REC_OPT!"

    if "!CHOICE!"=="1" (
        call :install_engine "%NAME_4B%" "%FILE_4B%" "~2.71 GB"
        if errorlevel 1 exit /b 1
    ) else if "!CHOICE!"=="2" (
        call :install_engine "%NAME_9B%" "%FILE_9B%" "~5.63 GB"
        if errorlevel 1 exit /b 1
    ) else if "!CHOICE!"=="3" (
        call :install_engine "%NAME_4B%" "%FILE_4B%" "~2.71 GB"
        if errorlevel 1 exit /b 1
        call :install_engine "%NAME_9B%" "%FILE_9B%" "~5.63 GB"
        if errorlevel 1 exit /b 1
    ) else (
        echo Opcion no reconocida; instalando recomendacion [!REC_OPT!]...
        if "!REC_OPT!"=="1" (
            call :install_engine "%NAME_4B%" "%FILE_4B%" "~2.71 GB"
        ) else (
            call :install_engine "%NAME_9B%" "%FILE_9B%" "~5.63 GB"
        )
        if errorlevel 1 exit /b 1
    )
) else (
    echo Motores PRISMA detectados en Ollama:
    if "%HAS_4B%"=="1" echo   * %NAME_4B% ^(Qwen 3.5 4B^)
    if "%HAS_9B%"=="1" echo   * %NAME_9B% ^(Qwen 3.5 9B^)
    if "%HAS_LEG%"=="1" echo   * %NAME_LEGACY% ^(instalacion previa^)
    echo   ^(Tip: ejecuta "install_and_run.bat --models" para instalar otro motor^)
)

:: 6. Iniciar interfaz local
echo.
echo Iniciando PRISMA en http://localhost:8501 ...
".venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats false
if errorlevel 1 pause
exit /b 0

:install_engine
set "M_NAME=%~1"
set "M_FILE=%~2"
set "M_SIZE=%~3"
set "M_PATH=%MODEL_DIR%\%M_FILE%"
set "M_PART=%M_PATH%.part"
set "M_URL=%HF_BASE%/%M_FILE%"

if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
if not exist "%M_PATH%" (
    echo Descargando %M_FILE% ^(%M_SIZE%^) desde vicstern/PRISMA-Models...
    echo ^(Esta descarga solo ocurre una vez; despues opera 100%% offline.^)
    curl.exe -fL --progress-bar -C - -o "%M_PART%" "%M_URL%"
    if errorlevel 1 (
        echo [ERROR] No se pudo descargar %M_FILE% desde Hugging Face.
        pause
        exit /b 1
    )
    move /Y "%M_PART%" "%M_PATH%" >nul
) else (
    echo Archivo local encontrado: %M_PATH%
)

set "TMP_MF=%MODEL_DIR%\.Modelfile.tmp"
".venv\Scripts\python.exe" -c "lines=open('Modelfile',encoding='utf-8').readlines(); lines[0]='FROM ./models/%M_FILE%\n'; open(r'%TMP_MF%','w',encoding='utf-8').writelines(lines)"
echo Compilando motor local '%M_NAME%' en Ollama...
ollama create "%M_NAME%" -f "%TMP_MF%"
if errorlevel 1 (
    del /f /q "%TMP_MF%" >nul 2>&1
    echo [ERROR] No se pudo compilar '%M_NAME%' en Ollama.
    pause
    exit /b 1
)
del /f /q "%TMP_MF%" >nul 2>&1
echo Motor '%M_NAME%' listo.
exit /b 0
