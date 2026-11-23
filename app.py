import io
import json
import os
import platform
import re
import subprocess
from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches, Pt, RGBColor
    DOCX_DISPONIBLE = True
except ImportError:
    DOCX_DISPONIBLE = False


# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="PRISMA™",
    page_icon="🌌",
    layout="wide"
)

# --- RUTAS LOCALES PERSISTENTES (AIR-GAPPED) ---
DIR_APP_USER = os.path.expanduser("~/PRISMA_App")
DIR_EXPEDIENTES = os.path.join(DIR_APP_USER, "expedientes")
CONFIG_PATH = os.path.join(DIR_APP_USER, "config.json")
os.makedirs(DIR_EXPEDIENTES, exist_ok=True)


def cargar_config_local():
    default_cfg = {"lang": "en", "modelo_activo": ""}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                default_cfg.update({k: v for k, v in data.items() if k in default_cfg})
        except Exception:
            pass
    return default_cfg


def guardar_config_local(lang=None, modelo_activo=None):
    cfg = cargar_config_local()
    if lang is not None:
        cfg["lang"] = lang
    if modelo_activo is not None:
        cfg["modelo_activo"] = modelo_activo
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


def detectar_motores_ollama():
    """Consulta modelos PRISMA instalados en Ollama local (agrupando variantes -es/-en por tier)."""
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=2)
        if resp.status_code != 200:
            return [], set(), False
        modelos = [m.get("name", "") for m in resp.json().get("models", [])]
        raw_set = set()
        tiers = []
        for m in modelos:
            base = m.split(":")[0]
            if base.startswith("prisma"):
                raw_set.add(base)
                tier = re.sub(r"-(es|en)$", "", base)
                if tier not in tiers:
                    tiers.append(tier)
        candidatos = []
        for p in ("prisma-engine-9b", "prisma-engine-4b", "prisma-engine"):
            if p in tiers:
                candidatos.append(p)
        for tier in tiers:
            if tier not in candidatos:
                candidatos.append(tier)
        return candidatos, raw_set, True
    except Exception:
        return [], set(), False


def resolver_modelo_ollama(base_key, lang="es"):
    """Enruta al motor compilado nativo del idioma activo (-es / -en) con respaldo seguro."""
    preferido = f"{base_key}-{lang}"
    if preferido in MODELOS_OLLAMA_RAW:
        return preferido
    if base_key in MODELOS_OLLAMA_RAW:
        return base_key
    otro = f"{base_key}-{'en' if lang == 'es' else 'es'}"
    if otro in MODELOS_OLLAMA_RAW:
        return otro
    return preferido



PRISMA_ENGINE_CATALOG = {
    "prisma-engine-4b": {
        "short": "PRISMA 4B",
        "ram_es": "8 GB de RAM",
        "ram_en": "8 GB RAM",
        "size": "~2.71 GB",
        "min_ram": 8,
        "file": "Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf",
        "url": "https://huggingface.co/vicstern/PRISMA-Models/resolve/main/Qwen3.5-4B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf",
    },
    "prisma-engine-9b": {
        "short": "PRISMA 9B",
        "ram_es": "16+ GB de RAM",
        "ram_en": "16+ GB RAM",
        "size": "~5.63 GB",
        "min_ram": 14,
        "file": "Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf",
        "url": "https://huggingface.co/vicstern/PRISMA-Models/resolve/main/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive-Q4_K_M.gguf",
    },
}

PRISMA_SVG_ICON = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke-linecap="round" '
    'stroke-linejoin="round" style="vertical-align:-4px;margin-right:7px;">'
    '<line x1="1.5" y1="14" x2="9.2" y2="11.2" stroke="currentColor" stroke-width="1.8"/>'
    '<line x1="14" y1="9.8" x2="22.5" y2="6.2" stroke="#c084fc" stroke-width="1.6"/>'
    '<line x1="14.6" y1="11.2" x2="22.5" y2="9.6" stroke="#38bdf8" stroke-width="1.6"/>'
    '<line x1="15.2" y1="12.6" x2="22.5" y2="13.1" stroke="#4ade80" stroke-width="1.6"/>'
    '<line x1="15.8" y1="14" x2="22.5" y2="16.4" stroke="#facc15" stroke-width="1.6"/>'
    '<line x1="16.3" y1="15.4" x2="22.5" y2="19.5" stroke="#f87171" stroke-width="1.6"/>'
    '<polygon points="12,3.2 20.5,19.5 3.5,19.5" stroke="currentColor" stroke-width="1.7" fill="none"/>'
    '</svg>'
)


def detectar_ram_gb_local():
    try:
        sys_name = platform.system()
        if sys_name == "Darwin":
            out = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            return max(1, round(int(out) / (1024 ** 3)))
        if sys_name == "Linux" and os.path.exists("/proc/meminfo"):
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        return max(1, round(int(line.split()[1]) / (1024 ** 2)))
        if sys_name == "Windows":
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return max(1, round(stat.ullTotalPhys / (1024 ** 3)))
    except Exception:
        pass
    return 8


