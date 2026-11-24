#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

MODEL_DIR="models"
FILE_4B="PRISMA-Core-Qwen3.5-4B-HauhauCS-Q4_K_M.gguf"
FILE_9B="PRISMA-Core-Qwen3.5-9B-HauhauCS-Q4_K_M.gguf"
URL_4B="https://huggingface.co/vicstern/PRISMA-Models/resolve/main/${FILE_4B}"
URL_9B="https://huggingface.co/vicstern/PRISMA-Models/resolve/main/${FILE_9B}"
BASE_4B="prisma-engine-4b"
BASE_9B="prisma-engine-9b"

echo "============================================================"
echo "  Aula Viva® — PRISMA™ (Offline Edge-AI Installer & Launcher)"
echo "============================================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ Python 3 no encontrado. Instálalo desde https://www.python.org/downloads/"
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "❌ Ollama no encontrado. Instálalo desde https://ollama.com/download"
  exit 1
fi

if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "⏳ Iniciando servidor local de Ollama..."
  if [[ "$(uname)" == "Darwin" ]] && [ -d "/Applications/Ollama.app" ]; then
    open -a Ollama || true
  else
    nohup ollama serve >/dev/null 2>&1 &
  fi
  for _ in $(seq 1 15); do
    if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
fi

if [ ! -d ".venv" ]; then
  echo "📦 Creando entorno virtual aislado (.venv)..."
  python3 -m venv .venv
  echo "📦 Instalando dependencias de Python (incluye exportación .docx)..."
  .venv/bin/pip install --upgrade pip >/dev/null 2>&1 || true
  .venv/bin/pip install -r requirements.txt
else
  if ! .venv/bin/python -c "import docx" >/dev/null 2>&1; then
    echo "📦 Actualizando dependencias de Python..."
    .venv/bin/pip install -r requirements.txt
  fi
fi

detectar_ram_gb() {
  if [[ "$(uname)" == "Darwin" ]]; then
    local bytes
    bytes=$(sysctl -n hw.memsize 2>/dev/null || echo 8589934592)
    echo $(( (bytes + 536870912) / 1073741824 ))
  elif [ -r /proc/meminfo ]; then
    local kb
    kb=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
    echo $(( (kb + 524288) / 1048576 ))
  else
    echo 8
  fi
}

modelo_instalado() {
  ollama list 2>/dev/null | awk 'NR>1 {print $1}' | grep -q "^${1}:"
}

descargar_y_compilar_dual() {
  local base_name="$1"
  local file_name="$2"
  local url="$3"
  local size_lbl="$4"

  mkdir -p "${MODEL_DIR}"
  local full_path="${MODEL_DIR}/${file_name}"

  if [ ! -f "${full_path}" ]; then
    echo "⬇️  Descargando ${file_name} (${size_lbl}) desde vicstern/PRISMA-Models..."
    echo "   (Esta descarga solo ocurre una vez; después opera 100% offline.)"
    curl -L --fail --progress-bar -o "${full_path}.part" "${url}"
    mv "${full_path}.part" "${full_path}"
  else
    echo "📁 Archivo local encontrado: ${full_path}"
  fi

  local tmp_mf=".Modelfile.tmp"
  for lang_suf in es en; do
    local mf_src="Modelfile.${lang_suf}"
    if [ ! -f "${mf_src}" ]; then
      mf_src="Modelfile"
    fi
    local target="${base_name}-${lang_suf}"
    echo "Compilando motor local '${target}' en Ollama..."
    awk -v m="FROM ./${full_path}" 'NR==1{print m; next} {print}' "${mf_src}" > "${tmp_mf}"
    ollama create "${target}" -f "${tmp_mf}"
    rm -f "${tmp_mf}"
    echo "✅ Motor '${target}' listo."
  done
}

FORCE_MENU=0
if [[ "$1" == "--models" ]]; then
  FORCE_MENU=1
fi

HAS_4B=0
if modelo_instalado "${BASE_4B}-es" && modelo_instalado "${BASE_4B}-en"; then HAS_4B=1; fi
HAS_9B=0
if modelo_instalado "${BASE_9B}-es" && modelo_instalado "${BASE_9B}-en"; then HAS_9B=1; fi

if [[ ${FORCE_MENU} -eq 1 ]] || [[ ${HAS_4B} -eq 0 && ${HAS_9B} -eq 0 ]]; then
  RAM_GB=$(detectar_ram_gb)
  echo ""
  echo "🖥️  Memoria RAM detectada / Detected RAM: ${RAM_GB} GB"
  if [[ ${RAM_GB} -le 12 ]]; then
    REC="1"
    echo "💡 Recomendación / Recommended: [1] PRISMA 4B (~2.71 GB) — óptimo para ${RAM_GB} GB RAM"
  else
    REC="2"
    echo "💡 Recomendación / Recommended: [2] PRISMA 9B (~5.63 GB) — óptimo para ${RAM_GB} GB RAM"
  fi
  echo ""
  echo "Selecciona el motor local a instalar (compila ES + EN sin duplicar espacio):"
  echo "  [1] PRISMA 4B  (Qwen3.5-4B · ~2.71 GB)"
  echo "  [2] PRISMA 9B  (Qwen3.5-9B · ~5.63 GB)"
  echo "  [3] Ambos / Both (4B + 9B · ~8.34 GB)"
  echo ""
  read -r -p "Elige opción [1/2/3] (Enter = ${REC}): " CHOICE
  CHOICE="${CHOICE:-$REC}"

  case "${CHOICE}" in
    1) descargar_y_compilar_dual "${BASE_4B}" "${FILE_4B}" "${URL_4B}" "~2.71 GB" ;;
    2) descargar_y_compilar_dual "${BASE_9B}" "${FILE_9B}" "${URL_9B}" "~5.63 GB" ;;
    3)
      descargar_y_compilar_dual "${BASE_4B}" "${FILE_4B}" "${URL_4B}" "~2.71 GB"
      descargar_y_compilar_dual "${BASE_9B}" "${FILE_9B}" "${URL_9B}" "~5.63 GB"
      ;;
    *)
      echo "⚠️  Opción no válida. Usando recomendación automática (${REC})."
      if [[ "${REC}" == "1" ]]; then
        descargar_y_compilar_dual "${BASE_4B}" "${FILE_4B}" "${URL_4B}" "~2.71 GB"
      else
        descargar_y_compilar_dual "${BASE_9B}" "${FILE_9B}" "${URL_9B}" "~5.63 GB"
      fi
      ;;
  esac
fi

echo ""
echo "🚀 Iniciando PRISMA™ en http://localhost:8501 ..."
exec .venv/bin/streamlit run app.py
