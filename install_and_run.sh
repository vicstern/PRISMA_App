#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Asegurar rutas comunes en macOS (Apple Silicon / Intel)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

MODEL_NAME="prisma-engine"
MODEL_FILE="Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"
MODEL_DIR="models"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_PART="${MODEL_PATH}.part"
MODEL_URL="https://huggingface.co/vicstern/PRISMA-Models/resolve/main/${MODEL_FILE}"

echo "============================================================"
echo "  Aula Viva® — PRISMA™ (Offline Edge-AI Installer & Launcher)"
echo "============================================================"

# 1. Verificar Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Error: Python 3 no está instalado."
  echo "   Instálalo desde: https://www.python.org/downloads/"
  exit 1
fi

# 2. Verificar Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "❌ Error: Ollama no está instalado."
  echo "   Instálalo desde: https://ollama.com/download"
  echo "   Luego vuelve a ejecutar: bash install_and_run.sh"
  exit 1
fi

# 3. Levantar servicio local de Ollama si no está respondiendo
if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "⏳ Iniciando servicio local de Ollama..."
  ollama serve >/dev/null 2>&1 &
  for _ in $(seq 1 15); do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "❌ No se pudo conectar con Ollama en http://localhost:11434."
  echo "   Abre la aplicación Ollama manualmente e intenta de nuevo."
  exit 1
fi

# 4. Crear entorno virtual Python aislado e instalar dependencias
if [ ! -d ".venv" ]; then
  echo "📦 Creando entorno virtual aislado (.venv)..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if ! python -c "import streamlit, plotly, numpy, requests" >/dev/null 2>&1; then
  echo "📦 Instalando dependencias de Python..."
  python -m pip install --upgrade pip >/dev/null 2>&1 || true
  python -m pip install -r requirements.txt
fi

# 5. Descargar modelo Qwen 3.5 4B y compilar prisma-engine si no existe aún
if ! ollama list 2>/dev/null | grep -q "^${MODEL_NAME}"; then
  mkdir -p "${MODEL_DIR}"
  if [ ! -f "${MODEL_PATH}" ]; then
    echo "⬇️  Descargando Qwen 3.5 4B (~2.71 GB) desde vicstern/PRISMA-Models..."
    echo "   (Esta descarga solo ocurre una vez; después opera 100% offline.)"
    curl -fL --progress-bar -C - -o "${MODEL_PART}" "${MODEL_URL}"
    mv "${MODEL_PART}" "${MODEL_PATH}"
  fi

  echo "🧠 Compilando motor local '${MODEL_NAME}' en Ollama..."
  ollama create "${MODEL_NAME}" -f Modelfile
  echo "✅ Motor '${MODEL_NAME}' listo."
else
  echo "✅ Motor '${MODEL_NAME}' detectado en Ollama."
fi

# 6. Iniciar interfaz local de PRISMA™
echo "🚀 Iniciando PRISMA™ en http://localhost:8501 ..."
exec python -m streamlit run app.py --browser.gatherUsageStats false