def instalar_motor_desde_app(model_key, progress_bar, status_box, lang="es"):
    meta = PRISMA_ENGINE_CATALOG[model_key]
    app_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(app_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    model_path = os.path.join(models_dir, meta["file"])
    part_path = model_path + ".part"
    modelfile_src = os.path.join(app_dir, "Modelfile")
    tmp_mf = os.path.join(app_dir, ".Modelfile.tmp")

    if not os.path.exists(model_path):
        status_box.info(
            f"Descargando {meta['short']} ({meta['size']})..."
            if lang == "es" else f"Downloading {meta['short']} ({meta['size']})..."
        )
        with requests.get(meta["url"], stream=True, timeout=30) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(part_path, "wb") as out_f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        out_f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            progress_bar.progress(min(0.88, (downloaded / total) * 0.88))
        os.replace(part_path, model_path)
    else:
        progress_bar.progress(0.88)

    for idx_l, suf in enumerate(("es", "en")):
        mf_path = os.path.join(app_dir, f"Modelfile.{suf}")
        if not os.path.exists(mf_path):
            mf_path = modelfile_src
        target_name = f"{model_key}-{suf}"
        status_box.info(
            f"Compilando {meta['short']} ({suf.upper()}) en tu equipo..."
            if lang == "es" else f"Compiling {meta['short']} ({suf.upper()}) on your device..."
        )
        with open(mf_path, "r", encoding="utf-8") as mf:
            lines = mf.readlines()
        lines[0] = f"FROM ./models/{meta['file']}\n"
        with open(tmp_mf, "w", encoding="utf-8") as mf_out:
            mf_out.writelines(lines)
        try:
            subprocess.run(["ollama", "create", target_name, "-f", tmp_mf], cwd=app_dir, check=True, capture_output=True, text=True)
        finally:
            if os.path.exists(tmp_mf):
                os.remove(tmp_mf)
        progress_bar.progress(0.94 if idx_l == 0 else 1.0)


# --- CARGAR PREFERENCIAS PERSISTENTES ANTES DE INICIALIZAR WIDGETS ---
_cfg_inicial = cargar_config_local()
if "lang" not in st.session_state:
    st.session_state.lang = _cfg_inicial.get("lang", "en")
if st.session_state.lang not in ("es", "en"):
    st.session_state.lang = "en"

MOTORES_INSTALADOS, MODELOS_OLLAMA_RAW, OLLAMA_ONLINE = detectar_motores_ollama()
if "modelo_activo" not in st.session_state:
    guardado = _cfg_inicial.get("modelo_activo", "")
    if guardado and guardado in MOTORES_INSTALADOS:
        st.session_state.modelo_activo = guardado
    elif MOTORES_INSTALADOS:
        st.session_state.modelo_activo = MOTORES_INSTALADOS[0]
    else:
        st.session_state.modelo_activo = guardado or "prisma-engine-4b"
elif MOTORES_INSTALADOS and st.session_state.modelo_activo not in MOTORES_INSTALADOS:
    st.session_state.modelo_activo = MOTORES_INSTALADOS[0]


# --- DICCIONARIO BILINGÜE (ES / EN) ---
TEXTS = {
    "es": {
        "app_title": "Aula Viva® con IA",
        "app_subtitle": "### Analítica cualitativa vectorizada en ℝ⁸ | Ecosistema ASPIRE® — PRISMA™",
        "app_caption": "Plataforma de Reflexión e Interpretación para el Seguimiento Multidimensional del Aprendizaje | SSRN DOI: 10.2139/ssrn.7310080",
        "app_quote": "«Hacer brillar luz blanca a través de cada estudiante y proyectar sus colores refractados para revelar el profundo camino de su crecimiento.»",
        "sidebar_header": "⚙️ Gestión y entorno",
        "lang_label": "🌐 Idioma / Language:",
        "engine_header": "Motor local",
        "engine_select": "Motor PRISMA activo:",
        "engine_offline": "⚠️ El motor local no responde en `localhost:11434`. Inicia Ollama para procesar notas.",
        "engine_none": "⚠️ No hay un motor PRISMA instalado todavía. Selecciónalo abajo para instalarlo.",
        "engine_ready": "Listo",
        "engine_missing": "No instalado",
        "engine_install_prompt": "Este motor aún no está instalado en tu equipo (RAM detectada: **{ram} GB**). Puedes instalarlo ahora con conexión a internet; después operará 100 % sin conexión.",
        "engine_ram_warn": "Tu equipo tiene **{ram} GB de RAM**. PRISMA 9B funciona mejor con 16+ GB y puede responder más lento aquí; PRISMA 4B es la opción óptima para tu equipo.",
        "engine_install_btn": "⬇️ Descargar e instalar {name} ({size})",
        "engine_install_ok": "✅ {name} instalado y activado.",
        "engine_install_err": "⚠️ No se pudo completar la instalación (verifica conexión a internet y Ollama):",
        "lang_matrix_title": "🌍 Lenguas compatibles",
        "lang_matrix_body": (
            "**Idiomas PRISMA™ (interfaz, entrada y salida nativa):** Español, Inglés.\n\n"
            "**Soporte nativo local para notas (Qwen 3.5 · 4B / 9B):**\n"
            "- **Óptimo:** Español, Inglés, Francés, Portugués, Alemán, Italiano, Chino, Japonés, Coreano, Árabe.\n"
            "- **Funcional (mejor en 9B):** Catalán, Gallego, Euskera, Ruso, Hindi, Turco, Holandés.\n\n"
            "**Otras lenguas (indígenas, regionales o con menor presencia digital):**\n"
            "Por favor, traduce tus notas localmente sin subir datos a la nube antes de ingresarlas a PRISMA™ usando herramientas sin conexión como:\n"
            "- **Firefox Translations (Bergamot):** Traducción local integrada en el navegador.\n"
            "- **Argos Translate / LibreTranslate (local):** Motor abierto 100 % aislado.\n"
            "- **Meta NLLB-200 (local):** Cobertura para más de 200 lenguas (incl. guaraní, quechua, aymara, maya y náhuatl en modelos comunitarios)."
        ),
        "scope_notice": "<strong>Alcance pedagógico:</strong> PRISMA™ es estrictamente un instrumento educativo de reflexión y analítica formativa diseñado para potenciar el aprendizaje y la calidad de la educación. No es una herramienta médica ni de diagnóstico clínico o psicológico, ni sustituye la valoración de profesionales de la salud.",
        "footer_brand": "Aula Viva® · Grupo SiEFH · aulaviva.lat · Código abierto",
        "wf_header": "1. Flujo de trabajo",
        "btn_reset": "✨ Reiniciar pantalla de registro",
        "load_header": "2. Cargar expediente (.json)",
        "load_uploader": "Selecciona expediente JSON:",
        "load_help": "Carga de expedientes históricos (compatibles ES/EN).",
        "btn_load": "📥 Cargar expediente",
        "load_ok": "Expediente cargado correctamente.",
        "load_err": "Error al leer el archivo JSON:",
        "export_sidebar_btn": "💾 Exportar expediente (.json)",
        "export_sidebar_dl": "⬇️ Descargar archivo generado",
        "admin_header": "🔒 Herramientas de administrador",
        "admin_key_label": "🔑 Clave de administrador:",
        "admin_key_ph": "Ingresa clave de acceso",
        "admin_key_help": "Habilita la transición de cierre de ciclo escolar.",
        "admin_ok": "Acceso concedido — Modo Administrador",
        "admin_logout": "🔴 Salir del modo administrador",
        "admin_locked": "Funciones avanzadas reservadas para Admin",
        "tabula_label": "Cierre de ciclo escolar",
        "tabula_caption": "Congela el ciclo actual en un JSON de cierre y restablece el vector a 0.0 dB registrando la transición.",
        "tabula_cycle": "Identificador del ciclo a cerrar:",
        "tabula_help": "Ejemplos: 2026-1, 2026-2, 2025-2026",
        "tabula_btn": "🔄 Ejecutar cierre de ciclo",
        "tabula_ok": "Transición registrada y ciclo congelado en `{fn}`. Vector restablecido a 0.0 dB.",
        "sec1_title": "1. Ficha del estudiante y registro",
        "lbl_name": "Nombre del estudiante (obligatorio):",
        "ph_name": "Ej: María López",
        "lbl_id": "Matrícula / ID:",
        "ph_id": "Ej: A012345",
        "lbl_group": "Grupo:",
        "ph_group": "Ej: 2° B",
        "lbl_level": "Nivel educativo (obligatorio para contextualizar zona de desarrollo):",
        "lbl_subject": "Asignatura / Espacio:",
        "ph_subject": "Ej: Matemáticas / Laboratorio",
        "sec2_title": "2. Registro de estado de educabilidad",
        "sec2_caption": "Condición sociofisiológica y bioemocional basal (protección no punitiva):",
        "lbl_sleep": "Sueño / descanso:",
        "lbl_food": "Alimentación / nutrición:",
        "lbl_well": "Bienestar integral:",
        "sec3_title": "3. Registro de nota narrativa docente",
        "lbl_note": "Dictado / nota narrativa del docente:",
        "ph_note": "Describe los hechos y acciones observadas en el aula. Presiona Cmd+Enter o Ctrl+Enter para procesar.",
        "btn_analyze": "⚡ Ejecutar análisis de nota",
        "btn_analyzing": "⏳ Procesando inferencia...",
        "err_no_name": "⚠️ Por favor ingresa el nombre del estudiante antes de continuar.",
        "err_no_level": "⚠️ Por favor selecciona el nivel educativo del estudiante (candado de zona de desarrollo).",
        "err_no_note": "⚠️ Por favor ingresa una nota de observación docente.",
        "spinner_note": "Procesando inferencia cualitativa en ℝ⁸ con {model}...",
        "debug_raw": "🔬 Respuesta cruda de Ollama (Debug)",
        "staging_title": "#### 🔍 Previsualización del análisis de la IA",
        "staging_caption": "Revisa los deltas propuestos en el mapa vectorial. Si deseas calibrar algún eje, ajústalo en la Sección 4 justo debajo: tu ajuste se sumará en vivo sobre esta propuesta.",
        "crit_title": "🚨 **ALERTA DE RIESGO VITAL ACTIVA (ROJO CRÍTICO)**",
        "crit_body": "El motor PRISMA™ ha suspendido la evaluación pedagógica (0.0 dB en todos los ejes). La narrativa sugiere riesgo inminente.",
        "crit_action": "👉 **Acción requerida:** Contención y acompañamiento físico/emocional urgente del estudiante. Activar protocolo institucional y canalización profesional de inmediato.",
        "btn_crit_log": "🚨 Registrar alerta crítica en expediente (0.0 dB)",
        "btn_crit_discard": "❌ Descartar y limpiar",
        "sem_red": "🔴 **Semáforo ROJO — Alerta de Educabilidad:**",
        "sem_yellow": "🟡 **Semáforo AMARILLO — Atención Pedagógica:**",
        "sem_green": "🟢 **Semáforo VERDE — Condición Óptima:**",
        "sem_green_default": "Sin restricciones sociofisiológicas activas.",
        "btn_accept": "✅ Aceptar y Registrar Hito",
        "btn_adjust": "🎨 Ajustar Manualmente",
        "btn_reject": "❌ Rechazar análisis",
        "sec4_title": "5. Meta-análisis de trayectoria",
        "sec4_caption": "Evaluación holística multidimensional a partir de los hitos acumulados.",
        "btn_meta": "🌌 Ejecutar Meta-análisis PRISMA™",
        "err_meta_min": "⚠️ Se requieren al menos 2 hitos acumulados para realizar un Meta-análisis de trayectoria.",
        "spinner_meta": "Analizando trayectoria multidimensional integral en ℝ⁸ ({model})...",
        "meta_card_title": "#### 🌌 Diagnóstico holístico sugerido por PRISMA™",
        "btn_meta_accept": "✅ Aceptar y registrar Meta-análisis como hito",
        "btn_meta_discard": "❌ Descartar Meta-análisis",
        "sec5_title": "6. Reporte oficial",
        "sec5_caption": "Traduce el expediente acumulado del estudiante al formato oficial del sistema educativo para reducir la carga administrativa docente.",
        "lbl_framework": "Sistema / Marco curricular oficial:",
        "lbl_period": "Periodo / Corte evaluativo (opcional):",
        "ph_period": "Ej: Trimestre 1 · 2026-2027",
        "lbl_custom_fw": "Competencias o criterios institucionales personalizados:",
        "ph_custom_fw": "Escribe los campos, rúbricas o atributos de egreso que solicita tu institución...",
        "btn_gen_report": "📝 Generar reporte oficial",
        "err_report_min": "⚠️ Registra o carga al menos 1 hito en el expediente para generar el reporte oficial.",
        "err_custom_empty": "⚠️ Especifica los criterios de tu marco personalizado antes de generar el reporte.",
        "spinner_report": "Redactando síntesis curricular alineada a {fw} ({model})...",
        "report_ready_title": "#### 📄 Reporte oficial listo para validar",
        "report_copy_label": "Texto limpio listo para copiar y pegar en tu plataforma escolar (editable):",
        "btn_dl_docx": "📥 Descargar reporte en Word (.docx)",
        "docx_missing": "Instala `python-docx` (`pip install python-docx`) para habilitar la descarga en Word.",
        "btn_clear_report": "🗑️ Limpiar reporte",
        "hist_title": "📋 Historial de hitos acumulados",
        "tag_ia": "🌌 Inferencia PRISMA™",
        "tag_manual": "🎨 Calibración manual docente",
        "tag_meta": "🌌 Meta-análisis PRISMA™",
        "tag_crit": "🚨 Alerta crítica registrada (0.0 dB)",
        "tag_tabula": "🔄 Cierre de ciclo",
        "hist_note_lbl": "**Nota narrativa docente:**",
        "hist_breakdown": "**Desglose e Inferencia de PRISMA™:**",
        "hist_no_deltas": "ℹ️ *El motor PRISMA™ no detectó evidencias para aplicar deltas en este hito.*",
        "hist_manual_lbl": "**Razonamiento pedagógico docente:**",
        "hist_direct_adj": "Ajuste directo",
        "hist_trans_lbl": "**Registro de transición:**",
        "sec6_title": "4. Calibración manual docente (dB)",
        "sec6_caption": "Si hay un análisis de PRISMA™ pendiente arriba, tus ajustes se suman en vivo sobre esa propuesta y ambos se registran en orden al confirmar.",
        "lbl_justif": "Razonamiento / Justificación pedagógica del ajuste (Obligatorio):",
        "ph_justif": "Ejemplo: Incremento en Razonamiento ético tras observar la mediación espontánea del estudiante.",
        "btn_prev_manual": "👁️ Previsualizar calibración manual en el mapa",
        "err_manual_zero": "⚠️ Ajusta al menos un valor diferente de 0.0 dB para previsualizar.",
        "err_manual_justif": "⚠️ Ingresa el razonamiento pedagógico para justificar el ajuste manual.",
        "manual_card_title": "#### 🎨 Previsualización de calibración manual",
        "manual_card_caption": "Verifica la proyección punteada morada en el mapa visual a la derecha.",
        "manual_justif_lbl": "**Justificación registrada:**",
        "btn_manual_confirm": "🎨 Confirmar y registrar calibración",
        "btn_manual_cancel": "❌ Cancelar previsualización",
        "radar_header": "Espejo metacognitivo — Espacio vectorial ℝ⁸",
        "vis_all": "Trayectoria completa",
        "vis_custom": "Personalizada",
        "hist_chk": "Trayectoria histórica",
        "hist_chk_help": "Habilitado para Administrador tras ejecutar Cierre de Ciclo.",
        "radar_map_title": "Mapa Visual de Crecimiento",
        "radar_subtitle_default": "Evaluación Formativa Integral",
        "radar_multiselect": "Superponer hitos para comparativa:",
        "radar_current": "Estado actual",
        "radar_prev_ia": "Previsualización IA",
        "radar_prev_man": "Previsualización manual",
        "orb_0": "0 dB (Línea base: 1x)",
        "orb_6": "+6 dB (Principiante: 2x)",
        "orb_12": "+12 dB (Intermedio: 4x)",
        "orb_18": "+18 dB (Avanzado: 8x)",
        "orb_24": "+24 dB (Experto: 16x)",
        "modal_save_title": "💾 Resguardo de expediente vectorial",
        "modal_save_body": "Se ha consolidado el hito en el expediente de **{name}**.",
        "modal_save_cap": "El expediente ya quedó resguardado localmente en `~/PRISMA_App/expedientes/`. Puedes descargar una copia extra si lo deseas:",
        "modal_save_dl": "💾 Descargar copia (.json)",
        "modal_save_cont": "Continuar ➔",
        "modal_reset_title": "⚠️ Confirmar reinicio de pantalla",
        "modal_reset_body": "Hay hitos activos en pantalla que aún no has descargado como copia extra.",
        "modal_reset_ask": "¿Deseas descargar el expediente `.json` antes de limpiar?",
        "modal_reset_dl": "💾 Descargar resguardo (.json) y limpiar",
        "modal_reset_force": "🗑️ Limpiar sin descargar",
        "modal_cancel": "Cancelar",
        "docx_footer": "Síntesis formativa asistida por PRISMA™ · Aula Viva® (aulaviva.lat) — Analítica cualitativa local en ℝ⁸. Validado por la persona docente.",
        "docx_doc_title": "Reporte Formativo Oficial",
        "docx_vec_title": "Resumen cuantitativo de apoyo — Espacio Vectorial ℝ⁸ (escala logarítmica dB)",
    },
    "en": {
        "app_title": "Aula Viva® with AI",
        "app_subtitle": "### Vectorized Qualitative Learning Analytics in ℝ⁸ | ASPIRE® — PRISMA™ Ecosystem",
        "app_caption": "Platform for Reflection, Interpretation, and Synthesis in Multidimensional Assessment | SSRN DOI: 10.2139/ssrn.7310080",
        "app_quote": "“Shining white light through learners and projecting its refracted colors to reveal the profound journey of their growth.”",
        "sidebar_header": "⚙️ Workspace & Engine",
        "lang_label": "🌐 Language / Idioma:",
        "engine_header": "Local Engine",
        "engine_select": "Active PRISMA Engine:",
        "engine_offline": "⚠️ Local engine is not responding at `localhost:11434`. Start Ollama to process notes.",
        "engine_none": "⚠️ No PRISMA engine is installed yet. Select one below to install it.",
        "engine_ready": "Ready",
        "engine_missing": "Not installed",
        "engine_install_prompt": "This engine is not installed on your device yet (detected RAM: **{ram} GB**). You can download and install it now; after that it runs 100% offline.",
        "engine_ram_warn": "Your device has **{ram} GB RAM**. PRISMA 9B works best on 16+ GB and may run slower here; PRISMA 4B is the recommended option for your hardware.",
        "engine_install_btn": "⬇️ Download & install {name} ({size})",
        "engine_install_ok": "✅ {name} installed and activated.",
        "engine_install_err": "⚠️ Installation could not be completed (check internet connection and Ollama):",
        "lang_matrix_title": "🌍 Supported languages",
        "lang_matrix_body": (
            "**PRISMA™ Languages (native interface, input & output):** English, Spanish.\n\n"
            "**Native local note support (Qwen 3.5 · 4B / 9B):**\n"
            "- **Optimal:** English, Spanish, French, Portuguese, German, Italian, Chinese, Japanese, Korean, Arabic.\n"
            "- **Functional (stronger on 9B):** Catalan, Galician, Basque, Russian, Hindi, Turkish, Dutch.\n\n"
            "**Other languages (indigenous, regional, or with limited digital representation):**\n"
            "Please translate classroom notes locally without cloud uploads before entering them into PRISMA™ using offline tools such as:\n"
            "- **Firefox Translations (Bergamot):** Built-in local browser translation.\n"
            "- **Argos Translate / LibreTranslate (local):** Open-source air-gapped engine.\n"
            "- **Meta NLLB-200 (local):** Supports 200+ languages (including Quechua, Guarani, Aymara, and community Maya/Nahuatl models)."
        ),
        "scope_notice": "<strong>Pedagogical scope notice:</strong> PRISMA™ is strictly an educational reflection and learning-analytics instrument designed to strengthen teaching quality and holistic student growth. It is not a medical, clinical, or psychological diagnostic tool, nor a substitute for qualified healthcare or mental-health professionals.",
        "footer_brand": "Aula Viva® · Grupo SiEFH · aulaviva.lat · Open source",
        "wf_header": "1. Workflow",
        "btn_reset": "✨ Reset workspace",
        "load_header": "2. Load student record (.json)",
        "load_uploader": "Select JSON record:",
        "load_help": "Loads longitudinal student records (ES/EN compatible).",
        "btn_load": "📥 Load record",
        "load_ok": "Student record loaded successfully.",
        "load_err": "Error reading JSON file:",
        "export_sidebar_btn": "💾 Export record (.json)",
        "export_sidebar_dl": "⬇️ Download generated file",
        "admin_header": "🔒 Administrator Tools",
        "admin_key_label": "🔑 Admin passphrase:",
        "admin_key_ph": "Enter access key",
        "admin_key_help": "Unlocks end-of-cycle transition (Tabula Rasa).",
        "admin_ok": "Access granted — Admin Mode",
        "admin_logout": "🔴 Exit Admin Mode",
        "admin_locked": "Advanced functions reserved for Admin",
        "tabula_label": "End-of-cycle archive",
        "tabula_caption": "Freezes the active cycle into an immutable archive JSON and resets the vector to 0.0 dB.",
        "tabula_cycle": "Academic cycle identifier:",
        "tabula_help": "Examples: 2026-1, 2026-2, 2025-2026",
        "tabula_btn": "🔄 Execute cycle closure",
        "tabula_ok": "Transition logged and cycle archived to `{fn}`. Vector reset to 0.0 dB.",
        "sec1_title": "1. Student Profile & Record",
        "lbl_name": "Student Name (required):",
        "ph_name": "e.g., Maria Lopez",
        "lbl_id": "Student ID:",
        "ph_id": "e.g., A012345",
        "lbl_group": "Group / Section:",
        "ph_group": "e.g., Grade 8B",
        "lbl_level": "Educational Level (required to anchor Zone of Proximal Development):",
        "lbl_subject": "Subject / Learning Space:",
        "ph_subject": "e.g., Physics / Workshop",
        "sec2_title": "2. State of Educability Check",
        "sec2_caption": "Biopsychosocial baseline (non-punitive safeguard):",
        "lbl_sleep": "Sleep / rest:",
        "lbl_food": "Food / nutrition:",
        "lbl_well": "Holistic well-being:",
        "sec3_title": "3. Teacher Narrative Observation",
        "lbl_note": "Dictation / classroom narrative note:",
        "ph_note": "Describe concrete facts and actions observed in class. Press Cmd+Enter or Ctrl+Enter to analyze.",
        "btn_analyze": "⚡ Run qualitative analysis",
        "btn_analyzing": "⏳ Processing inference...",
        "err_no_name": "⚠️ Please enter the student's name before continuing.",
        "err_no_level": "⚠️ Please select the educational level (ZPD calibration lock).",
        "err_no_note": "⚠️ Please enter a narrative observation note.",
        "spinner_note": "Processing qualitative inference in ℝ⁸ with {model}...",
        "debug_raw": "🔬 Raw Ollama Output (Debug)",
        "staging_title": "#### 🔍 AI Analysis Preview",
        "staging_caption": "Review proposed deltas on the vector map. To calibrate any axis, adjust it in Section 4 directly below: your adjustment will sum live on top of this proposal.",
        "crit_title": "🚨 **CRITICAL SAFETY ALERT ACTIVE (ROJO CRÍTICO)**",
        "crit_body": "PRISMA™ has suspended pedagogical scoring (0.0 dB across all axes). The narrative indicates potential imminent risk.",
        "crit_action": "👉 **Required action:** Provide immediate human care and containment. Trigger institutional safeguarding protocol and professional intervention immediately.",
        "btn_crit_log": "🚨 Log critical alert in record (0.0 dB)",
        "btn_crit_discard": "❌ Discard and clear",
        "sem_red": "🔴 **RED Traffic Light — Educability Alert:**",
        "sem_yellow": "🟡 **YELLOW Traffic Light — Pedagogical Care:**",
        "sem_green": "🟢 **GREEN Traffic Light — Stable Baseline:**",
        "sem_green_default": "No active biopsychosocial constraints.",
        "btn_accept": "✅ Accept & Register Milestone",
        "btn_adjust": "🎨 Adjust Manually",
        "btn_reject": "❌ Reject Analysis",
        "sec4_title": "5. Longitudinal Meta-Analysis",
        "sec4_caption": "Holistic multidimensional synthesis across accumulated milestones.",
        "btn_meta": "🌌 Run PRISMA™ Meta-Analysis",
        "err_meta_min": "⚠️ At least 2 accumulated milestones are required to run a trajectory Meta-Analysis.",
        "spinner_meta": "Analyzing longitudinal trajectory in ℝ⁸ ({model})...",
        "meta_card_title": "#### 🌌 Holistic Diagnosis Suggested by PRISMA™",
        "btn_meta_accept": "✅ Accept & Register Meta-Analysis",
        "btn_meta_discard": "❌ Discard Meta-Analysis",
        "sec5_title": "6. Official Report",
        "sec5_caption": "Translates the student's accumulated record into your official educational framework to eliminate double-work reporting.",
        "lbl_framework": "Official Educational Framework:",
        "lbl_period": "Term / Reporting Period (optional):",
        "ph_period": "e.g., Term 1 · 2026-2027",
        "lbl_custom_fw": "Custom institutional competencies or criteria:",
        "ph_custom_fw": "Enter your school's exit profile, rubric domains, or reporting criteria...",
        "btn_gen_report": "📝 Generate Official Report",
        "err_report_min": "⚠️ Register or load at least 1 milestone to generate an official report.",
        "err_custom_empty": "⚠️ Please specify your custom framework criteria before generating.",
        "spinner_report": "Drafting curricular synthesis aligned to {fw} ({model})...",
        "report_ready_title": "#### 📄 Official Report Ready for Educator Review",
        "report_copy_label": "Clean text ready to copy & paste into your school portal (editable):",
        "btn_dl_docx": "📥 Download Word Report (.docx)",
        "docx_missing": "Install `python-docx` (`pip install python-docx`) to enable Word export.",
        "btn_clear_report": "🗑️ Clear report",
        "hist_title": "📋 Accumulated Milestones History",
        "tag_ia": "🌌 PRISMA™ Inference",
        "tag_manual": "🎨 Manual Educator Calibration",
        "tag_meta": "🌌 PRISMA™ Meta-Analysis",
        "tag_crit": "🚨 Critical Alert Logged (0.0 dB)",
        "tag_tabula": "🔄 Cycle Closure",
        "hist_note_lbl": "**Teacher narrative note:**",
        "hist_breakdown": "**PRISMA™ Breakdown & Inference:**",
        "hist_no_deltas": "ℹ️ *PRISMA™ detected no factual evidence requiring deltas in this milestone.*",
        "hist_manual_lbl": "**Educator pedagogical rationale:**",
        "hist_direct_adj": "Direct adjustment",
        "hist_trans_lbl": "**Transition record:**",
        "sec6_title": "4. Manual Educator Calibration (dB)",
        "sec6_caption": "When a PRISMA™ analysis is pending above, your adjustments sum live on top of it and both register in order upon confirmation.",
        "lbl_justif": "Pedagogical Rationale / Justification (Required):",
        "ph_justif": "Example: Increase in Ethical Reasoning after spontaneous peer mediation during lab work.",
        "btn_prev_manual": "👁️ Preview manual calibration on map",
        "err_manual_zero": "⚠️ Adjust at least one axis away from 0.0 dB to preview.",
        "err_manual_justif": "⚠️ Please enter a pedagogical justification for this manual adjustment.",
        "manual_card_title": "#### 🎨 Manual Calibration Preview",
        "manual_card_caption": "Check the dashed purple projection on the vector map to the right.",
        "manual_justif_lbl": "**Recorded justification:**",
        "btn_manual_confirm": "🎨 Confirm & Register Calibration",
        "btn_manual_cancel": "❌ Cancel preview",
        "radar_header": "Metacognitive Mirror — Vector Space ℝ⁸",
        "vis_all": "Full trajectory",
        "vis_custom": "Custom",
        "hist_chk": "Historical trajectory",
        "hist_chk_help": "Unlocked for Admin after executing an end-of-cycle archive.",
        "radar_map_title": "Visual Growth Map",
        "radar_subtitle_default": "Holistic Formative Assessment",
        "radar_multiselect": "Overlay milestones to compare:",
        "radar_current": "Current state",
        "radar_prev_ia": "AI preview",
        "radar_prev_man": "Manual preview",
        "orb_0": "0 dB (Baseline: 1x)",
        "orb_6": "+6 dB (Novice: 2x)",
        "orb_12": "+12 dB (Intermediate: 4x)",
        "orb_18": "+18 dB (Advanced: 8x)",
        "orb_24": "+24 dB (Expert: 16x)",
        "modal_save_title": "💾 Vector Record Backup",
        "modal_save_body": "Milestone consolidated in **{name}**'s record.",
        "modal_save_cap": "Your record is already safely stored on disk (`~/PRISMA_App/expedientes/`). You may download an extra copy below:",
        "modal_save_dl": "💾 Download copy (.json)",
        "modal_save_cont": "Continue ➔",
        "modal_reset_title": "⚠️ Confirm Workspace Reset",
        "modal_reset_body": "There are active milestones on screen that have not been downloaded as an extra copy yet.",
        "modal_reset_ask": "Would you like to download the `.json` backup before clearing?",
        "modal_reset_dl": "💾 Download backup (.json) & reset",
        "modal_reset_force": "🗑️ Clear without downloading",
        "modal_cancel": "Cancel",
        "docx_footer": "Formative synthesis assisted by PRISMA™ · Aula Viva® (aulaviva.lat) — Local qualitative analytics in ℝ⁸. Educator-validated.",
        "docx_doc_title": "Official Formative Report",
        "docx_vec_title": "Supporting Quantitative Summary — ℝ⁸ Vector Space (logarithmic dB scale)",
    }
}


def t(key):
    return TEXTS[st.session_state.lang].get(key, key)


# --- CLAVES CANÓNICAS (GARANTIZAN COMPATIBILIDAD TOTAL DE JSON ENTRE ES Y EN) ---
MAPEO_EJES = {
    "Indagacion_Investigacion": "Indagación e investigación",
    "Pensamiento_Critico_Analitico": "Pensamiento crítico y analítico",
    "Razonamiento_Etico": "Razonamiento ético",
    "Agencia_Intercultural": "Agencia intercultural",
    "Liderazgo_Colaborativo": "Liderazgo colaborativo",
    "Saber_Hacer_Ejecucion_Tecnica": "Saber hacer y ejecución técnica",
    "Resiliencia_Autogestion": "Resiliencia y autogestión",
    "Reflexion_Metacognitiva": "Reflexión metacognitiva"
}

EJE_NOMBRES = list(MAPEO_EJES.values())

EJES_DISPLAY = {
    "es": {eje: eje for eje in EJE_NOMBRES},
    "en": {
        "Indagación e investigación": "Inquiry & Research",
        "Pensamiento crítico y analítico": "Critical & Analytical Thinking",
        "Razonamiento ético": "Ethical Reasoning",
        "Agencia intercultural": "Intercultural Agency",
        "Liderazgo colaborativo": "Collaborative Leadership",
        "Saber hacer y ejecución técnica": "Practical & Technical Mastery",
        "Resiliencia y autogestión": "Resilience & Self-Management",
        "Reflexión metacognitiva": "Metacognitive Reflection",
    }
}

FORMATO_EJES_RADAR = {
    "es": {
        "Indagación e investigación": "Indagación e<br>investigación",
        "Pensamiento crítico y analítico": "Pensamiento crítico<br>y analítico",
        "Razonamiento ético": "Razonamiento<br>ético",
        "Agencia intercultural": "Agencia<br>intercultural",
        "Liderazgo colaborativo": "Liderazgo<br>colaborativo",
        "Saber hacer y ejecución técnica": "Saber hacer y<br>ejecución técnica",
        "Resiliencia y autogestión": "Resiliencia y<br>autogestión",
        "Reflexión metacognitiva": "Reflexión<br>metacognitiva"
    },
    "en": {
        "Indagación e investigación": "Inquiry &<br>Research",
        "Pensamiento crítico y analítico": "Critical &<br>Analytical Thinking",
        "Razonamiento ético": "Ethical<br>Reasoning",
        "Agencia intercultural": "Intercultural<br>Agency",
        "Liderazgo colaborativo": "Collaborative<br>Leadership",
        "Saber hacer y ejecución técnica": "Practical &<br>Technical Mastery",
        "Resiliencia y autogestión": "Resilience &<br>Self-Management",
        "Reflexión metacognitiva": "Metacognitive<br>Reflection"
    }
}

NIVELES_CANON = [
    "-- Selecciona el nivel educativo --",
    "Educación Inicial / Preescolar (Maternal / Kínder)",
    "Educación Primaria",
    "Educación Secundaria",
    "Educación Media Superior (Bachillerato / Prepa)",
    "Educación Superior (Licenciatura / Ingeniería)",
    "Posgrado (Especialidad / Maestría / Doctorado)",
    "Formación Continua / No Formal"
]

NIVELES_DISPLAY = {
    "es": {n: n for n in NIVELES_CANON},
    "en": {
        NIVELES_CANON[0]: "-- Select educational level --",
        NIVELES_CANON[1]: "Early Childhood / Preschool",
        NIVELES_CANON[2]: "Primary / Elementary School",
        NIVELES_CANON[3]: "Lower Secondary / Middle School",
        NIVELES_CANON[4]: "Upper Secondary / High School (IB DP / A-Levels)",
        NIVELES_CANON[5]: "Higher Education (Undergraduate)",
        NIVELES_CANON[6]: "Postgraduate (Master's / Doctorate)",
        NIVELES_CANON[7]: "Continuing / Non-Formal Education",
    }
}

OPCIONES_SUENO_CANON = [
    "Sin registro",
    "> 7 horas (óptimo)",
    "5 - 7 horas (insuficiente)",
    "< 5 horas (vulnerabilidad severa)"
]
OPCIONES_SUENO_DISPLAY = {
    "es": {x: x for x in OPCIONES_SUENO_CANON},
    "en": {
        OPCIONES_SUENO_CANON[0]: "No record",
        OPCIONES_SUENO_CANON[1]: "> 7 hours (optimal)",
        OPCIONES_SUENO_CANON[2]: "5 - 7 hours (insufficient)",
        OPCIONES_SUENO_CANON[3]: "< 5 hours (severe deprivation)",
    }
}

OPCIONES_ALIM_CANON = [
    "Sin registro",
    "Completa (adecuada)",
    "Parcial (insuficiente)",
    "Ayuno (vulnerabilidad severa)"
]
OPCIONES_ALIM_DISPLAY = {
    "es": {x: x for x in OPCIONES_ALIM_CANON},
    "en": {
        OPCIONES_ALIM_CANON[0]: "No record",
        OPCIONES_ALIM_CANON[1]: "Complete (adequate)",
        OPCIONES_ALIM_CANON[2]: "Partial (insufficient)",
        OPCIONES_ALIM_CANON[3]: "Fasting (severe vulnerability)",
    }
}

OPCIONES_BIEN_CANON = [
    "Sin registro",
    "Bienestar óptimo (sin dolor, molestia o fatiga)",
    "Malestar moderado (cólico, dolor, molestia o fatiga moderada por ayuda en casa)",
    "Malestar agudo (cólico, dolor, molestia o fatiga severa por emergencia/ayuda intensiva en casa)"
]
OPCIONES_BIEN_DISPLAY = {
    "es": {x: x for x in OPCIONES_BIEN_CANON},
    "en": {
        OPCIONES_BIEN_CANON[0]: "No record",
        OPCIONES_BIEN_CANON[1]: "Optimal well-being (no pain, discomfort, or fatigue)",
        OPCIONES_BIEN_CANON[2]: "Moderate discomfort (cramps, pain, or moderate fatigue from household/care duties)",
        OPCIONES_BIEN_CANON[3]: "Acute discomfort (severe cramps, acute pain, or severe fatigue from domestic emergency/intensive household care)",
    }
}

MARCOS_CURRICULARES = {
    "SEP_NEM": {
        "es": "SEP / Nueva Escuela Mexicana (NEM)",
        "en": "SEP / New Mexican School (NEM)",
        "guia": (
            "Organiza el informe formativo en los Campos Formativos y Ejes Articuladores de la Nueva Escuela Mexicana (NEM / SEP): "
            "1) Saberes y Pensamiento Científico (vinculado a Indagación, Pensamiento Crítico y Saber Hacer Técnico), "
            "2) Ética, Naturaleza y Sociedades (Razonamiento Ético y Agencia Intercultural), "
            "3) De lo Humano y lo Comunitario (Liderazgo Colaborativo, Resiliencia/Vida Saludable y Reflexión Metacognitiva), "
            "4) Lenguajes y Comunicación dialógica, y 5) Sugerencias de acompañamiento formativo para la boleta descriptiva oficial."
        )
    },
    "IB": {
        "es": "Bachillerato Internacional (IB — PEP / PAI / PD / POP)",
        "en": "International Baccalaureate (IB — PYP / MYP / DP / CP)",
        "guia": (
            "Structure the formative report explicitly mapped to the IB Learner Profile and Approaches to Learning (ATL): "
            "1) Inquirers & Thinkers (Research & Thinking ATL skills), "
            "2) Principled, Caring & Open-Minded (Ethical reasoning & Intercultural agency), "
            "3) Communicators & Collaborative Practice (Social ATL & Applied Knowledge/CP), "
            "4) Balanced, Risk-Takers & Reflective (Self-Management & Reflection ATL), "
            "and 5) Actionable Next Steps for student agency."
        )
    },
    "CCH": {
        "es": "UNAM / CCH (Colegio de Ciencias y Humanidades)",
        "en": "UNAM / CCH Model (Mexico)",
        "guia": (
            "Estructura la síntesis formativa alrededor de los tres principios pedagógicos del Modelo Educativo del CCH (UNAM): "
            "1) Aprender a aprender (Indagación, Pensamiento Crítico y Reflexión Metacognitiva), "
            "2) Aprender a hacer (Saber Hacer Técnico, resolución de problemas y trabajo en taller/laboratorio), "
            "3) Aprender a ser (Razonamiento Ético, Agencia Intercultural, Liderazgo Colaborativo y Autogestión), "
            "y 4) Recomendaciones de acompañamiento académico."
        )
    },
    "CAMBRIDGE": {
        "es": "Cambridge (IGCSE / International A-Levels)",
        "en": "Cambridge (IGCSE / International A-Levels)",
        "guia": (
            "Draft a formal yet supportive Cambridge learner progress report aligned to the Cambridge Learner Attributes: "
            "1) Confident & Engaged (Inquiry, Critical Analysis, and Technical Execution), "
            "2) Responsible & Respectful (Ethical Reasoning, Collaboration, and Intercultural Awareness), "
            "3) Innovative & Reflective (Problem Solving, Self-Management, and Metacognition), "
            "and 4) Targeted Academic Recommendations for the upcoming assessment window."
        )
    },
    "CUSTOM": {
        "es": "Personalizado (criterios de mi institución)",
        "en": "Custom (institution-specific criteria)",
        "guia": "Align the synthesis strictly to the custom competencies and institutional criteria provided by the educator."
    }
}


def eje_label(eje_canon):
    return EJES_DISPLAY[st.session_state.lang].get(eje_canon, eje_canon)


def fmt_db(val):
    if abs(val) < 0.01:
        return "0.0"
    return f"{val:+.1f}"


def limpiar_cadena(texto):
    if not texto:
        return "Anonimo"
    cadena = re.sub(r"[^\w\s-]", "", texto).strip()
    return re.sub(r"[-\s]+", "_", cadena)


def calcular_delta_db(delta_pct, semaforo="VERDE"):
    """Transductor psicofísico puro (Weber-Fechner): ΔdB = 20 · log10(1 + g)."""
    try:
        if isinstance(delta_pct, str):
            delta_pct = delta_pct.replace("%", "").replace("+", "").strip()
        g = float(delta_pct) / 100.0
    except (ValueError, TypeError):
        return 0.0
    if abs(g) < 0.001:
        return 0.0
    ratio = max(1.0 + g, 0.01)
    delta_db = 20.0 * np.log10(ratio)
    return round(float(delta_db), 1)


def limpiar_salida_llm(texto):
    """Elimina cualquier bloque de razonamiento interno (<think> / Thinking Process) si el runtime lo emite."""
    if not texto:
        return ""
    limpio = re.sub(r"<think>[\s\S]*?</think>", "", texto, flags=re.IGNORECASE)
    if "</think>" in limpio:
        limpio = limpio.split("</think>", 1)[1]
    limpio = re.sub(r"^Thinking Process:[\s\S]*?(?=\n## |\n# |\n\*\*)", "", limpio.strip(), flags=re.IGNORECASE)
    return limpio.strip()


def obtener_tag_sociofisiologico(d_val, semaforo, basal_pct=None, final_pct=None):
    sem = str(semaforo).upper()
    if "VERDE" in sem or "N/A" in sem or "CRITICO" in sem:
        return ""
    emoji = "🔴" if "ROJO" in sem else ("🟡" if "AMARILLO" in sem else "")
    if not emoji or basal_pct is None or final_pct is None:
        return ""
    try:
        b_abs = abs(int(basal_pct))
        f_int = int(final_pct)
    except (ValueError, TypeError):
        return ""
    if b_abs == abs(f_int):
        return ""
    lang = st.session_state.lang
    if f_int > 0 and f_int > b_abs:
        db_basal = calcular_delta_db(b_abs)
        return (
            f" ⚡ *[Amplificado desde {fmt_db(db_basal)} dB (+{b_abs}%) · {emoji}]*"
            if lang == "es"
            else f" ⚡ *[Amplified from {fmt_db(db_basal)} dB (+{b_abs}%) · {emoji}]*"
        )
    if (d_val < 0 or f_int == 0) and b_abs > abs(f_int):
        db_basal = calcular_delta_db(-b_abs)
        return (
            f" 🛡️ *[Atenuado desde {fmt_db(db_basal)} dB (-{b_abs}%) · {emoji}]*"
            if lang == "es"
            else f" 🛡️ *[Dampened from {fmt_db(db_basal)} dB (-{b_abs}%) · {emoji}]*"
        )
    return ""


def parsear_json_ollama(raw_text):
    """Extrae y carga de forma tolerante un objeto JSON devuelto por Ollama."""
    clean_text = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.MULTILINE)
    clean_text = re.sub(r"\s*```$", "", clean_text, flags=re.MULTILINE).strip()
    match_json = re.search(r"(\{[\s\S]*\})", clean_text)
    json_str = match_json.group(1) if match_json else clean_text
    try:
        return json.loads(json_str)
    except Exception:
        json_str_fixed = re.sub(r"(?<!\\)\n", " ", json_str)
        try:
            return json.loads(json_str_fixed)
        except Exception:
            return None


