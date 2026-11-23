#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Asegurar rutas comunes en macOS (Apple Silicon / Intel)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

MODEL_DIR="models"
HF_BASE="https://huggingface.co/vicstern/PRISMA-Models/resolve/main"

FILE_4B="Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"
FILE_9B="Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf"

NAME_4B="prisma-engine-4b"
NAME_9B="prisma-engine-9b"
NAME_LEGACY="prisma-engine"

FORCE_MENU=0
if [ "${1:-}" = "--models" ] || [ "${1:-}" = "-m" ]; then
  FORCE_MENU=1
fi

echo "============================================================"
echo "  Aula Viva® — PRISMA™ (Offline Edge-AI Installer & Launcher)"
echo "============================================================"

# 1. Verificar Python 3
if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Error: Python 3 no está instalado / Python 3 is not installed."
  echo "   https://www.python.org/downloads/"
  exit 1
fi

# 2. Verificar Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "❌ Error: Ollama no está instalado / Ollama is not installed."
  echo "   https://ollama.com/download"
  echo "   Luego ejecuta / Then run: bash install_and_run.sh"
  exit 1
fi

# 3. Levantar servicio local de Ollama si no responde
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

# 4. Crear entorno virtual aislado e instalar/actualizar dependencias
if [ ! -d ".venv" ]; then
  echo "📦 Creando entorno virtual aislado (.venv)..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if ! python -c "import streamlit, plotly, numpy, requests, docx" >/dev/null 2>&1; then
  echo "📦 Instalando dependencias de Python (incluye exportación .docx)..."
  python -m pip install --upgrade pip >/dev/null 2>&1 || true
  python -m pip install -r requirements.txt
fi

# 5. Funciones auxiliares: RAM y compilación de motores
detectar_ram_gb() {
  local ram_gb=8
  if [ "$(uname -s)" = "Darwin" ]; then
    local bytes
    bytes=$(sysctl -n hw.memsize 2>/dev/null || echo 8589934592)
    ram_gb=$(( (bytes + 536870912) / 1073741824 ))
  elif [ -r /proc/meminfo ]; then
    local kb
    kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 8388608)
    ram_gb=$(( (kb + 524288) / 1048576 ))
  fi
  echo "$ram_gb"
}

modelo_instalado() {
  local m_name="$1"
  ollama list 2>/dev/null | grep -Eq "^${m_name}(:|[[:space:]])"
}

instalar_motor() {
  local m_name="$1"
  local m_file="$2"
  local m_size="$3"
  local m_path="${MODEL_DIR}/${m_file}"
  local m_part="${m_path}.part"
  local m_url="${HF_BASE}/${m_file}"

  mkdir -p "${MODEL_DIR}"
  if [ ! -f "${m_path}" ]; then
    echo "⬇️  Descargando ${m_file} (${m_size}) desde vicstern/PRISMA-Models..."
    echo "   (Esta descarga solo ocurre una vez; después opera 100% offline.)"
    curl -fL --progress-bar -C - -o "${m_part}" "${m_url}"
    mv "${m_part}" "${m_path}"
  else
    echo "📁 Archivo local encontrado: ${m_path}"
  fi

  local tmp_mf="${MODEL_DIR}/.Modelfile.tmp"
  python -c "
import sys
with open('Modelfile', 'r', encoding='utf-8') as f:
    lines = f.readlines()
lines[0] = 'FROM ./${m_path}\n'
with open('${tmp_mf}', 'w', encoding='utf-8') as f:
    f.writelines(lines)
"
  echo "🧠 Compilando motor local '${m_name}' en Ollama..."
  ollama create "${m_name}" -f "${tmp_mf}"
  rm -f "${tmp_mf}"
  echo "✅ Motor '${m_name}' listo."
}

# 6. Detectar motores existentes y mostrar menú solo si hace falta (o con --models)
HAS_4B=0; modelo_instalado "${NAME_4B}" && HAS_4B=1
HAS_9B=0; modelo_instalado "${NAME_9B}" && HAS_9B=1
HAS_LEG=0; modelo_instalado "${NAME_LEGACY}" && HAS_LEG=1

if [ "${FORCE_MENU}" -eq 1 ] || { [ "${HAS_4B}" -eq 0 ] && [ "${HAS_9B}" -eq 0 ] && [ "${HAS_LEG}" -eq 0 ]; }; then
  RAM_GB=$(detectar_ram_gb)
  if [ "${RAM_GB}" -le 8 ]; then
    REC_OPT="1"
    REC_TXT="PRISMA 4B (~2.71 GB) — óptimo para ${RAM_GB} GB RAM"
  else
    REC_OPT="2"
    REC_TXT="PRISMA 9B (~5.63 GB) — mayor profundidad analítica para ${RAM_GB} GB RAM"
  fi

  echo ""
  echo "🖥️  Memoria RAM detectada / Detected RAM: ${RAM_GB} GB"
  echo "💡 Recomendación / Recommended: [${REC_OPT}] ${REC_TXT}"
  echo ""
  echo "Selecciona el motor local a instalar / Choose local engine to install:"
  echo "  [1] PRISMA 4B  (Qwen3.5-4B · ~2.71 GB)  $( [ "${HAS_4B}" -eq 1 ] && echo '[ya instalado]' || echo '' )"
  echo "  [2] PRISMA 9B  (Qwen3.5-9B · ~5.63 GB)  $( [ "${HAS_9B}" -eq 1 ] && echo '[ya instalado]' || echo '' )"
  echo "  [3] Ambos / Both (4B + 9B · ~8.34 GB)"
  echo ""
  read -r -p "Elige opción [1/2/3] (Enter = ${REC_OPT}): " CHOICE
  CHOICE="${CHOICE:-${REC_OPT}}"

  case "${CHOICE}" in
    1)
      instalar_motor "${NAME_4B}" "${FILE_4B}" "~2.71 GB"
      ;;
    2)
      instalar_motor "${NAME_9B}" "${FILE_9B}" "~5.63 GB"
      ;;
    3)
      instalar_motor "${NAME_4B}" "${FILE_4B}" "~2.71 GB"
      instalar_motor "${NAME_9B}" "${FILE_9B}" "~5.63 GB"
      ;;
    *)
      echo "⚠️  Opción no reconocida; instalando recomendación [${REC_OPT}]..."
      if [ "${REC_OPT}" = "1" ]; then
        instalar_motor "${NAME_4B}" "${FILE_4B}" "~2.71 GB"
      else
        instalar_motor "${NAME_9B}" "${FILE_9B}" "~5.63 GB"
      fi
      ;;
  esac
else
  echo "✅ Motores PRISMA detectados en Ollama:"
  [ "${HAS_4B}" -eq 1 ] && echo "   • ${NAME_4B} (Qwen 3.5 4B)"
  [ "${HAS_9B}" -eq 1 ] && echo "   • ${NAME_9B} (Qwen 3.5 9B)"
  [ "${HAS_LEG}" -eq 1 ] && echo "   • ${NAME_LEGACY} (instalación previa)"
  echo "   (Tip: ejecuta 'bash install_and_run.sh --models' para instalar/actualizar otro motor)"
fi

# 7. Iniciar interfaz local de PRISMA™
echo ""
echo "🚀 Iniciando PRISMA™ en http://localhost:8501 ..."
exec python -m streamlit run app.py --browser.gatherUsageStats false
