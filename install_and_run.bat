@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "MODEL_NAME=prisma-engine"
set "MODEL_FILE=Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"
set "MODEL_DIR=models"
set "MODEL_PATH=%MODEL_DIR%\%MODEL_FILE%"
set "MODEL_PART=%MODEL_PATH%.part"
set "MODEL_URL=https://huggingface.co/vicstern/PRISMA-Models/resolve/main/%MODEL_FILE%"

echo ============================================================
echo   Aula Viva - PRISMA (Offline Edge-AI Installer ^& Launcher)
echo ============================================================

:: 1. Verificar Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 no esta instalado o no esta en el PATH.
    echo Descargalo desde: https://www.python.org/downloads/
    echo (Marca la casilla "Add Python to PATH" al instalar.)
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

:: 4. Crear entorno virtual e instalar dependencias
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual aislado (.venv^)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" -c "import streamlit, plotly, numpy, requests" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias de Python...
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Fallo la instalacion de dependencias.
        pause
        exit /b 1
    )
)

:: 5. Descargar Qwen 3.5 4B y compilar prisma-engine si no existe
ollama list 2>nul | findstr /B /C:"%MODEL_NAME%" >nul
if errorlevel 1 (
    if not exist "%MODEL_DIR%" mkdir "%MODEL_DIR%"
    if not exist "%MODEL_PATH%" (
        echo Descargando Qwen 3.5 4B (~2.71 GB^) desde vicstern/PRISMA-Models...
        echo (Esta descarga solo ocurre una vez; despues opera 100%% offline.^)
        curl.exe -fL --progress-bar -C - -o "%MODEL_PART%" "%MODEL_URL%"
        if errorlevel 1 (
            echo [ERROR] No se pudo descargar el modelo desde Hugging Face.
            pause
            exit /b 1
        )
        move /Y "%MODEL_PART%" "%MODEL_PATH%" >nul
    )
    echo Compilando motor local '%MODEL_NAME%' en Ollama...
    ollama create "%MODEL_NAME%" -f Modelfile
    if errorlevel 1 (
        echo [ERROR] No se pudo compilar el modelo en Ollama.
        pause
        exit /b 1
    )
    echo Motor '%MODEL_NAME%' listo.
) else (
    echo Motor '%MODEL_NAME%' detectado en Ollama.
)

:: 6. Iniciar interfaz local
echo Iniciando PRISMA en http://localhost:8501 ...
".venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats false
if errorlevel 1 pause