def compactar_expediente_para_reporte(nombre, nivel, materia, grupo, valores_db, historial):
    """Compactación determinista en Python para proteger la ventana de contexto en 4B y 9B."""
    conteo_sem = {"VERDE": 0, "AMARILLO": 0, "ROJO": 0, "ROJO_CRITICO": 0}
    evidencias_por_eje = {eje: [] for eje in EJE_NOMBRES}
    notas_docentes = []
    notas_educabilidad = []

    for idx, obs in enumerate(historial, 1):
        tipo = obs.get("tipo", "IA")
        if obs.get("nota"):
            notas_docentes.append(f"Hito #{idx}: {obs['nota'][:240]}")
        elif tipo == "MANUAL" and obs.get("justificacion"):
            notas_docentes.append(f"Hito #{idx} (Manual): {obs['justificacion'][:240]}")

        res_ia = obs.get("resultado_ia", {})
        est_edu = res_ia.get("estado_educabilidad", {})
        sem = str(est_edu.get("semaforo", "")).upper()
        if "CRITICO" in sem:
            conteo_sem["ROJO_CRITICO"] += 1
        elif "ROJO" in sem:
            conteo_sem["ROJO"] += 1
        elif "AMARILLO" in sem:
            conteo_sem["AMARILLO"] += 1
        elif "VERDE" in sem:
            conteo_sem["VERDE"] += 1
        if any(k in sem for k in ("AMARILLO", "ROJO")):
            ana = est_edu.get("analisis_previo_educabilidad", "")
            adv = est_edu.get("advertencia_pedagogica", "")
            detalle_edu = " ".join(x for x in (ana, adv) if x).strip()
            if detalle_edu:
                notas_educabilidad.append(f"Hito #{idx} [{sem}]: {detalle_edu[:260]}")

        eval_ejes = res_ia.get("evaluacion_ejes", {})
        deltas_h = obs.get("deltas", {})
        for c_j, n_eje in MAPEO_EJES.items():
            d_val = deltas_h.get(n_eje, 0.0)
            if abs(d_val) > 0.01:
                razon = eval_ejes.get(c_j, {}).get("razonamiento", obs.get("justificacion", ""))
                if razon:
                    evidencias_por_eje[n_eje].append(f"({fmt_db(d_val)} dB) {razon}")

    lineas_vec = []
    for eje in EJE_NOMBRES:
        val_db = float(valores_db.get(eje, 0.0))
        factor = 10.0 ** (val_db / 20.0)
        destacados = " | ".join(evidencias_por_eje[eje][-3:]) if evidencias_por_eje[eje] else "Sin evidencia directa registrada."
        lineas_vec.append(f"- {eje} [{EJES_DISPLAY['en'][eje]}]: {fmt_db(val_db)} dB ({factor:.2f}x) -> {destacados}")

    resumen = (
        f"Estudiante: {nombre}\n"
        f"Nivel educativo: {nivel}\n"
        f"Asignatura: {materia or 'General'} | Grupo: {grupo or 'N/A'}\n"
        f"Total de hitos acumulados: {len(historial)}\n"
        f"Historial de semáforos de educabilidad: Verde={conteo_sem['VERDE']}, Amarillo={conteo_sem['AMARILLO']}, Rojo={conteo_sem['ROJO']}, AlertaCrítica={conteo_sem['ROJO_CRITICO']}\n\n"
        f"PERFIL VECTORIAL ACUMULADO EN R8 Y EVIDENCIAS:\n"
        + "\n".join(lineas_vec)
        + (
            "\n\nCONTEXTO SOCIOFISIOLÓGICO / EDUCABILIDAD REGISTRADO (vulnerabilidad física/doméstica, NO es conducta sancionable):\n"
            + "\n".join(notas_educabilidad[-4:])
            if notas_educabilidad else ""
        )
        + "\n\nSÍNTESIS DE OBSERVACIONES RECIENTES:\n"
        + "\n".join(notas_docentes[-6:])
    )
    return resumen


def agregar_texto_formateado_docx(parrafo, texto):
    """Convierte **negritas** y *cursivas* en runs nativos de Word sin dejar asteriscos."""
    partes = re.split(r"(\*\*[^*]+?\*\*|\*[^*]+?\*)", texto)
    for parte in partes:
        if parte.startswith("**") and parte.endswith("**") and len(parte) > 4:
            run = parrafo.add_run(parte[2:-2])
            run.bold = True
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            run = parrafo.add_run(parte[1:-1])
            run.italic = True
        else:
            parrafo.add_run(parte)


def generar_docx_reporte(nombre, matricula, grupo, nivel, materia, marco_nombre, periodo, texto_reporte, valores_db, lang):
    """Genera un archivo Word (.docx) limpio en memoria con pie de página sobrio de Aula Viva®."""
    doc = Document()

    for sec in doc.sections:
        sec.top_margin = Inches(0.85)
        sec.bottom_margin = Inches(0.85)
        sec.left_margin = Inches(0.9)
        sec.right_margin = Inches(0.9)

        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run(TEXTS[lang]["docx_footer"])
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(100, 116, 139)

    # Encabezado
    h1 = doc.add_heading(TEXTS[lang]["docx_doc_title"], level=1)
    h1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    sub = doc.add_paragraph()
    sub_run = sub.add_run(f"{marco_nombre}" + (f"  |  {periodo}" if periodo else ""))
    sub_run.bold = True
    sub_run.font.size = Pt(11)
    sub_run.font.color.rgb = RGBColor(51, 65, 85)

    # Tabla de metadatos del estudiante
    nivel_docx = "—" if (not nivel or nivel == NIVELES_CANON[0] or str(nivel).startswith("--")) else NIVELES_DISPLAY[lang].get(nivel, nivel)
    meta_rows = (
        [
            ("Estudiante", nombre or "—", "Matrícula / ID", matricula or "—"),
            ("Nivel educativo", nivel_docx, "Grupo", grupo or "—"),
            ("Asignatura", materia or "—", "Fecha", datetime.now().strftime("%Y-%m-%d")),
        ]
        if lang == "es"
        else [
            ("Student", nombre or "—", "Student ID", matricula or "—"),
            ("Educational level", nivel_docx, "Group", grupo or "—"),
            ("Subject", materia or "—", "Date", datetime.now().strftime("%Y-%m-%d")),
        ]
    )
    tbl = doc.add_table(rows=len(meta_rows), cols=4)
    tbl.style = "Light Grid Accent 1"
    for r_i, (k1, v1, k2, v2) in enumerate(meta_rows):
        row = tbl.rows[r_i].cells
        row[0].text = k1
        row[1].text = str(v1)
        row[2].text = k2
        row[3].text = str(v2)
        for c_i in (0, 2):
            for p in row[c_i].paragraphs:
                for run in p.runs:
                    run.bold = True

    doc.add_paragraph("")

    # Cuerpo del reporte (interpretando encabezados markdown y viñetas)
    for linea in texto_reporte.splitlines():
        s = linea.strip()
        if not s:
            continue
        if s.startswith("### "):
            doc.add_heading(s[4:].replace("**", ""), level=3)
        elif s.startswith("## "):
            doc.add_heading(s[3:].replace("**", ""), level=2)
        elif s.startswith("# "):
            doc.add_heading(s[2:].replace("**", ""), level=2)
        elif s.startswith("- ") or s.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            agregar_texto_formateado_docx(p, s[2:])
        else:
            p = doc.add_paragraph()
            agregar_texto_formateado_docx(p, s)

    # Tabla de respaldo vectorial en R8
    doc.add_paragraph("")
    doc.add_heading(TEXTS[lang]["docx_vec_title"], level=2)
    vtbl = doc.add_table(rows=1, cols=3)
    vtbl.style = "Light List Accent 1"
    hdr = vtbl.rows[0].cells
    hdr[0].text = "Dimensión" if lang == "es" else "Dimension"
    hdr[1].text = "Acumulado (dB)" if lang == "es" else "Accumulated (dB)"
    hdr[2].text = "Factor (Weber-Fechner)"
    for c in hdr:
        for p in c.paragraphs:
            for run in p.runs:
                run.bold = True

    for eje in EJE_NOMBRES:
        val_db = float(valores_db.get(eje, 0.0))
        factor = 10.0 ** (val_db / 20.0)
        rc = vtbl.add_row().cells
        rc[0].text = EJES_DISPLAY[lang][eje]
        rc[1].text = f"{fmt_db(val_db)} dB"
        rc[2].text = f"{factor:.2f}x"

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


# --- FAVICON VECTORIAL Y ESCUDO ANTI-RECARGA ---
components.html(
    """
    <script>
    (function() {
      const doc = window.parent.document;
      const svgIcon = "data:image/svg+xml," +
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>" +
        "<rect x='2' y='2' width='96' height='96' rx='20' fill='%23ffffff' stroke='%23d0d7de' stroke-width='4'/>" +
        "<polygon points='50,18 82,78 18,78' fill='none' stroke='%230969da' stroke-width='6'/>" +
        "<line x1='10' y1='56' x2='42' y2='48' stroke='%231f2328' stroke-width='4.5'/>" +
        "<line x1='58' y1='46' x2='90' y2='36' stroke='%239333ea' stroke-width='4'/>" +
        "<line x1='61' y1='52' x2='90' y2='52' stroke='%2316a34a' stroke-width='4'/>" +
        "<line x1='64' y1='58' x2='90' y2='68' stroke='%23d97706' stroke-width='4'/>" +
        "</svg>";
      doc.querySelectorAll("link[rel*='icon']").forEach(el => el.remove());
      const link = doc.createElement("link");
      link.rel = "icon";
      link.type = "image/svg+xml";
      link.href = svgIcon;
      doc.head.appendChild(link);
    })();
    </script>
    """,
    height=0,
    width=0
)

if len(st.session_state.get("historial_observaciones", [])) > 0:
    components.html(
        """
        <script>
        const mainWindow = window.parent.document.defaultView;
        if (!mainWindow._prismaGuardAttached) {
            mainWindow.addEventListener('beforeunload', function (e) {
                e.preventDefault();
                e.returnValue = '';
            });
            mainWindow._prismaGuardAttached = true;
        }
        </script>
        """,
        height=0,
        width=0
    )

# --- ESTILOS CSS ADAPTABLES (MODO CLARO Y MODO OSCURO) ---
st.markdown("""
<style>
    .block-container {
        padding-top: 3.2rem !important;
        padding-bottom: 1.5rem !important;
    }
    h1 {
        margin-top: 0rem !important;
        padding-top: 0rem !important;
    }
    [data-testid="stColumn"]:nth-of-type(2) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 3.8rem !important;
        align-self: flex-start !important;
        z-index: 99;
    }
    .sticky-radar-container {
        max-height: calc(100vh - 2rem) !important;
        overflow-y: auto !important;
        padding-right: 0.4rem;
    }
    .stButton button {
        border-radius: 8px;
    }
    .staging-card {
        background-color: rgba(99, 102, 241, 0.08);
        border: 1.5px solid rgba(99, 102, 241, 0.65);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .manual-staging-card {
        background-color: rgba(168, 85, 247, 0.08);
        border: 1.5px solid rgba(168, 85, 247, 0.65);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .report-card {
        background-color: rgba(16, 185, 129, 0.07);
        border: 1.5px solid rgba(16, 185, 129, 0.55);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    }
    .stAppDeployButton, [data-testid="stAppDeployButton"] {
        display: none !important;
    }
    .prisma-hero-quote {
        margin: -0.2rem 0 0.85rem 0;
        font-size: 0.96rem;
        font-style: italic;
        font-weight: 500;
        line-height: 1.45;
        background: linear-gradient(
            90deg,
            #6366F1 0%,
            #9333EA 22%,
            #2563EB 42%,
            #0891B2 58%,
            #16A34A 74%,
            #D97706 88%,
            #DC2626 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
    }
    .js-plotly-plot .plotly .modebar,
    .js-plotly-plot .plotly .modebar-group {
        background: transparent !important;
        background-color: transparent !important;
        opacity: 0.90 !important;
        visibility: visible !important;
    }
    [data-testid="stColumn"]:nth-of-type(2) [data-testid="stElementToolbar"],
    [data-testid="stColumn"]:nth-of-type(2) .stElementToolbar {
        opacity: 0.85 !important;
        visibility: visible !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    [data-testid="stColumn"]:nth-of-type(2) [data-testid="stElementToolbar"]:hover,
    [data-testid="stColumn"]:nth-of-type(2) .stElementToolbar:hover {
        opacity: 1 !important;
    }
    [data-testid="stColumn"]:nth-of-type(2) [data-testid="stElementToolbar"] button,
    [data-testid="stColumn"]:nth-of-type(2) [data-testid="stElementToolbarButton"] {
        background: transparent !important;
        background-color: transparent !important;
    }
    .prisma-footer {
        margin-top: 2.2rem;
        padding-top: 0.9rem;
        border-top: 1px solid rgba(148, 163, 184, 0.28);
        font-size: 0.76rem;
        line-height: 1.5;
    }
    .prisma-footer-scope {
        margin: 0 0 0.45rem 0;
        opacity: 0.72;
    }
    .prisma-footer-brand {
        margin: 0;
        font-weight: 600;
        letter-spacing: 0.015em;
        background: linear-gradient(
            90deg,
            #6366F1 0%,
            #9333EA 22%,
            #2563EB 42%,
            #0891B2 58%,
            #16A34A 74%,
            #D97706 88%,
            #DC2626 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        display: inline-block;
    }
    .prisma-field-lbl {
        font-size: 0.875rem;
        margin-bottom: 0.22rem;
        line-height: 1.35;
    }
</style>
""", unsafe_allow_html=True)


# --- INICIALIZACIÓN DE ESTADO DE SESIÓN ---
def inicializar_estado():
    defaults = {
        "valores_db": {eje: 0.0 for eje in EJE_NOMBRES},
        "historial_observaciones": [],
        "analisis_pendiente": None,
        "meta_analisis_pendiente": None,
        "reporte_curricular_generado": None,
        "previsualizacion_manual": None,
        "procesando": False,
        "estudiantes_db": {},
        "mostrar_modal_resguardo": False,
        "mostrar_modal_confirmar_reiniciar": False,
        "input_clave_admin": "",
        "json_ya_descargado": False,
        "input_nombre": "",
        "input_nivel": NIVELES_CANON[0],
        "input_materia": "",
        "input_matricula": "",
        "input_grupo": "",
        "input_nota": "",
        "input_justificacion": "",
        "input_descanso": OPCIONES_SUENO_CANON[0],
        "input_alimentacion": OPCIONES_ALIM_CANON[0],
        "input_bienestar": OPCIONES_BIEN_CANON[0],
        "input_marco": "SEP_NEM",
        "input_periodo": "",
        "input_marco_custom": "",
        "modo_vis_key": "all",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    for eje in EJE_NOMBRES:
        if f"slider_{eje}" not in st.session_state:
            st.session_state[f"slider_{eje}"] = 0.0
        if f"num_{eje}" not in st.session_state:
            st.session_state[f"num_{eje}"] = 0.0


inicializar_estado()

# --- BANDERAS DIFERIDAS (SE EJECUTAN ANTES DE INSTANCIAR WIDGETS) ---
if st.session_state.get("flag_reset_todo", False):
    st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
    st.session_state.historial_observaciones = []
    st.session_state.analisis_pendiente = None
    st.session_state.meta_analisis_pendiente = None
    st.session_state.reporte_curricular_generado = None
    st.session_state.previsualizacion_manual = None
    st.session_state.procesando = False
    st.session_state.input_nombre = ""
    st.session_state.input_matricula = ""
    st.session_state.input_grupo = ""
    st.session_state.input_nivel = NIVELES_CANON[0]
    st.session_state.input_materia = ""
    st.session_state.input_nota = ""
    st.session_state.input_justificacion = ""
    st.session_state.input_descanso = OPCIONES_SUENO_CANON[0]
    st.session_state.input_alimentacion = OPCIONES_ALIM_CANON[0]
    st.session_state.input_bienestar = OPCIONES_BIEN_CANON[0]
    st.session_state.json_ya_descargado = False
    st.session_state.mostrar_modal_resguardo = False
    st.session_state.mostrar_modal_confirmar_reiniciar = False
    st.session_state["debug_raw_ollama"] = ""
    for eje in EJE_NOMBRES:
        st.session_state[f"slider_{eje}"] = 0.0
        st.session_state[f"num_{eje}"] = 0.0
    st.session_state.flag_reset_todo = False

if st.session_state.get("flag_cargar_expediente") is not None:
    datos_c = st.session_state.flag_cargar_expediente
    st.session_state.flag_cargar_expediente = None
    vec_cargado = datos_c.get("vector_actual_db", {})
    st.session_state.valores_db = {eje: float(vec_cargado.get(eje, 0.0)) for eje in EJE_NOMBRES}
    st.session_state.historial_observaciones = datos_c.get("historial_observaciones", [])
    st.session_state.input_nombre = datos_c.get("estudiante", "")
    st.session_state.input_matricula = datos_c.get("matricula", "")
    st.session_state.input_grupo = datos_c.get("grupo", "")
    niv_c = datos_c.get("nivel_educativo", NIVELES_CANON[0])
    st.session_state.input_nivel = niv_c if niv_c in NIVELES_CANON else NIVELES_CANON[0]
    st.session_state.input_materia = datos_c.get("materia", "")
    st.session_state.analisis_pendiente = None
    st.session_state.meta_analisis_pendiente = None
    st.session_state.reporte_curricular_generado = None
    st.session_state.previsualizacion_manual = None
    st.session_state["debug_raw_ollama"] = ""
    st.session_state.json_ya_descargado = True

if st.session_state.get("flag_limpiar_nota", False):
    st.session_state.input_nota = ""
    st.session_state.flag_limpiar_nota = False

if st.session_state.get("flag_limpiar_justificacion", False):
    st.session_state.input_justificacion = ""
    st.session_state.flag_limpiar_justificacion = False

if st.session_state.get("flag_reset_calib", False):
    for eje in EJE_NOMBRES:
        st.session_state[f"slider_{eje}"] = 0.0
        st.session_state[f"num_{eje}"] = 0.0
    st.session_state.flag_reset_calib = False


# --- ESTADO DE BLOQUEO GLOBAL (PROCESANDO O ALARMA CRÍTICA ACTIVA) ---
alerta_critica_activa = False
if st.session_state.analisis_pendiente:
    alerta_critica_activa = any(
        "ROJO_CRITICO" in str(item.get("resultado_ia", {}).get("estado_educabilidad", {}).get("semaforo", "")).upper()
        for item in st.session_state.analisis_pendiente.get("hitos", [])
    )
bloqueo_ui = st.session_state.procesando or alerta_critica_activa

if alerta_critica_activa:
    st.markdown(
        "<style>"
        "[data-testid='stColumn']:nth-of-type(2) {"
        "  opacity: 0.30 !important;"
        "  pointer-events: none !important;"
        "  filter: grayscale(0.55);"
        "}"
        "</style>",
        unsafe_allow_html=True
    )


def obtener_deltas_ia_pendientes():
    deltas_tot = {eje: 0.0 for eje in EJE_NOMBRES}
    if st.session_state.analisis_pendiente and not alerta_critica_activa:
        for item in st.session_state.analisis_pendiente.get("hitos", []):
            for eje, d_v in item.get("deltas", {}).items():
                deltas_tot[eje] = round(deltas_tot[eje] + float(d_v), 1)
    return deltas_tot


# --- CALLBACKS SEGUROS ---
def sync_slider_a_num(eje_nombre):
    st.session_state[f"num_{eje_nombre}"] = float(st.session_state[f"slider_{eje_nombre}"])


def sync_num_a_slider(eje_nombre):
    st.session_state[f"slider_{eje_nombre}"] = float(st.session_state[f"num_{eje_nombre}"])


def on_change_lang():
    guardar_config_local(lang=st.session_state.lang)


def on_change_model():
    guardar_config_local(modelo_activo=st.session_state.modelo_activo)


def on_change_matricula():
    mat_val = st.session_state.input_matricula
    if mat_val in st.session_state.estudiantes_db:
        reg = st.session_state.estudiantes_db[mat_val]
        st.session_state.input_nombre = reg.get("nombre", "")
        st.session_state.input_grupo = reg.get("grupo", "")
        niv = reg.get("nivel", NIVELES_CANON[0])
        st.session_state.input_nivel = niv if niv in NIVELES_CANON else NIVELES_CANON[0]
        st.session_state.input_materia = reg.get("materia", "")


def marcar_descargado():
    st.session_state.json_ya_descargado = True


# --- PERSISTENCIA DE EXPEDIENTE EN DISCO ---
def guardar_expediente_disco(nombre, matricula, grupo, nivel="", materia="", ciclo_id="2026", es_cierre=False):
    fecha_iso = datetime.now().strftime("%y%m%d")
    hora_iso = datetime.now().strftime("%H%M%S")
    nom_clean = limpiar_cadena(nombre)
    grp_clean = limpiar_cadena(grupo)
    ciclo_clean = limpiar_cadena(ciclo_id)

    n_h = len(st.session_state.historial_observaciones)
    hito_str = f"_Hito{n_h:02d}" if n_h > 0 else ""

    sufijo = f"_CIERRE_{ciclo_clean}.json" if es_cierre else f"{hito_str}_PRISMA.json"
    filename = f"{fecha_iso}_{hora_iso}_{nom_clean}_{grp_clean}{sufijo}"
    filepath = os.path.join(DIR_EXPEDIENTES, filename)

    exp_data = {
        "tipo_archivo": "CIERRE_CICLO" if es_cierre else "EXPEDIENTE_ACTIVO",
        "ciclo_escolar": ciclo_id,
        "estudiante": nombre,
        "matricula": matricula,
        "grupo": grupo,
        "nivel_educativo": nivel,
        "materia": materia,
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vector_actual_db": dict(st.session_state.valores_db),
        "historial_observaciones": list(st.session_state.historial_observaciones)
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(exp_data, f, indent=2, ensure_ascii=False)
    return filename, exp_data


# --- DIÁLOGOS DE CONTROL (MODALES) ---
@st.dialog("💾 PRISMA™")
def modal_exportar_resguardo(nombre, matricula, grupo, nivel, materia):
    st.session_state.mostrar_modal_resguardo = False
    nombre_mostrar = nombre if nombre else ("Estudiante" if st.session_state.lang == "es" else "Student")
    st.markdown(f"### {t('modal_save_title')}")
    st.write(t("modal_save_body").format(name=nombre_mostrar))
    st.caption(t("modal_save_cap"))

    filename_export, exp_data = guardar_expediente_disco(nombre, matricula, grupo, nivel, materia)

    col_m1, col_m2 = st.columns([0.6, 0.4])
    with col_m1:
        st.download_button(
            label=t("modal_save_dl"),
            data=json.dumps(exp_data, indent=2, ensure_ascii=False),
            file_name=filename_export,
            mime="application/json",
            type="primary",
            use_container_width=True,
            on_click=marcar_descargado
        )
    with col_m2:
        if st.button(t("modal_save_cont"), use_container_width=True):
            st.rerun()


@st.dialog("⚠️ PRISMA™")
def modal_confirmar_reiniciar():
    st.markdown(f"### {t('modal_reset_title')}")
    st.write(t("modal_reset_body"))
    st.write(t("modal_reset_ask"))

    filename_export, exp_data = guardar_expediente_disco(
        st.session_state.input_nombre,
        st.session_state.input_matricula,
        st.session_state.input_grupo,
        st.session_state.input_nivel,
        st.session_state.input_materia
    )

    if st.download_button(
        label=t("modal_reset_dl"),
        data=json.dumps(exp_data, indent=2, ensure_ascii=False),
        file_name=filename_export,
        mime="application/json",
        type="primary",
        use_container_width=True
    ):
        st.session_state.flag_reset_todo = True
        st.rerun()

    st.markdown("---")
    col_r1, col_r2 = st.columns([0.55, 0.45])
    with col_r1:
        if st.button(t("modal_reset_force"), type="secondary", use_container_width=True):
            st.session_state.flag_reset_todo = True
            st.rerun()
    with col_r2:
        if st.button(t("modal_cancel"), use_container_width=True):
            st.session_state.mostrar_modal_confirmar_reiniciar = False
            st.rerun()


# --- ENCABEZADO PRINCIPAL ---
st.title(t("app_title"))
st.markdown(t("app_subtitle"))
st.caption(t("app_caption"))
st.markdown(f"<p class='prisma-hero-quote'>{t('app_quote')}</p>", unsafe_allow_html=True)


# --- SIDEBAR: IDIOMA, MOTOR, EXPEDIENTES Y ADMIN ---
with st.sidebar:
    st.header(t("sidebar_header"))

    if "lang_selector_ui" not in st.session_state:
        st.session_state.lang_selector_ui = st.session_state.lang

    def on_change_lang_ui():
        st.session_state.lang = st.session_state.lang_selector_ui
        guardar_config_local(lang=st.session_state.lang)

    st.radio(
        "🌐 Language / Idioma",
        options=["es", "en"],
        format_func=lambda x: "Español" if x == "es" else "English",
        horizontal=True,
        key="lang_selector_ui",
        on_change=on_change_lang_ui,
        disabled=st.session_state.procesando
    )

    st.markdown("---")
    st.markdown(f"<h3 style='margin:0 0 0.4rem 0;font-size:1.15rem;'>{PRISMA_SVG_ICON}{t('engine_header')}</h3>", unsafe_allow_html=True)
    if not OLLAMA_ONLINE:
        st.warning(t("engine_offline"))
    else:
        opciones_motor = ["prisma-engine-4b", "prisma-engine-9b"]
        for m_ext in MOTORES_INSTALADOS:
            if m_ext not in opciones_motor:
                opciones_motor.append(m_ext)

        if "selector_motor_ui" not in st.session_state or st.session_state.selector_motor_ui not in opciones_motor:
            st.session_state.selector_motor_ui = st.session_state.modelo_activo if st.session_state.modelo_activo in opciones_motor else opciones_motor[0]

        def fmt_motor_opcion(m_key):
            instalado = m_key in MOTORES_INSTALADOS
            estado = t("engine_ready") if instalado else t("engine_missing")
            if m_key in PRISMA_ENGINE_CATALOG:
                meta = PRISMA_ENGINE_CATALOG[m_key]
                ram_lbl = meta["ram_es"] if st.session_state.lang == "es" else meta["ram_en"]
                return f"{meta['short']} ({ram_lbl}) · {estado}"
            return f"{m_key} · {estado}"

        def on_change_motor_ui():
            sel = st.session_state.selector_motor_ui
            if sel in MOTORES_INSTALADOS:
                st.session_state.modelo_activo = sel
                guardar_config_local(modelo_activo=sel)

        motor_ui_sel = st.selectbox(
            t("engine_select"),
            options=opciones_motor,
            format_func=fmt_motor_opcion,
            key="selector_motor_ui",
            on_change=on_change_motor_ui,
            disabled=bloqueo_ui
        )

        if not MOTORES_INSTALADOS:
            st.warning(t("engine_none"))

        if motor_ui_sel not in MOTORES_INSTALADOS and motor_ui_sel in PRISMA_ENGINE_CATALOG:
            meta_sel = PRISMA_ENGINE_CATALOG[motor_ui_sel]
            ram_actual = detectar_ram_gb_local()
            st.info(t("engine_install_prompt").format(ram=ram_actual))
            if ram_actual < meta_sel["min_ram"]:
                st.warning(t("engine_ram_warn").format(ram=ram_actual))
            if st.button(
                t("engine_install_btn").format(name=meta_sel["short"], size=meta_sel["size"]),
                type="primary",
                use_container_width=True,
                disabled=bloqueo_ui
            ):
                pbar = st.progress(0.0)
                sbox = st.empty()
                try:
                    instalar_motor_desde_app(motor_ui_sel, pbar, sbox, lang=st.session_state.lang)
                    st.session_state.modelo_activo = motor_ui_sel
                    guardar_config_local(modelo_activo=motor_ui_sel)
                    sbox.success(t("engine_install_ok").format(name=meta_sel["short"]))
                    st.rerun()
                except Exception as exc:
                    sbox.error(f"{t('engine_install_err')} {exc}")

    with st.expander(t("lang_matrix_title"), expanded=False):
        st.markdown(t("lang_matrix_body"))

    st.markdown("---")
    st.subheader(t("wf_header"))
    if st.button(t("btn_reset"), use_container_width=True, type="primary", disabled=bloqueo_ui):
        if len(st.session_state.historial_observaciones) > 0 and not st.session_state.get("json_ya_descargado", False):
            st.session_state.mostrar_modal_confirmar_reiniciar = True
            st.rerun()
        else:
            st.session_state.flag_reset_todo = True
            st.rerun()

    if len(st.session_state.historial_observaciones) > 0 and st.session_state.input_nombre.strip():
        fn_sb, data_sb = guardar_expediente_disco(
            st.session_state.input_nombre,
            st.session_state.input_matricula,
            st.session_state.input_grupo,
            st.session_state.input_nivel,
            st.session_state.input_materia
        )
        st.download_button(
            label=t("export_sidebar_btn"),
            data=json.dumps(data_sb, indent=2, ensure_ascii=False),
            file_name=fn_sb,
            mime="application/json",
            use_container_width=True,
            on_click=marcar_descargado,
            disabled=bloqueo_ui
        )

    st.markdown("---")
    st.subheader(t("load_header"))
    archivo_cargado = st.file_uploader(
        t("load_uploader"),
        type=["json"],
        disabled=bloqueo_ui,
        help=t("load_help")
    )

    btn_importar = st.button(t("btn_load"), disabled=(archivo_cargado is None or bloqueo_ui), use_container_width=True)
    if btn_importar and archivo_cargado is not None:
        try:
            datos = json.load(archivo_cargado)
            if datos.get("matricula"):
                niv_tmp = datos.get("nivel_educativo", NIVELES_CANON[0])
                st.session_state.estudiantes_db[datos["matricula"]] = {
                    "nombre": datos.get("estudiante", ""),
                    "grupo": datos.get("grupo", ""),
                    "nivel": niv_tmp if niv_tmp in NIVELES_CANON else NIVELES_CANON[0],
                    "materia": datos.get("materia", "")
                }
            st.session_state.flag_cargar_expediente = datos
            st.success(t("load_ok"))
            st.rerun()
        except Exception as e:
            st.error(f"{t('load_err')} {e}")

    st.markdown("---")
    st.header(t("admin_header"))

    st.text_input(
        t("admin_key_label"),
        type="password",
        key="input_clave_admin",
        placeholder=t("admin_key_ph"),
        disabled=bloqueo_ui,
        help=t("admin_key_help")
    )

    es_admin = (st.session_state.input_clave_admin in ["prisma2026", "prisma26"])

    def cerrar_sesion_admin():
        st.session_state.input_clave_admin = ""

    if es_admin:
        st.success(t("admin_ok"))
        st.button(t("admin_logout"), use_container_width=True, disabled=bloqueo_ui, on_click=cerrar_sesion_admin)
    else:
        st.info(t("admin_locked"))

    st.markdown("---")
    label_tabula = f"1. {t('tabula_label')}" if es_admin else f"1. {t('tabula_label')} 🔒 Admin"
    st.subheader(label_tabula)
    st.caption(t("tabula_caption"))

    ciclo_id_input = st.text_input(
        t("tabula_cycle"),
        value=f"{datetime.now().year}-1",
        disabled=(not es_admin or bloqueo_ui),
        help=t("tabula_help")
    )

    btn_tabula = st.button(t("tabula_btn"), disabled=(not es_admin or bloqueo_ui), use_container_width=True)
    if btn_tabula and es_admin:
        fn_cierre, _ = guardar_expediente_disco(
            st.session_state.input_nombre,
            st.session_state.input_matricula,
            st.session_state.input_grupo,
            st.session_state.input_nivel,
            st.session_state.input_materia,
            ciclo_id=ciclo_id_input,
            es_cierre=True
        )
        st.session_state.historial_observaciones.append({
            "tipo": "TABULA_RASA",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "justificacion": f"Cierre de ciclo escolar '{ciclo_id_input}' ('Año nuevo, vida nueva'). Resguardado en {fn_cierre}. Vector restablecido a 0.0 dB.",
            "vector_snapshot": dict(st.session_state.valores_db)
        })
        st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
        st.session_state.json_ya_descargado = False
        st.success(t("tabula_ok").format(fn=fn_cierre))
        st.rerun()


# --- SECCIÓN 1: FICHA DEL ESTUDIANTE ---
st.subheader(t("sec1_title"))
col_f1, col_f2, col_f3 = st.columns([0.38, 0.37, 0.25])

with col_f1:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_name')}</div>", unsafe_allow_html=True)
    nom_in = st.text_input("f_name", key="input_nombre", placeholder="María López", disabled=bloqueo_ui, label_visibility="collapsed")
with col_f2:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_id')}</div>", unsafe_allow_html=True)
    mat_in = st.text_input("f_id", key="input_matricula", placeholder="A012345", on_change=on_change_matricula, disabled=bloqueo_ui, label_visibility="collapsed")
with col_f3:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_group')}</div>", unsafe_allow_html=True)
    grp_in = st.text_input("f_group", key="input_grupo", placeholder="2B", disabled=bloqueo_ui, label_visibility="collapsed")

col_ctx1, col_ctx2 = st.columns([0.6, 0.4])
with col_ctx1:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_level')}</div>", unsafe_allow_html=True)
    nivel_in = st.selectbox(
        "f_level",
        options=NIVELES_CANON,
        format_func=lambda n: NIVELES_DISPLAY[st.session_state.lang].get(n, n),
        key="input_nivel",
        disabled=bloqueo_ui,
        label_visibility="collapsed"
    )
with col_ctx2:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_subject')}</div>", unsafe_allow_html=True)
    materia_in = st.text_input("f_subject", key="input_materia", placeholder="STEM / Lab", disabled=bloqueo_ui, label_visibility="collapsed")

if mat_in and nom_in:
    st.session_state.estudiantes_db[mat_in] = {
        "nombre": nom_in,
        "grupo": grp_in,
        "nivel": nivel_in,
        "materia": materia_in
    }

# --- SECCIÓN 2: ESTADO DE EDUCABILIDAD ---
st.markdown("---")
st.subheader(t("sec2_title"))
st.caption(t("sec2_caption"))

col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_sleep')}</div>", unsafe_allow_html=True)
    st.selectbox(
        "f_sleep",
        options=OPCIONES_SUENO_CANON,
        format_func=lambda x: OPCIONES_SUENO_DISPLAY[st.session_state.lang][x],
        key="input_descanso",
        disabled=bloqueo_ui,
        label_visibility="collapsed"
    )
with col_e2:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_food')}</div>", unsafe_allow_html=True)
    st.selectbox(
        "f_food",
        options=OPCIONES_ALIM_CANON,
        format_func=lambda x: OPCIONES_ALIM_DISPLAY[st.session_state.lang][x],
        key="input_alimentacion",
        disabled=bloqueo_ui,
        label_visibility="collapsed"
    )
with col_e3:
    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_well')}</div>", unsafe_allow_html=True)
    st.selectbox(
        "f_well",
        options=OPCIONES_BIEN_CANON,
        format_func=lambda x: OPCIONES_BIEN_DISPLAY[st.session_state.lang][x],
        key="input_bienestar",
        disabled=bloqueo_ui,
        label_visibility="collapsed"
    )

st.markdown("---")

# --- COLUMNAS PRINCIPALES (IZQUIERDA: OPERACIÓN | DERECHA: RADAR STICKY) ---
col_izq, col_der = st.columns([0.46, 0.54])

with col_izq:
    # --- SECCIÓN 3: NOTA NARRATIVA ---
    st.subheader(t("sec3_title"))
    with st.form(key="form_nota_docente", clear_on_submit=False):
        st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_note')}</div>", unsafe_allow_html=True)
        nota_docente = st.text_area(
            "f_note",
            key="input_nota",
            height=130,
            disabled=bloqueo_ui,
            label_visibility="collapsed"
        )
        st.caption(t("ph_note"))
        btn_analizar = st.form_submit_button(
            t("btn_analyze") if not st.session_state.procesando else t("btn_analyzing"),
            type="primary",
            use_container_width=True,
            disabled=bloqueo_ui
        )

    if btn_analizar and not st.session_state.procesando:
        if not nom_in.strip():
            st.error(t("err_no_name"))
        elif nivel_in == NIVELES_CANON[0]:
            st.error(t("err_no_level"))
        elif not nota_docente.strip():
            st.error(t("err_no_note"))
        else:
            st.session_state.procesando = True
            st.rerun()

    # Proceso activo de inferencia
    if st.session_state.procesando and st.session_state.input_nota.strip():
        texto_nota = st.session_state.input_nota.strip()
        modelo_actual = resolver_modelo_ollama(st.session_state.get("modelo_activo", "prisma-engine-4b"), st.session_state.lang)
        with st.spinner(t("spinner_note").format(model=modelo_actual)):
            hubo_falla = False
            try:
                sueno_val = st.session_state.get("input_descanso", OPCIONES_SUENO_CANON[0])
                nutri_val = st.session_state.get("input_alimentacion", OPCIONES_ALIM_CANON[0])
                bienestar_val = st.session_state.get("input_bienestar", OPCIONES_BIEN_CANON[0])

                if st.session_state.lang == "en":
                    nivel_ctx = NIVELES_DISPLAY["en"].get(nivel_in, nivel_in)
                    sueno_ctx = OPCIONES_SUENO_DISPLAY["en"].get(sueno_val, sueno_val)
                    nutri_ctx = OPCIONES_ALIM_DISPLAY["en"].get(nutri_val, nutri_val)
                    bien_ctx = OPCIONES_BIEN_DISPLAY["en"].get(bienestar_val, bienestar_val)
                    encabezado_contexto = (
                        f"FORMATIVE CONTEXT:\n"
                        f"- Student: {nom_in}\n"
                        f"- Educational Level: {nivel_ctx}\n"
                        f"- Subject / Space: {materia_in if materia_in else 'General'}\n"
                        f"- Biopsychosocial record: Sleep: [{sueno_ctx}] | Food/Nutrition: [{nutri_ctx}] | Holistic well-being: [{bien_ctx}]\n"
                    )
                    user_prompt = f'{encabezado_contexto}\nNarrative observation: "{texto_nota}"'
                else:
                    encabezado_contexto = (
                        f"CONTEXTO FORMATIVO:\n"
                        f"- Estudiante: {nom_in}\n"
                        f"- Nivel Educativo: {nivel_in}\n"
                        f"- Asignatura / Espacio: {materia_in if materia_in else 'General'}\n"
                        f"- Registro sociofisiológico: Sueño: [{sueno_val}] | Nutrición: [{nutri_val}] | Bienestar integral: [{bienestar_val}]\n"
                    )
                    user_prompt = f'{encabezado_contexto}\nNota narrativa: "{texto_nota}"'

                payload = {
                    "model": modelo_actual,
                    "prompt": user_prompt,
                    "format": "json",
                    "think": False,
                    "options": {
                        "temperature": 0.0,
                        "num_predict": 2048,
                        "num_ctx": 8192
                    },
                    "stream": False
                }

                response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=180)
                if response.status_code == 200:
                    data_ollama = response.json()
                    raw_text = data_ollama.get("response", "").strip()
                    st.session_state["debug_raw_ollama"] = raw_text

                    res_json = parsear_json_ollama(raw_text)
                    eval_ejes = {}
                    if res_json and isinstance(res_json.get("evaluacion_ejes"), dict):
                        eval_ejes = res_json["evaluacion_ejes"]
                        est_educ = res_json.get("estado_educabilidad", {})
                        semaforo_ia = str(est_educ.get("semaforo", "VERDE")).upper()
                        adv_pedag = est_educ.get("advertencia_pedagogica", "")
                    else:
                        sem_match = re.search(r'"semaforo"\s*:\s*"([^"]+)"', raw_text, re.IGNORECASE)
                        semaforo_ia = sem_match.group(1).upper() if sem_match else "VERDE"
                        adv_match = re.search(r'"advertencia_pedagogica"\s*:\s*"([^"]+)"', raw_text, re.IGNORECASE)
                        adv_pedag = adv_match.group(1) if adv_match else ""
                        res_json = {
                            "estudiante": nom_in,
                            "estado_educabilidad": {
                                "semaforo": semaforo_ia,
                                "advertencia_pedagogica": adv_pedag
                            },
                            "evaluacion_ejes": {}
                        }
                        for c_j in MAPEO_EJES.keys():
                            m_pct = re.search(rf'"{c_j}"\s*:\s*\{{[^}}]*?"delta_pct"\s*:\s*([+-]?\d+)', raw_text)
                            m_pol = re.search(rf'"{c_j}"\s*:\s*\{{[^}}]*?"polaridad"\s*:\s*"([^"]+)"', raw_text)
                            m_raz = re.search(rf'"{c_j}"\s*:\s*\{{[^}}]*?"razonamiento"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', raw_text)
                            eval_ejes[c_j] = {
                                "polaridad": m_pol.group(1).upper() if m_pol else "NEUTRO",
                                "delta_pct": int(m_pct.group(1)) if m_pct else 0,
                                "razonamiento": m_raz.group(1) if m_raz else ""
                            }
                        res_json["evaluacion_ejes"] = eval_ejes

                    es_critico = ("ROJO_CRITICO" in semaforo_ia)
                    if not es_critico:
                        es_rojo_explicito = (
                            "< 5 horas" in sueno_val
                            or "Ayuno" in nutri_val
                            or "Malestar agudo" in bienestar_val
                        )
                        es_amarillo_explicito = (
                            "5 - 7 horas" in sueno_val
                            or "Parcial" in nutri_val
                            or "Malestar moderado" in bienestar_val
                        )
                        if es_rojo_explicito and "ROJO" not in semaforo_ia:
                            semaforo_ia = "ROJO"
                            res_json.setdefault("estado_educabilidad", {})["semaforo"] = "ROJO"
                        elif es_amarillo_explicito and semaforo_ia == "VERDE":
                            semaforo_ia = "AMARILLO"
                            res_json.setdefault("estado_educabilidad", {})["semaforo"] = "AMARILLO"

                    deltas_calculados = {}
                    for c_j, n_eje in MAPEO_EJES.items():
                        if es_critico:
                            if c_j in eval_ejes and isinstance(eval_ejes[c_j], dict):
                                eval_ejes[c_j]["polaridad"] = "NEUTRO"
                                eval_ejes[c_j]["delta_basal_pct"] = 0
                                eval_ejes[c_j]["delta_pct"] = 0
                            deltas_calculados[n_eje] = 0.0
                        elif c_j in eval_ejes and isinstance(eval_ejes[c_j], dict):
                            val_obj = eval_ejes[c_j]
                            polaridad = str(val_obj.get("polaridad", "NEUTRO")).upper()
                            magnitud = abs(int(val_obj.get("delta_pct", 0)))
                            basal_mag = abs(int(val_obj.get("delta_basal_pct", magnitud)))
                            if polaridad == "REGRESION" and magnitud > 0:
                                pct_crec = -magnitud
                                eval_ejes[c_j]["delta_basal_pct"] = basal_mag if ("AMARILLO" in semaforo_ia or "ROJO" in semaforo_ia) else magnitud
                            elif polaridad == "CRECIMIENTO" and magnitud > 0:
                                if "AMARILLO" in semaforo_ia or "ROJO" in semaforo_ia:
                                    max_amp_pct = 12 if "ROJO" in semaforo_ia else 6
                                    max_amp_db = 1.0 if "ROJO" in semaforo_ia else 0.5
                                    if basal_mag == 0:
                                        basal_mag = magnitud
                                    magnitud = min(magnitud, basal_mag + max_amp_pct)
                                    db_basal_chk = calcular_delta_db(basal_mag)
                                    db_final_chk = calcular_delta_db(magnitud)
                                    if db_final_chk > round(db_basal_chk + max_amp_db, 1):
                                        db_lim = round(db_basal_chk + max_amp_db, 1)
                                        magnitud = max(basal_mag, int(round((10.0 ** (db_lim / 20.0) - 1.0) * 100.0)))
                                    eval_ejes[c_j]["delta_basal_pct"] = basal_mag
                                else:
                                    eval_ejes[c_j]["delta_basal_pct"] = magnitud
                                pct_crec = magnitud
                            else:
                                pct_crec = 0
                                if not ("AMARILLO" in semaforo_ia or "ROJO" in semaforo_ia):
                                    eval_ejes[c_j]["delta_basal_pct"] = 0
                            eval_ejes[c_j]["delta_pct"] = pct_crec
                            deltas_calculados[n_eje] = calcular_delta_db(pct_crec, semaforo=semaforo_ia)
                        else:
                            deltas_calculados[n_eje] = 0.0

                    st.session_state.analisis_pendiente = {
                        "modo": "SIMPLE",
                        "hitos": [{
                            "sub_idx": 1,
                            "nota": texto_nota,
                            "deltas": deltas_calculados,
                            "resultado_ia": res_json
                        }]
                    }
                else:
                    st.error(f"⚠️ HTTP {response.status_code} (Ollama).")
                    hubo_falla = True
            except Exception as e:
                st.error(f"⚠️ Error Ollama: {e}")
                hubo_falla = True
            finally:
                st.session_state.procesando = False
                if not hubo_falla:
                    st.rerun()

    if st.session_state.get("debug_raw_ollama"):
        with st.expander(t("debug_raw"), expanded=False):
            st.code(st.session_state["debug_raw_ollama"], language="json")

    # --- STAGING / PREVISUALIZACIÓN DE IA ---
    if st.session_state.analisis_pendiente:
        with st.container(border=True):
            hitos_p = st.session_state.analisis_pendiente["hitos"]
            hay_rojo_critico = any(
                "ROJO_CRITICO" in str(item.get("resultado_ia", {}).get("estado_educabilidad", {}).get("semaforo", "")).upper()
                for item in hitos_p
            )

            if hay_rojo_critico:
                st.error(t("crit_title"))
                st.markdown(t("crit_body"))
                st.markdown(t("crit_action"))

                col_cr1, col_cr2 = st.columns([0.62, 0.38])
                with col_cr1:
                    if st.button(t("btn_crit_log"), type="primary", use_container_width=True, disabled=st.session_state.procesando):
                        for item in hitos_p:
                            st.session_state.historial_observaciones.append({
                                "tipo": "ALERTA_CRITICA",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "nota": item["nota"],
                                "deltas": {eje: 0.0 for eje in EJE_NOMBRES},
                                "resultado_ia": item["resultado_ia"],
                                "vector_snapshot": dict(st.session_state.valores_db)
                            })
                        st.session_state.analisis_pendiente = None
                        st.session_state.previsualizacion_manual = None
                        st.session_state.json_ya_descargado = False
                        st.session_state.flag_limpiar_nota = True
                        guardar_expediente_disco(nom_in, mat_in, grp_in, nivel_in, materia_in)
                        st.session_state.mostrar_modal_resguardo = True
                        st.rerun()
                with col_cr2:
                    if st.button(t("btn_crit_discard"), use_container_width=True, disabled=st.session_state.procesando):
                        st.session_state.analisis_pendiente = None
                        st.session_state.previsualizacion_manual = None
                        st.session_state.flag_limpiar_nota = True
                        st.rerun()
            else:
                st.markdown(t("staging_title"))
                st.caption(t("staging_caption"))

                for item in hitos_p:
                    res_ia = item.get("resultado_ia", {})
                    est_educ = res_ia.get("estado_educabilidad", {})
                    semaforo = str(est_educ.get("semaforo", "VERDE")).upper()
                    adv_pedag = est_educ.get("advertencia_pedagogica", "")

                    if "ROJO" in semaforo:
                        st.error(f"{t('sem_red')} {adv_pedag}")
                    elif "AMARILLO" in semaforo:
                        st.warning(f"{t('sem_yellow')} {adv_pedag}")
                    else:
                        st.success(f"{t('sem_green')} {adv_pedag or t('sem_green_default')}")

                    res_ejes = res_ia.get("evaluacion_ejes", {})
                    hubo_eje = False
                    for c_j, n_eje in MAPEO_EJES.items():
                        d_val = item["deltas"].get(n_eje, 0.0)
                        pct_val = res_ejes.get(c_j, {}).get("delta_pct", 0)
                        basal_val = res_ejes.get(c_j, {}).get("delta_basal_pct", abs(pct_val))
                        if abs(d_val) > 0.01:
                            hubo_eje = True
                            razon = res_ejes.get(c_j, {}).get("razonamiento", "")
                            pct_str = f" ({pct_val:+d}%)"
                            color_tag = f":green[**{fmt_db(d_val)} dB**{pct_str}]" if d_val > 0 else f":red[**{fmt_db(d_val)} dB**{pct_str}]"
                            tag_socio = obtener_tag_sociofisiologico(d_val, semaforo, basal_pct=basal_val, final_pct=pct_val)
                            st.markdown(f"  └ **{eje_label(n_eje)}:** {color_tag}{tag_socio} — *{razon}*")
                    if not hubo_eje:
                        st.caption(t("hist_no_deltas"))

                st.markdown("---")
                col_s1, col_s2 = st.columns([0.55, 0.45])
                with col_s1:
                    if st.button(t("btn_accept"), type="primary", use_container_width=True, disabled=bloqueo_ui):
                        for item in hitos_p:
                            for eje, d_val in item["deltas"].items():
                                st.session_state.valores_db[eje] = round(st.session_state.valores_db[eje] + float(d_val), 1)
                            st.session_state.historial_observaciones.append({
                                "tipo": "IA",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "nota": item["nota"],
                                "deltas": item["deltas"],
                                "resultado_ia": item["resultado_ia"],
                                "vector_snapshot": dict(st.session_state.valores_db)
                            })
                        st.session_state.analisis_pendiente = None
                        st.session_state.previsualizacion_manual = None
                        st.session_state.json_ya_descargado = False
                        st.session_state.flag_limpiar_nota = True
                        guardar_expediente_disco(nom_in, mat_in, grp_in, nivel_in, materia_in)
                        st.session_state.mostrar_modal_resguardo = True
                        st.rerun()

                with col_s2:
                    if st.button(t("btn_reject"), use_container_width=True, disabled=bloqueo_ui):
                        st.session_state.analisis_pendiente = None
                        st.session_state.previsualizacion_manual = None
                        st.rerun()

    # --- SECCIÓN 4: CALIBRACIÓN MANUAL DOCENTE (SUMADA EN VIVO SOBRE PRISMA) ---
    st.markdown("---")
    st.subheader(t("sec6_title"))
    st.caption(t("sec6_caption"))

    deltas_ia_pend = obtener_deltas_ia_pendientes()
    hay_ia_pendiente = (st.session_state.analisis_pendiente is not None and not alerta_critica_activa)

    for eje in EJE_NOMBRES:
        base_eje = round(st.session_state.valores_db[eje] + (deltas_ia_pend[eje] if hay_ia_pendiente else 0.0), 1)
        sufijo_ia = f" &nbsp;*(PRISMA: {fmt_db(deltas_ia_pend[eje])} dB)*" if (hay_ia_pendiente and abs(deltas_ia_pend[eje]) > 0.01) else ""
        st.markdown(f"**{eje_label(eje)}** &nbsp;·&nbsp; `{fmt_db(base_eje)} dB`{sufijo_ia}")
        col_c1, col_c2 = st.columns([0.7, 0.3])
        with col_c1:
            st.slider(
                f"Slider {eje}",
                min_value=-6.0,
                max_value=6.0,
                step=0.1,
                key=f"slider_{eje}",
                on_change=sync_slider_a_num,
                args=(eje,),
                disabled=bloqueo_ui,
                label_visibility="collapsed"
            )
        with col_c2:
            st.number_input(
                f"Val {eje}",
                min_value=-6.0,
                max_value=6.0,
                step=0.1,
                key=f"num_{eje}",
                on_change=sync_num_a_slider,
                args=(eje,),
                disabled=bloqueo_ui,
                label_visibility="collapsed"
            )

    st.markdown(f"<div class='prisma-field-lbl'>{t('lbl_justif')}</div>", unsafe_allow_html=True)
    justificacion_docente = st.text_area(
        "f_justif",
        key="input_justificacion",
        height=80,
        disabled=bloqueo_ui,
        label_visibility="collapsed"
    )
    st.caption(t("ph_justif"))

    if st.button(t("btn_prev_manual"), type="secondary", use_container_width=True, disabled=bloqueo_ui):
        if not nom_in.strip():
            st.error(t("err_no_name"))
        elif nivel_in == NIVELES_CANON[0]:
            st.error(t("err_no_level"))
        elif justificacion_docente.strip():
            deltas_propuestos = {eje: float(st.session_state[f"num_{eje}"]) for eje in EJE_NOMBRES}
            if any(abs(v) > 0.001 for v in deltas_propuestos.values()):
                st.session_state.previsualizacion_manual = deltas_propuestos
                st.rerun()
            else:
                st.error(t("err_manual_zero"))
        else:
            st.error(t("err_manual_justif"))

    if st.session_state.previsualizacion_manual and not alerta_critica_activa:
        with st.container(border=True):
            st.markdown(t("manual_card_title"))
            st.caption(t("manual_card_caption"))

            for eje, d_v in st.session_state.previsualizacion_manual.items():
                if abs(d_v) > 0.001:
                    base_eje = round(st.session_state.valores_db[eje] + (deltas_ia_pend[eje] if hay_ia_pendiente else 0.0), 1)
                    val_nuevo = round(base_eje + d_v, 1)
                    st.write(f"• **{eje_label(eje)}:** `{fmt_db(base_eje)} dB` ➔ **`{fmt_db(val_nuevo)} dB`** (`{fmt_db(d_v)} dB`)")

            st.write(f'{t("manual_justif_lbl")} *"{st.session_state.input_justificacion}"*')
            st.markdown("---")
            col_m1, col_m2 = st.columns([0.62, 0.38])
            with col_m1:
                if st.button(t("btn_manual_confirm"), type="primary", use_container_width=True, disabled=bloqueo_ui):
                    # 1) Si hay análisis de PRISMA pendiente, registrarlo PRIMERO para conservar el orden causal (#N PRISMA -> #N+1 Manual)
                    if hay_ia_pendiente:
                        for item in st.session_state.analisis_pendiente["hitos"]:
                            for eje, d_ia in item["deltas"].items():
                                st.session_state.valores_db[eje] = round(st.session_state.valores_db[eje] + float(d_ia), 1)
                            st.session_state.historial_observaciones.append({
                                "tipo": "IA",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "nota": item["nota"],
                                "deltas": item["deltas"],
                                "resultado_ia": item["resultado_ia"],
                                "vector_snapshot": dict(st.session_state.valores_db)
                            })
                        st.session_state.analisis_pendiente = None
                        st.session_state.flag_limpiar_nota = True

                    # 2) Luego registrar el ajuste manual docente sobre ese estado
                    for eje in EJE_NOMBRES:
                        st.session_state.valores_db[eje] = round(st.session_state.valores_db[eje] + float(st.session_state.previsualizacion_manual[eje]), 1)
                    st.session_state.historial_observaciones.append({
                        "tipo": "MANUAL",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "justificacion": st.session_state.input_justificacion,
                        "deltas": st.session_state.previsualizacion_manual,
                        "vector_snapshot": dict(st.session_state.valores_db)
                    })
                    st.session_state.previsualizacion_manual = None
                    st.session_state.json_ya_descargado = False
                    st.session_state.flag_limpiar_justificacion = True
                    st.session_state.flag_reset_calib = True
                    guardar_expediente_disco(nom_in, mat_in, grp_in, nivel_in, materia_in)
                    st.session_state.mostrar_modal_resguardo = True
                    st.rerun()
            with col_m2:
                if st.button(t("btn_manual_cancel"), use_container_width=True, disabled=bloqueo_ui):
                    st.session_state.previsualizacion_manual = None
                    st.rerun()

    # --- HISTORIAL DE HITOS ACUMULADOS ---
    if st.session_state.historial_observaciones:
        st.markdown("---")
        st.subheader(f"{t('hist_title')} ({len(st.session_state.historial_observaciones)})")

        for idx, obs in enumerate(reversed(st.session_state.historial_observaciones), 1):
            num_obs = len(st.session_state.historial_observaciones) - idx + 1
            tipo_hito = obs.get("tipo", "IA")

            if tipo_hito == "IA":
                etiqueta_tipo = t("tag_ia")
            elif tipo_hito == "MANUAL":
                etiqueta_tipo = t("tag_manual")
            elif tipo_hito == "META_ANALISIS":
                etiqueta_tipo = t("tag_meta")
            elif tipo_hito == "ALERTA_CRITICA":
                etiqueta_tipo = t("tag_crit")
            else:
                etiqueta_tipo = t("tag_tabula")

            ts = obs.get("timestamp", "")
            with st.expander(f"#{num_obs} — {ts} [{etiqueta_tipo}]", expanded=(num_obs == len(st.session_state.historial_observaciones))):
                if tipo_hito == "ALERTA_CRITICA":
                    st.error(t("crit_title"))
                    if obs.get("nota"):
                        st.write(f'{t("hist_note_lbl")} *"{obs["nota"]}"*')
                    st.caption(t("crit_action"))
                elif tipo_hito in ("IA", "META_ANALISIS"):
                    if obs.get("nota"):
                        st.write(f'{t("hist_note_lbl")} *"{obs["nota"]}"*')
                    elif obs.get("justificacion"):
                        st.write(f"*{obs['justificacion']}*")

                    res_ia_hist = obs.get("resultado_ia", {})
                    est_edu_hist = res_ia_hist.get("estado_educabilidad", obs.get("educabilidad", {}))
                    sem_hist = str(est_edu_hist.get("semaforo", "N/A")).upper()
                    adv_hist = est_edu_hist.get("advertencia_pedagogica", "")

                    if "ROJO" in sem_hist:
                        st.error(f"{t('sem_red')} {adv_hist}")
                    elif "AMARILLO" in sem_hist:
                        st.warning(f"{t('sem_yellow')} {adv_hist}")
                    elif "VERDE" in sem_hist:
                        st.success(f"{t('sem_green')} {adv_hist or t('sem_green_default')}")

                    st.markdown(t("hist_breakdown"))
                    deltas_hist = obs.get("deltas", {})
                    eval_ejes = res_ia_hist.get("evaluacion_ejes", {})
                    hubo_cambios = False
                    for c_j, n_eje in MAPEO_EJES.items():
                        delta = deltas_hist.get(n_eje, 0.0)
                        if abs(delta) > 0.01:
                            hubo_cambios = True
                            razon = eval_ejes.get(c_j, {}).get("razonamiento", "") if isinstance(eval_ejes, dict) else ""
                            pct_eje = eval_ejes.get(c_j, {}).get("delta_pct", "") if isinstance(eval_ejes, dict) else ""
                            basal_eje = eval_ejes.get(c_j, {}).get("delta_basal_pct", abs(pct_eje) if isinstance(pct_eje, int) else 0) if isinstance(eval_ejes, dict) else 0
                            pct_str = f" ({pct_eje:+d}%)" if isinstance(pct_eje, int) else ""
                            color_tag = f":green[**{fmt_db(delta)} dB**{pct_str}]" if delta > 0 else f":red[**{fmt_db(delta)} dB**{pct_str}]"
                            tag_socio_hist = obtener_tag_sociofisiologico(delta, sem_hist, basal_pct=basal_eje, final_pct=pct_eje if isinstance(pct_eje, int) else None)
                            st.markdown(f"• **{eje_label(n_eje)}:** {color_tag}{tag_socio_hist} — *{razon}*")
                    if not hubo_cambios:
                        st.caption(t("hist_no_deltas"))
                elif tipo_hito == "MANUAL":
                    st.write(f'{t("hist_manual_lbl")} *"{obs.get("justificacion", "")}"*')
                    for eje_nom, delta_val in obs.get("deltas", {}).items():
                        if abs(delta_val) > 0.01:
                            st.caption(f"• **{eje_label(eje_nom)}:** `{fmt_db(delta_val)} dB` ({t('hist_direct_adj')})")
                else:
                    st.write(f'{t("hist_trans_lbl")} *"{obs.get("justificacion", "")}"*')

    # --- SECCIÓN 5: META-ANÁLISIS DE TRAYECTORIA ---
    st.markdown("---")
    st.subheader(t("sec4_title"))
    st.caption(t("sec4_caption"))

    if st.button(t("btn_meta"), use_container_width=True, disabled=bloqueo_ui):
        if not nom_in.strip():
            st.error(t("err_no_name"))
        elif len(st.session_state.historial_observaciones) < 2:
            st.warning(t("err_meta_min"))
        else:
            modelo_meta = resolver_modelo_ollama(st.session_state.get("modelo_activo", "prisma-engine-4b"), st.session_state.lang)
            with st.spinner(t("spinner_meta").format(model=modelo_meta)):
                try:
                    resumen_comp = compactar_expediente_para_reporte(
                        nom_in, nivel_in, materia_in, grp_in,
                        st.session_state.valores_db,
                        st.session_state.historial_observaciones
                    )
                    lang_meta = "ESPAÑOL" if st.session_state.lang == "es" else "ENGLISH"
                    meta_sys = (
                        f"You are PRISMA-Engine in LONGITUDINAL META-ANALYSIS mode. Respond in {lang_meta} inside a strict JSON object:\n"
                        '{"diagnostico_general": "Brief holistic synthesis of trajectory strengths, dialectic balance, and growth horizon.", '
                        '"evaluacion_ejes": {"Indagacion_Investigacion": {"razonamiento": "...", "polaridad": "CRECIMIENTO|REGRESION|NEUTRO", "delta_pct": 0}, ... (all 8 canonical keys)}}.\n'
                        "Only propose small fine-tuning holistic deltas (0% to 15%) if longitudinal synergy clearly justifies it; otherwise use NEUTRO and 0."
                    )
                    response_meta = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": modelo_meta,
                            "system": meta_sys,
                            "prompt": resumen_comp,
                            "format": "json",
                            "think": False,
                            "options": {"temperature": 0.0, "num_predict": 2048, "num_ctx": 8192},
                            "stream": False
                        },
                        timeout=180
                    )
                    if response_meta.status_code == 200:
                        meta_res = parsear_json_ollama(limpiar_salida_llm(response_meta.json().get("response", "")))
                        if meta_res and isinstance(meta_res, dict):
                            eval_meta = meta_res.get("evaluacion_ejes", {})
                            overrides = {}
                            for c_j, n_eje in MAPEO_EJES.items():
                                item_m = eval_meta.get(c_j, {}) if isinstance(eval_meta, dict) else {}
                                pol_m = str(item_m.get("polaridad", "NEUTRO")).upper()
                                mag_m = abs(int(item_m.get("delta_pct", 0))) if isinstance(item_m, dict) else 0
                                pct_m = -mag_m if (pol_m == "REGRESION" and mag_m > 0) else (mag_m if (pol_m == "CRECIMIENTO" and mag_m > 0) else 0)
                                overrides[n_eje] = calcular_delta_db(pct_m)
                            st.session_state.meta_analisis_pendiente = {
                                "diagnostico_general": meta_res.get("diagnostico_general", meta_res.get("resumen", "")),
                                "deltas": overrides,
                                "resultado_ia": meta_res
                            }
                            st.rerun()
                        else:
                            st.error("⚠️ Invalid JSON returned during Meta-Analysis.")
                    else:
                        st.error(f"⚠️ HTTP {response_meta.status_code} (Ollama).")
                except Exception as e:
                    st.error(f"⚠️ Error Ollama: {e}")

    if st.session_state.meta_analisis_pendiente and not alerta_critica_activa:
        with st.container(border=True):
            st.markdown(t("meta_card_title"))
            m_data = st.session_state.meta_analisis_pendiente
            if m_data.get("diagnostico_general"):
                st.write(f"*{m_data['diagnostico_general']}*")
            eval_m = m_data.get("resultado_ia", {}).get("evaluacion_ejes", {})
            for c_j, n_eje in MAPEO_EJES.items():
                d_m = m_data["deltas"].get(n_eje, 0.0)
                razon_m = eval_m.get(c_j, {}).get("razonamiento", "") if isinstance(eval_m, dict) else ""
                if abs(d_m) > 0.01 or razon_m:
                    st.write(f"• **{eje_label(n_eje)}:** `{fmt_db(d_m)} dB` — {razon_m}")

            col_ma1, col_ma2 = st.columns([0.62, 0.38])
            with col_ma1:
                if st.button(t("btn_meta_accept"), type="primary", use_container_width=True, disabled=bloqueo_ui):
                    for eje, d_m in m_data["deltas"].items():
                        st.session_state.valores_db[eje] = round(st.session_state.valores_db[eje] + float(d_m), 1)
                    st.session_state.historial_observaciones.append({
                        "tipo": "META_ANALISIS",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "justificacion": m_data.get("diagnostico_general", "Meta-análisis PRISMA™."),
                        "deltas": m_data["deltas"],
                        "resultado_ia": m_data["resultado_ia"],
                        "vector_snapshot": dict(st.session_state.valores_db)
                    })
                    st.session_state.meta_analisis_pendiente = None
                    st.session_state.json_ya_descargado = False
                    guardar_expediente_disco(nom_in, mat_in, grp_in, nivel_in, materia_in)
                    st.session_state.mostrar_modal_resguardo = True
                    st.rerun()
            with col_ma2:
                if st.button(t("btn_meta_discard"), use_container_width=True, disabled=bloqueo_ui):
                    st.session_state.meta_analisis_pendiente = None
                    st.rerun()

    # --- SECCIÓN 6: REPORTE OFICIAL + EXPORTACIÓN .DOCX ---
    st.markdown("---")
    st.subheader(t("sec5_title"))
    st.caption(t("sec5_caption"))

    col_rep1, col_rep2 = st.columns([0.62, 0.38])
    with col_rep1:
        marco_sel = st.selectbox(
            t("lbl_framework"),
            options=list(MARCOS_CURRICULARES.keys()),
            format_func=lambda k: MARCOS_CURRICULARES[k][st.session_state.lang],
            key="input_marco",
            disabled=bloqueo_ui
        )
    with col_rep2:
        periodo_in = st.text_input(
            t("lbl_period"),
            key="input_periodo",
            placeholder=t("ph_period"),
            disabled=bloqueo_ui
        )

    custom_criteria = ""
    if marco_sel == "CUSTOM":
        custom_criteria = st.text_area(
            t("lbl_custom_fw"),
            key="input_marco_custom",
            height=90,
            placeholder=t("ph_custom_fw"),
            disabled=bloqueo_ui
        )

    if st.button(t("btn_gen_report"), type="secondary", use_container_width=True, disabled=bloqueo_ui):
        if not nom_in.strip():
            st.error(t("err_no_name"))
        elif len(st.session_state.historial_observaciones) < 1:
            st.warning(t("err_report_min"))
        elif marco_sel == "CUSTOM" and not custom_criteria.strip():
            st.warning(t("err_custom_empty"))
        else:
            modelo_rep = resolver_modelo_ollama(st.session_state.get("modelo_activo", "prisma-engine-4b"), st.session_state.lang)
            fw_nombre = MARCOS_CURRICULARES[marco_sel][st.session_state.lang]
            with st.spinner(t("spinner_report").format(fw=fw_nombre, model=modelo_rep)):
                try:
                    resumen_exp = compactar_expediente_para_reporte(
                        nom_in, nivel_in, materia_in, grp_in,
                        st.session_state.valores_db,
                        st.session_state.historial_observaciones
                    )
                    lang_rep = "ESPAÑOL" if st.session_state.lang == "es" else "ENGLISH"
                    guia_fw = MARCOS_CURRICULARES[marco_sel]["guia"]
                    if marco_sel == "IB":
                        if nivel_in in (NIVELES_CANON[1], NIVELES_CANON[2]):
                            guia_fw += "\nNote: This student is in Primary/Early Years — reference IB PYP (PEP) only; do NOT mention CP or DP."
                        elif nivel_in == NIVELES_CANON[3]:
                            guia_fw += "\nNote: This student is in Lower Secondary — reference IB MYP (PAI) only; do NOT mention Career-related Programme (CP) or DP."
                        elif nivel_in == NIVELES_CANON[4]:
                            guia_fw += "\nNote: This student is in Upper Secondary — reference IB DP / CP appropriately."
                    elif marco_sel == "CUSTOM":
                        guia_fw = f"{guia_fw}\nCRITERIOS INSTITUCIONALES DEL DOCENTE:\n{custom_criteria.strip()}"

                    rep_system = (
                        f"Eres un especialista en evaluación formativa y redacción curricular de Aula Viva® — PRISMA™. "
                        f"Redacta EXCLUSIVAMENTE en {lang_rep} un reporte oficial, claro, humanista, conciso y listo para entregar en plataforma escolar o a familias. "
                        f"NO incluyas proceso de pensamiento, análisis previo ni preámbulos; empieza directamente con el contenido del reporte. "
                        f"NO devuelvas JSON ni bloques de código; entrega prosa clara con subtítulos breves (##) y viñetas donde aporte legibilidad. "
                        f"Ancla cada afirmación únicamente a las evidencias provistas; no inventes hechos ni calificaciones numéricas arbitrarias. "
                        f"REGLA DE ÉTICA DEL CUIDADO: Los semáforos AMARILLO y ROJO reflejan condiciones de educabilidad (fatiga somática, dolor, alimentación parcial o carga doméstica), JAMÁS mala conducta ni fallas morales. Si existió un episodio de frustración o desborde bajo semáforo amarillo o rojo, contextualízalo explícitamente con empatía señalando que la vulnerabilidad registrada pudo alimentar dicho episodio, sin estigmatizar al estudiante. Evita terminología clínica o alarmista (como 'High Risk' o 'alto riesgo'); describe los estados amarillo o rojo en lenguaje educativo y humano (como 'desgaste somático o personal elevado' / 'elevated somatic or personal strain'), reservando lenguaje de riesgo únicamente para alertas críticas.\n\n"
                        f"MARCO CURRICULAR SOLICITADO ({fw_nombre}):\n{guia_fw}"
                    )

                    rep_prompt = (
                        f"Periodo evaluativo: {periodo_in or ('Actual' if st.session_state.lang == 'es' else 'Current')}\n\n"
                        f"EXPEDIENTE ACUMULADO DEL ESTUDIANTE:\n{resumen_exp}\n\n"
                        f"Redacta ahora el informe oficial en {lang_rep} alineado a {fw_nombre}."
                    )

                    resp_rep = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": modelo_rep,
                            "system": rep_system,
                            "prompt": rep_prompt,
                            "think": False,
                            "options": {"temperature": 0.2, "num_predict": 3072, "num_ctx": 8192},
                            "stream": False
                        },
                        timeout=180
                    )
                    if resp_rep.status_code == 200:
                        texto_gen = limpiar_salida_llm(resp_rep.json().get("response", ""))
                        st.session_state.reporte_curricular_generado = {
                            "marco_key": marco_sel,
                            "marco_nombre": fw_nombre,
                            "periodo": periodo_in,
                            "lang": st.session_state.lang,
                            "texto": texto_gen
                        }
                        st.rerun()
                    else:
                        st.error(f"⚠️ HTTP {resp_rep.status_code} (Ollama).")
                except Exception as e:
                    st.error(f"⚠️ Error Ollama: {e}")

    if st.session_state.reporte_curricular_generado and not alerta_critica_activa:
        rep_obj = st.session_state.reporte_curricular_generado
        with st.container(border=True):
            st.markdown(t("report_ready_title"))
            texto_editado = st.text_area(
                t("report_copy_label"),
                value=rep_obj["texto"],
                height=280,
                key="editor_reporte_curricular",
                disabled=bloqueo_ui
            )
            st.session_state.reporte_curricular_generado["texto"] = texto_editado

            col_rd1, col_rd2 = st.columns([0.65, 0.35])
            with col_rd1:
                if DOCX_DISPONIBLE:
                    docx_bytes = generar_docx_reporte(
                        nom_in, mat_in, grp_in, nivel_in, materia_in,
                        rep_obj["marco_nombre"], rep_obj["periodo"],
                        texto_editado, st.session_state.valores_db, rep_obj.get("lang", st.session_state.lang)
                    )
                    fn_docx = f"{datetime.now().strftime('%y%m%d')}_{limpiar_cadena(nom_in)}_{rep_obj['marco_key']}_PRISMA.docx"
                    st.download_button(
                        label=t("btn_dl_docx"),
                        data=docx_bytes,
                        file_name=fn_docx,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        disabled=bloqueo_ui
                    )
                else:
                    st.warning(t("docx_missing"))
            with col_rd2:
                if st.button(t("btn_clear_report"), use_container_width=True, disabled=bloqueo_ui):
                    st.session_state.reporte_curricular_generado = None
                    st.rerun()


# --- COLUMNA DERECHA: ESPEJO METACOGNITIVO Y RADAR (FONDO TRANSPARENTE ADAPTABLE) ---
with col_der:
    st.markdown('<div class="sticky-radar-container">', unsafe_allow_html=True)
    st.subheader(t("radar_header"))

    modo_vis_key = st.radio(
        "Vis",
        options=["all", "custom"],
        format_func=lambda k: t("vis_all") if k == "all" else t("vis_custom"),
        horizontal=True,
        key="modo_vis_key",
        disabled=bloqueo_ui,
        label_visibility="collapsed"
    )

    tiene_ciclos_previos = any(obs.get("tipo") == "TABULA_RASA" for obs in st.session_state.historial_observaciones)
    label_historico = t("hist_chk") if es_admin else f"{t('hist_chk')} 🔒"

    ver_historico = st.checkbox(
        label_historico,
        disabled=not (es_admin and tiene_ciclos_previos) or bloqueo_ui,
        value=False,
        help=t("hist_chk_help")
    )

    nombre_tit = st.session_state.input_nombre.strip()
    grupo_tit = st.session_state.input_grupo.strip()
    if nombre_tit and grupo_tit:
        id_estudiante = f"{nombre_tit} ({grupo_tit})"
    elif nombre_tit:
        id_estudiante = nombre_tit
    elif grupo_tit:
        id_estudiante = grupo_tit
    else:
        id_estudiante = ""

    titulo_radar_unico = f"{t('radar_map_title')} — {id_estudiante}" if id_estudiante else t("radar_map_title")

    valores_live = {eje: float(st.session_state.valores_db[eje]) for eje in EJE_NOMBRES}
    ejes_etiquetados = [FORMATO_EJES_RADAR[st.session_state.lang][eje] for eje in EJE_NOMBRES]
    angles_8 = list(range(0, 360, 45)) + [360]
    angles_360 = np.linspace(0, 360, 361)

    hitos_activos = []
    paso_tabula = False
    for obs in st.session_state.historial_observaciones:
        if obs.get("tipo") == "TABULA_RASA":
            paso_tabula = True
            continue
        if paso_tabula or not tiene_ciclos_previos:
            hitos_activos.append(obs)

    hitos_a_dibujar = st.session_state.historial_observaciones if (ver_historico and es_admin) else hitos_activos

    deltas_p_tot_calc = obtener_deltas_ia_pendientes()
    todos_vectores = [list(valores_live.values())]
    for obs in hitos_a_dibujar:
        if "vector_snapshot" in obs:
            todos_vectores.append([float(obs["vector_snapshot"].get(eje, 0.0)) for eje in EJE_NOMBRES])
    if st.session_state.analisis_pendiente and not alerta_critica_activa:
        todos_vectores.append([round(valores_live[eje] + deltas_p_tot_calc.get(eje, 0.0), 1) for eje in EJE_NOMBRES])
    if st.session_state.previsualizacion_manual and not alerta_critica_activa:
        todos_vectores.append([
            round(valores_live[eje] + deltas_p_tot_calc.get(eje, 0.0) + st.session_state.previsualizacion_manual.get(eje, 0.0), 1)
            for eje in EJE_NOMBRES
        ])

    max_valor_global = max([val for vec in todos_vectores for val in vec] + [0.0])
    limite_radar = 6.0 if max_valor_global <= 6.0 else (12.0 if max_valor_global <= 12.0 else (18.0 if max_valor_global <= 18.0 else 24.0))

    fig = go.Figure()

    def agregar_orbita_circular(fig_obj, r_val, nombre, color="rgba(148, 163, 184, 0.55)", width=1.4, dash="solid"):
        fig_obj.add_trace(go.Scatterpolar(
            r=[r_val] * 361,
            theta=angles_360,
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            name=nombre,
            hoverinfo="skip"
        ))

    agregar_orbita_circular(fig, 0.0, t("orb_0"), color="rgba(148, 163, 184, 0.85)", width=1.8)
    agregar_orbita_circular(fig, 6.0, t("orb_6"), color="rgba(148, 163, 184, 0.60)", width=1.6 if limite_radar == 6.0 else 1.2)
    if limite_radar >= 12.0:
        agregar_orbita_circular(fig, 12.0, t("orb_12"), color="rgba(148, 163, 184, 0.60)", width=1.6 if limite_radar == 12.0 else 1.2)
    if limite_radar >= 18.0:
        agregar_orbita_circular(fig, 18.0, t("orb_18"), color="rgba(148, 163, 184, 0.60)", width=1.6 if limite_radar == 18.0 else 1.2)
    if limite_radar >= 24.0:
        agregar_orbita_circular(fig, 24.0, t("orb_24"), color="rgba(148, 163, 184, 0.75)", width=1.6)

    num_hitos = len(hitos_a_dibujar)
    PALETA_COLORES = [
        ("rgba(236, 72, 153, 0.85)", "rgba(236, 72, 153, 0.14)"),
        ("rgba(168, 85, 247, 0.85)", "rgba(168, 85, 247, 0.16)"),
        ("rgba(59, 130, 246, 0.90)", "rgba(59, 130, 246, 0.18)"),
        ("rgba(16, 185, 129, 0.90)", "rgba(16, 185, 129, 0.20)"),
        ("rgba(99, 102, 241, 1.00)", "rgba(99, 102, 241, 0.32)")
    ]

    sin_staging = (st.session_state.analisis_pendiente is None and st.session_state.previsualizacion_manual is None)

    if modo_vis_key == "all":
        if num_hitos > 0:
            for i, obs in enumerate(hitos_a_dibujar):
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [float(v_snap.get(eje, 0.0)) for eje in EJE_NOMBRES]
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                is_last = (i == num_hitos - 1) and sin_staging
                tipo_hito = obs.get("tipo", "IA")
                tag_tipo = "PRISMA" if tipo_hito == "IA" else ("Manual" if tipo_hito == "MANUAL" else ("Alert" if tipo_hito == "ALERTA_CRITICA" else "Meta"))
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=angles_8,
                    fill="toself" if is_last else "none",
                    fillcolor=color_fill,
                    line=dict(color=color_line, width=3 if is_last else 1.8, dash="solid" if is_last else "dot"),
                    marker=dict(size=6, color=color_line),
                    name=f"#{i+1} [{tag_tipo}]",
                    hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
                ))
        else:
            vals = [valores_live[eje] for eje in EJE_NOMBRES]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=angles_8,
                fill="toself" if sin_staging else "none",
                fillcolor="rgba(99, 102, 241, 0.30)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#6366F1"),
                name=t("radar_current"),
                hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
            ))
    else:
        if num_hitos > 0:
            opciones_hitos = [f"#{i+1} [{obs.get('tipo', 'IA')}] — {obs.get('timestamp', '')}" for i, obs in enumerate(hitos_a_dibujar)]
            hitos_seleccionados = st.multiselect(
                t("radar_multiselect"),
                options=opciones_hitos,
                default=[opciones_hitos[-1]],
                disabled=bloqueo_ui
            )
            for idx_str in hitos_seleccionados:
                i = int(idx_str.split("#")[1].split(" ")[0]) - 1
                obs = hitos_a_dibujar[i]
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [float(v_snap.get(eje, 0.0)) for eje in EJE_NOMBRES]
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=angles_8,
                    fill="toself",
                    fillcolor=color_fill,
                    line=dict(color=color_line, width=2.5),
                    marker=dict(size=6, color=color_line),
                    name=f"#{i+1}",
                    hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
                ))
        else:
            vals = [valores_live[eje] for eje in EJE_NOMBRES]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=angles_8,
                fill="toself",
                fillcolor="rgba(99, 102, 241, 0.30)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#6366F1"),
                name=t("radar_current"),
                hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
            ))

    deltas_p_tot = obtener_deltas_ia_pendientes()
    if st.session_state.analisis_pendiente and not alerta_critica_activa:
        vals_proy = [round(valores_live[eje] + deltas_p_tot.get(eje, 0.0), 1) for eje in EJE_NOMBRES]
        fig.add_trace(go.Scatterpolar(
            r=vals_proy + [vals_proy[0]],
            theta=angles_8,
            fill="toself" if not st.session_state.previsualizacion_manual else "none",
            fillcolor="rgba(168, 85, 247, 0.16)",
            line=dict(color="#A855F7", width=2.5, dash="dot"),
            marker=dict(size=7, color="#A855F7"),
            name=t("radar_prev_ia"),
            hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
        ))

    if st.session_state.previsualizacion_manual and not alerta_critica_activa:
        vals_man = [round(valores_live[eje] + deltas_p_tot.get(eje, 0.0) + st.session_state.previsualizacion_manual.get(eje, 0.0), 1) for eje in EJE_NOMBRES]
        fig.add_trace(go.Scatterpolar(
            r=vals_man + [vals_man[0]],
            theta=angles_8,
            fill="toself",
            fillcolor="rgba(147, 51, 234, 0.22)",
            line=dict(color="#9333EA", width=2.8, dash="dash"),
            marker=dict(size=7, color="#9333EA"),
            name=t("radar_prev_man"),
            hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
        ))

    tick_vals_2db = list(range(-6, int(limite_radar) + 1, 2))
    tick_map = {0: "0 dB (1x)", 6: "+6 dB (2x)", 12: "+12 dB (4x)", 18: "+18 dB (8x)", 24: "+24 dB (16x)"}
    tick_texts_2db = [tick_map.get(tv, "") for tv in tick_vals_2db]

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        dragmode=False,
        modebar=dict(bgcolor="rgba(0,0,0,0)", color="#64748B", activecolor="#6366F1"),
        title=dict(
            text=f"<b>{titulo_radar_unico}</b>",
            x=0.5,
            xanchor="center",
            y=0.98,
            yanchor="top",
            font=dict(size=17)
        ),
        uirevision=f"radar_{limite_radar}_{st.session_state.lang}",
        polar=dict(
            bgcolor="rgba(148, 163, 184, 0.08)",
            domain=dict(x=[0.09, 0.91], y=[0.06, 0.89]),
            gridshape="circular",
            radialaxis=dict(
                visible=True,
                range=[-6, limite_radar],
                autorange=False,
                tickvals=tick_vals_2db,
                ticktext=tick_texts_2db,
                angle=22.5,
                gridcolor="rgba(148, 163, 184, 0.35)",
                gridwidth=0.8,
                tickfont=dict(size=9, color="#94A3B8")
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=list(range(0, 360, 45)),
                ticktext=ejes_etiquetados,
                tickfont=dict(size=10.5),
                rotation=90,
                direction="clockwise",
                gridcolor="rgba(148, 163, 184, 0.25)",
                linecolor="rgba(148, 163, 184, 0.45)"
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.14,
            xanchor="center",
            x=0.5,
            font=dict(size=10.0),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=495,
        margin=dict(l=64, r=64, t=48, b=56)
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        theme="streamlit",
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d", "pan2d", "select2d", "lasso2d",
                "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"
            ],
            "toImageButtonOptions": {
                "format": "png",
                "filename": f"PRISMA_R8_{limpiar_cadena(id_estudiante) if id_estudiante else 'Mapa'}",
                "height": 900,
                "width": 900,
                "scale": 2
            },
            "scrollZoom": False
        }
    )

    st.markdown('</div>', unsafe_allow_html=True)


# --- PIE DISCRETO: ALCANCE PEDAGÓGICO E IDENTIDAD ---
st.markdown(
    f"<div class='prisma-footer'>"
    f"<p class='prisma-footer-scope'>{t('scope_notice')}</p>"
    f"<p class='prisma-footer-brand'>{t('footer_brand')}</p>"
    f"</div>",
    unsafe_allow_html=True
)

# --- DESPLIEGUE DE DIÁLOGOS ---
if st.session_state.mostrar_modal_resguardo and st.session_state.input_nombre.strip() and not st.session_state.analisis_pendiente and not st.session_state.previsualizacion_manual and not st.session_state.meta_analisis_pendiente:
    modal_exportar_resguardo(
        st.session_state.input_nombre,
        st.session_state.input_matricula,
        st.session_state.input_grupo,
        st.session_state.input_nivel,
        st.session_state.input_materia
    )
elif st.session_state.mostrar_modal_confirmar_reiniciar:
    modal_confirmar_reiniciar()
