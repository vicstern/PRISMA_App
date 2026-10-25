PROMPT_PRISMA_SYSTEM = """Eres PRISMA-ENGINE, el sub-motor de analítica cualitativa del ecosistema AULA VIVA® (IMPI Exp. 3724582 / SSRN DOI: 10.2139/ssrn.7310080).

TU FUNCIÓN:
Actuar como un transductor cualitativo-vectorial. Recibes una observación cualitativa del docente sobre un estudiante, junto con los datos sociofisiológicos del Estado de Educabilidad y la ponderación de rúbrica, y debes traducirlos a deltas de ganancia/atenuación en decibeles (delta_db) en un espacio vectorial de 8 dimensiones (R8) y emitir un diagnóstico de educabilidad.

GRANULARIDAD DE MEDICIÓN:
- Utiliza incrementos continuos con resolución de 0.1 dB (ejemplo: +0.3, +1.2, +2.7, -0.8, -1.5 dB). NO te limites a saltos de 0.5 o números enteros.

PRINCIPIOS PEDAGÓGICOS Y EVALUACIÓN HUMANISTA:
1. CONDICIONANTES SOCIOFISIOLÓGICAS Y ESTADO DE EDUCABILIDAD:
   - Procesa los datos sociofisiológicos de entrada (Descanso / Sueño y Soporte Nutricional).
   - Genera un diagnóstico en el objeto "estado_educabilidad":
     * VERDE: Condición biológica estable / óptima.
     * AMARILLO: Tensión moderada (fatiga, descanso parcial 5-6h o alimento insuficiente).
     * ROJO: Vulnerabilidad severa (ayuno o descanso < 5h).
   - REGLA DE SUAVIZADO AUTÓNOMO (DAMPENING): Si detectas vulnerabilidad (AMARILLO o ROJO), ATENÚA AUTÓNOMAMENTE cualquier delta negativo en ejes cognitivos o técnicos. Por ejemplo, suaviza un delta que normalmente habría sido de -1.5 dB a -0.5 dB (Amarillo) o a 0.0 dB (Rojo). Explica explícitamente esta atenuación en el campo "razonamiento" como protección sociofisiológica.

2. DISTINCIÓN ENTRE ÉTICA Y REGULACIÓN SOCIOEMOCIONAL:
   - Una rabieta, llanto, grito o aislamiento derivado de exclusión social o frustración NO ES UNA FALTA ÉTICA. NUNCA penalices "Razonamiento_Etico" ni "Agencia_Intercultural" por episodios de desregulación emocional.
   - Penaliza "Resiliencia_Autogestion" (entre -0.5 y -4.0 dB) únicamente si hay episodios de frustración no regulada sin atenuación sociofisiológica.
   - Penaliza "Liderazgo_Colaborativo" (entre -0.5 y -3.0 dB) únicamente si la conducta interrumpe de forma activa la dinámica de trabajo del equipo.

3. RECONOCIMIENTO DE RESILIENCIA Y REINCORPORACIÓN:
   - Si el estudiante regresa a la actividad tras un episodio de frustración, reconoce el esfuerzo de reincorporación en "Resiliencia_Autogestion" o "Saber_Hacer_Ejecucion_Tecnica" con deltas positivos (+0.5 a +3.0 dB), equilibrando la lectura global.

4. SENSIBILIDAD A MICRO-EVIDENCIAS TÉCNICAS Y ORGANIZATIVAS:
   - Modificación de materiales, pruebas, corrección de errores -> +0.5 a +4.0 dB en "Saber_Hacer_Ejecucion_Tecnica" y/o "Pensamiento_Critico_Analitico".
   - Organización, mediación, repartición de tareas -> +0.5 a +4.0 dB en "Liderazgo_Colaborativo".

5. PONDERACIÓN DE CALIFICACIÓN ESCALAR TRADICIONAL (LÍNEA BASE):
   - Si la línea base es 90% - 100% (9.0-10.0): Dominio sobresaliente. Trata las observaciones negativas en el texto como detalles de pulido/refinamiento (deltas negativos mínimos de 0.0 a -0.2 dB).
   - Si la línea base es 75% - 89% (7.5-8.9): Desempeño sólido con brechas parciales de ejecución.
   - Si la línea base es 60% - 74% (6.0-7.4): Suficiencia límite (alerta de consolidación). Atenúa deltas positivos altos en ejecuciones parciales.
   - Si la línea base es < 60%: Reprobatorio / Brecha severa en la actividad.
   - Si no hay calificación escalar: Realiza evaluación formativa cualitativa pura.

6. REGLA DE EVALUACIÓN SOCIOFISIOLÓGICA Y SEMÁFORO N/A:
   - Si no se proporcionan datos de descanso/nutrición Y el texto de la nota tampoco menciona evidencias de vulnerabilidad biológica, responde estrictamente "semaforo": "N/A" y "advertencia_pedagogica": "Sin registro sociofisiológico (evaluación cualitativa pura)".
   - Si el texto menciona explícitamente fatiga, ayuno o desvelo, enciende el semáforo (AMARILLO o ROJO) de forma autónoma.

7. AXIOMA DE NEUTRALIDAD POR AUSENCIA DE EVIDENCIA (0.0 dB):
   - Si una nota narrativa no contiene evidencia explícita sobre un eje, asigna estrictamente 0.0 dB en ese eje.
   - NUNCA penalices con deltas negativos (ej. -0.2 dB) por "falta de evidencia" o "ausencia de dominio sobresaliente".
   - Asigna deltas negativos ÚNICAMENTE cuando exista evidencia narrativa explícita de un error conceptual, fallo técnico no atendido o desregulación que afecte la actividad.

8. REGISTRO ESTRICTO DE SEMÁFORO N/A:
   - Si la modalidad es "Sin registro" Y el texto narrativo tampoco describe fatiga, ayuno ni desvelo, el objeto "estado_educabilidad" DEBE responder estrictamente "semaforo": "N/A" y "advertencia_pedagogica": "Sin registro sociofisiológico (evaluación cualitativa pura)".

CONTRATO JSON OBLIGATORIO:
Responde ÚNICAMENTE en formato JSON válido. Usa EXACTAMENTE esta estructura de llaves.

ESTRUCTURA JSON EXCLUSIVA DE SALIDA:
{
  "estudiante": "Nombre",
  "estado_educabilidad": {
    "semaforo": "VERDE",
    "advertencia_pedagogica": "Descripción breve del estado y sugerencia de acompañamiento al docente"
  },
  "evaluacion_ejes": {
    "Indagacion_Investigacion": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Pensamiento_Critico_Analitico": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Razonamiento_Etico": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Agencia_Intercultural": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Liderazgo_Colaborativo": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Saber_Hacer_Ejecucion_Tecnica": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Resiliencia_Autogestion": {"delta_db": 0.0, "razonamiento": "motivo"},
    "Reflexion_Metacognitiva": {"delta_db": 0.0, "razonamiento": "motivo"}
  }
}
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import json
import requests
import os
import re
from datetime import datetime

# --- CONFIGURACIÓN Y ESTILOS DE INTERFAZ ---
st.set_page_config(
    page_title="Aula Viva® con IA — PRISMA",
    page_icon="🌌",
    layout="wide"
)

# Estilos CSS inyectados para fijar el mapa en la columna derecha y limitar su altura
st.markdown("""
<style>
    [data-testid="stColumn"]:nth-of-type(2) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 1rem !important;
        align-self: flex-start !important;
        z-index: 99;
    }
    .sticky-radar-container {
        max-height: calc(100vh - 2rem) !important;
        overflow-y: auto !important;
        padding-right: 0.5rem;
    }
    .stButton button {
        border-radius: 8px;
    }
    .staging-card {
        background-color: #F8FAFC;
        border: 1.5px solid #6366F1;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .manual-staging-card {
        background-color: #FAF5FF;
        border: 1.5px solid #A855F7;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("Aula Viva® con IA — PRISMA")
st.markdown("### Plataforma de Reflexión e Interpretación para el Seguimiento Multidimensional del Aprendizaje")
st.caption("Analítica cualitativa vectorizada en ℝ⁸ | Aula Viva® con IA | Ecosistema ASPIRE®")

DIR_EXPEDIENTES = os.path.expanduser("~/PRISMA_App/expedientes")
os.makedirs(DIR_EXPEDIENTES, exist_ok=True)

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

FORMATO_EJES_RADAR = {
    "Indagación e investigación": "Indagación e<br>investigación",
    "Pensamiento crítico y analítico": "Pensamiento crítico<br>y analítico",
    "Razonamiento ético": "Razonamiento<br>ético",
    "Agencia intercultural": "Agencia<br>intercultural",
    "Liderazgo colaborativo": "Liderazgo<br>colaborativo",
    "Saber hacer y ejecución técnica": "Saber hacer y<br>ejecución técnica",
    "Resiliencia y autogestión": "Resiliencia y<br>autogestión",
    "Reflexión metacognitiva": "Reflexión<br>metacognitiva"
}

EJE_NOMBRES = list(MAPEO_EJES.values())

def fmt_db(val):
    if abs(val) < 0.01:
        return "0.0"
    return f"{val:+.1f}"

def limpiar_cadena(texto):
    if not texto:
        return "Anonimo"
    cadena = re.sub(r"[^\w\s-]", "", texto).strip()
    return re.sub(r"[-\s]+", "_", cadena)

def parsear_nota_multihito(texto):
    patron = r'(?:^|\n)\s*(\d+[\.\)\-]\s*)'
    partes = re.split(patron, texto.strip())
    
    if len(partes) > 2:
        hitos = []
        for i in range(1, len(partes), 2):
            prefix = partes[i]
            contenido = partes[i+1].strip() if (i+1) < len(partes) else ""
            if contenido:
                hitos.append(f"{prefix}{contenido}")
        if hitos:
            return hitos
    return [texto.strip()]

# --- INICIALIZACIÓN Y CONTROL DE ESTADO LIMPIO ---
if "valores_db" not in st.session_state:
    st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}

if "historial_observaciones" not in st.session_state:
    st.session_state.historial_observaciones = []

if "analisis_pendiente" not in st.session_state:
    st.session_state.analisis_pendiente = None

if "previsualizacion_manual" not in st.session_state:
    st.session_state.previsualizacion_manual = None

if "procesando" not in st.session_state:
    st.session_state.procesando = False

if "estudiantes_db" not in st.session_state:
    st.session_state.estudiantes_db = {}

if "mostrar_modal_resguardo" not in st.session_state:
    st.session_state.mostrar_modal_resguardo = False

if "mostrar_modal_confirmar_reiniciar" not in st.session_state:
    st.session_state.mostrar_modal_confirmar_reiniciar = False

if "input_clave_admin" not in st.session_state:
    st.session_state.input_clave_admin = ""

# Banderas de limpieza diferida de estado
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

if "input_nombre" not in st.session_state:
    st.session_state.input_nombre = ""
if "input_matricula" not in st.session_state:
    st.session_state.input_matricula = ""
if "input_grupo" not in st.session_state:
    st.session_state.input_grupo = ""
if "input_nota" not in st.session_state:
    st.session_state.input_nota = ""
if "input_justificacion" not in st.session_state:
    st.session_state.input_justificacion = ""

# Sincronizadores bidireccionales para calibración manual
def sync_slider_a_num(eje_nombre):
    st.session_state[f"num_{eje_nombre}"] = float(st.session_state[f"slider_{eje_nombre}"])

def sync_num_a_slider(eje_nombre):
    st.session_state[f"slider_{eje_nombre}"] = float(st.session_state[f"num_{eje_nombre}"])

for eje in EJE_NOMBRES:
    if f"slider_{eje}" not in st.session_state:
        st.session_state[f"slider_{eje}"] = 0.0
    if f"num_{eje}" not in st.session_state:
        st.session_state[f"num_{eje}"] = 0.0

# --- FUNCIONES DE PERSISTENCIA ---
def guardar_expediente_disco(nombre, matricula, grupo, ciclo_id="2026", es_cierre=False):
    fecha_iso = datetime.now().strftime("%y%m%d")
    hora_iso = datetime.now().strftime("%H%M%S")
    nom_clean = limpiar_cadena(nombre)
    grp_clean = limpiar_cadena(grupo)
    ciclo_clean = limpiar_cadena(ciclo_id)
    
    n_h = len(st.session_state.historial_observaciones)
    hito_str = f"_Hito{n_h:02d}" if n_h > 0 else ""
    
    sufijo = f"CIERRE_{ciclo_clean}.json" if es_cierre else f"{hito_str}_PRISMA.json"
    filename = f"{fecha_iso}_{hora_iso}_{nom_clean}_{grp_clean}{sufijo}"
    filepath = os.path.join(DIR_EXPEDIENTES, filename)
    
    exp_data = {
        "tipo_archivo": "CIERRE_CICLO" if es_cierre else "EXPEDIENTE_ACTIVO",
        "ciclo_escolar": ciclo_id,
        "estudiante": nombre,
        "matricula": matricula,
        "grupo": grupo,
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vector_actual_db": dict(st.session_state.valores_db),
        "historial_observaciones": list(st.session_state.historial_observaciones)
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(exp_data, f, indent=2, ensure_ascii=False)
    return filename, exp_data

# --- DIÁLOGOS DE CONTROL (MODALES) ---
@st.dialog("💾 Resguardo de expediente vectorial")
def modal_exportar_resguardo(nombre, matricula, grupo):
    nombre_mostrar = nombre if nombre else "Estudiante"
    st.write(f"Se ha consolidado el hito en el expediente de **{nombre_mostrar}**.")
    st.write("¿Deseas descargar una copia de resguardo local (`.json`) con marca de tiempo?")
    
    filename_export, exp_data = guardar_expediente_disco(nombre, matricula, grupo)
    
    col_m1, col_m2 = st.columns([0.6, 0.4])
    with col_m1:
        if st.download_button(
            label="Sí, descargar (.json)",
            data=json.dumps(exp_data, indent=2, ensure_ascii=False),
            file_name=filename_export,
            mime="application/json",
            type="primary",
            use_container_width=True
        ):
            st.session_state.mostrar_modal_resguardo = False
            st.rerun()
            
    with col_m2:
        if st.button("No por ahora", use_container_width=True):
            st.session_state.mostrar_modal_resguardo = False
            st.rerun()

@st.dialog("⚠️ Confirmar reinicio de pantalla")
def modal_confirmar_reiniciar():
    st.write("Esta acción limpiará los datos del estudiante, notas y el vector activo en pantalla.")
    st.write("¿Deseas descargar un resguardo en `.json` antes de limpiar?")
    
    nombre = st.session_state.input_nombre
    matricula = st.session_state.input_matricula
    grupo = st.session_state.input_grupo
    filename_export, exp_data = guardar_expediente_disco(nombre, matricula, grupo)

    if st.download_button(
        label="💾 Descargar resguardo (.json) y reiniciar",
        data=json.dumps(exp_data, indent=2, ensure_ascii=False),
        file_name=filename_export,
        mime="application/json",
        type="primary",
        use_container_width=True
    ):
        st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
        st.session_state.historial_observaciones = []
        st.session_state.analisis_pendiente = None
        st.session_state.previsualizacion_manual = None
        st.session_state.procesando = False
        st.session_state.input_nombre = ""
        st.session_state.input_matricula = ""
        st.session_state.input_grupo = ""
        st.session_state.flag_limpiar_nota = True
        st.session_state.flag_limpiar_justificacion = True
        st.session_state.flag_reset_calib = True
        st.session_state.mostrar_modal_confirmar_reiniciar = False
        st.rerun()
    
    st.markdown("---")
    col_r1, col_r2 = st.columns([0.5, 0.5])
    with col_r1:
        if st.button("🗑️ Reiniciar sin descargar", type="secondary", use_container_width=True):
            st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
            st.session_state.historial_observaciones = []
            st.session_state.analisis_pendiente = None
            st.session_state.previsualizacion_manual = None
            st.session_state.procesando = False
            st.session_state.input_nombre = ""
            st.session_state.input_matricula = ""
            st.session_state.input_grupo = ""
            st.session_state.flag_limpiar_nota = True
            st.session_state.flag_limpiar_justificacion = True
            st.session_state.flag_reset_calib = True
            st.session_state.mostrar_modal_confirmar_reiniciar = False
            st.rerun()
    with col_r2:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.mostrar_modal_confirmar_reiniciar = False
            st.rerun()

# --- SIDEBAR: OPERACIÓN Y CONTROLES DE ADMINISTRADOR ---
with st.sidebar:
    st.header("⚙️ Gestión de registro")
    
    st.subheader("1. Flujo de trabajo")
    if st.button("✨ Reiniciar pantalla de registro", use_container_width=True, type="primary", disabled=st.session_state.procesando):
        st.session_state.mostrar_modal_confirmar_reiniciar = True
        st.rerun()

    st.markdown("---")
    
    st.header("🔒 Herramientas de administrador")
    
    clave_admin_input = st.text_input(
        "🔑 Clave de administrador:",
        type="password",
        key="input_clave_admin",
        placeholder="Ingresa clave de acceso",
        disabled=st.session_state.procesando,
        help="Habilita la carga de expedientes y la transición de ciclo escolar."
    )
    
    es_admin = (st.session_state.input_clave_admin in ["prisma2026", "prisma26"])
    
    if es_admin:
        st.success("Acceso concedido — Modo Administrador")
        if st.button("🔴 Salir del modo administrador", use_container_width=True, disabled=st.session_state.procesando):
            st.session_state.input_clave_admin = ""
            st.rerun()
    else:
        st.info("Funciones avanzadas reservadas para Admin")

    st.markdown("---")
    
    label_carga = "2. Cargar expediente (.json)" if es_admin else "2. Cargar expediente (.json) 🔒 Admin"
    st.subheader(label_carga)
    archivo_cargado = st.file_uploader(
        "Selecciona expediente JSON:",
        type=["json"],
        disabled=(not es_admin or st.session_state.procesando),
        help="Carga de expedientes históricos" if es_admin else "Función exclusiva para nivel Administrador"
    )
    
    btn_importar = st.button("📥 Cargar expediente", disabled=(not es_admin or archivo_cargado is None or st.session_state.procesando), use_container_width=True)
    if btn_importar and archivo_cargado is not None and es_admin:
        try:
            datos = json.load(archivo_cargado)
            st.session_state.valores_db = datos.get("vector_actual_db", {eje: 0.0 for eje in EJE_NOMBRES})
            st.session_state.historial_observaciones = datos.get("historial_observaciones", [])
            st.session_state.input_nombre = datos.get("estudiante", "")
            st.session_state.input_matricula = datos.get("matricula", "")
            st.session_state.input_grupo = datos.get("grupo", "")
            
            if datos.get("matricula"):
                st.session_state.estudiantes_db[datos["matricula"]] = {
                    "nombre": datos.get("estudiante", ""),
                    "grupo": datos.get("grupo", "")
                }
            st.success("Expediente cargado correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al leer el archivo JSON: {e}")

    st.markdown("---")
    
    label_tabula = "3. Transición: 'Año nuevo, vida nueva'" if es_admin else "3. Transición: 'Año nuevo, vida nueva' 🔒 Admin"
    st.subheader(label_tabula)
    st.caption("Aplica 'Tabula Rasa': congela el ciclo actual en un JSON de cierre y restablece el vector a 0.0 dB registrando la transición.")
    
    ciclo_id_input = st.text_input(
        "Identificador del ciclo a cerrar:",
        value=f"{datetime.now().year}-1",
        disabled=(not es_admin or st.session_state.procesando),
        help="Ejemplos: 2026-1, 2026-2, 2025-2026"
    )
    
    btn_tabula = st.button("🔄 Ejecutar 'Año nuevo, vida nueva'", disabled=(not es_admin or st.session_state.procesando), use_container_width=True)
    if btn_tabula and es_admin:
        nom_a = st.session_state.input_nombre
        mat_a = st.session_state.input_matricula
        grp_a = st.session_state.input_grupo
        
        fn_cierre, _ = guardar_expediente_disco(nom_a, mat_a, grp_a, ciclo_id=ciclo_id_input, es_cierre=True)
        
        st.session_state.historial_observaciones.append({
            "tipo": "TABULA_RASA",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "justificacion": f"Cierre de ciclo escolar '{ciclo_id_input}' ('Año nuevo, vida nueva'). Resguardado en {fn_cierre}. Vector restablecido a 0.0 dB.",
            "vector_snapshot": dict(st.session_state.valores_db)
        })
        st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
        st.success(f"Transición registrada y ciclo congelado en `{fn_cierre}`. Vector restablecido a 0.0 dB.")
        st.rerun()

# --- LAYOUT PRINCIPAL ---
col_izq, col_der = st.columns([0.45, 0.55])

with col_izq:
    st.subheader("1. Ficha del estudiante y registro")
    
    col_f1, col_f2, col_f3 = st.columns([0.35, 0.4, 0.25])
    
    with col_f2:
        mat_in = st.text_input("Matrícula ID:", key="input_matricula", placeholder="Ej: A012345", disabled=st.session_state.procesando)
        if mat_in in st.session_state.estudiantes_db:
            st.session_state.input_nombre = st.session_state.estudiantes_db[mat_in]["nombre"]
            st.session_state.input_grupo = st.session_state.estudiantes_db[mat_in]["grupo"]

    with col_f1:
        nom_in = st.text_input("Nombre del estudiante:", key="input_nombre", placeholder="Nombre_Apellido", disabled=st.session_state.procesando)
        if mat_in and nom_in:
            st.session_state.estudiantes_db[mat_in] = {
                "nombre": nom_in,
                "grupo": st.session_state.input_grupo
            }
            
    with col_f3:
        grp_in = st.text_input("Grupo:", key="input_grupo", placeholder="Grupo", disabled=st.session_state.procesando)

    st.markdown("---")
    st.subheader("2. Registro de Nota Narrativa Docente")
    st.markdown("##### Nota de Estado de Educabilidad")
    tipo_reg = st.radio("Registro de educabilidad:", ["Sin registro", "Con registro"], horizontal=True, key="input_educabilidad_modo")
    
    if tipo_reg == "Con registro":
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.selectbox("Sueño / Descanso:", ["> 7 horas (Óptimo)", "5 - 6 horas (Atención / Fatiga)", "< 5 horas (Vulnerabilidad Severa)"], key="input_descanso")
        with col_e2:
            st.selectbox("Alimentación / Nutrición:", ["Completa / Adecuada", "Insuficiente / Parcial", "Sin Alimento / Ayuno"], key="input_alimentacion")
    
    st.markdown("---")
    st.subheader("2. Registro de Nota Narrativa Docente")
    st.markdown("##### Nota de Estado de Educabilidad")

    st.markdown("---")
    st.number_input(
        "Calificación escalar (opcional: 0.0 - 10.0 o 0 - 100)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
        format="%.1f",
        key="input_nota_escalar",
        disabled=st.session_state.procesando,
        help="Ingresa la nota tradicional de la actividad. Si es <= 10.0 se tratará en base 10; si es > 10.0 en base 100."
    )
    
    with st.form(key="form_nota_docente", clear_on_submit=False):
        nota_docente = st.text_area(
            "Dictado / Nota narrativa del docente:",
            key="input_nota",
            height=130,
            disabled=st.session_state.procesando,
            placeholder="Ingresa la observación cualitativa (puedes incluir notas numeradas 1, 2, 3). Presiona Cmd+Enter o Ctrl+Enter para procesar."
        )
        btn_analizar = st.form_submit_button(
            "⚡ Ejecutar análisis de nota" if not st.session_state.procesando else "⏳ Procesando inferencia...",
            type="primary",
            use_container_width=True,
            disabled=st.session_state.procesando
        )

    if btn_analizar and not st.session_state.procesando:
        if not nom_in.strip():
            st.error("⚠️ Por favor ingresa el nombre del estudiante antes de procesar.")
        elif not grp_in.strip():
            st.error("⚠️ Por favor ingresa el grupo del estudiante antes de procesar.")
        elif not nota_docente.strip():
            st.error("⚠️ Por favor ingresa una nota de observación cualitativa.")
        else:
            sub_hitos = parsear_nota_multihito(nota_docente)
            st.session_state.procesando = True
            st.rerun()

    # Proceso activo de inferencia multi-hito
    if st.session_state.procesando and st.session_state.input_nota.strip():
        sub_hitos = parsear_nota_multihito(st.session_state.input_nota)
        with st.spinner(f"Procesando inferencia cualitativa en ℝ⁸ con PRISMA-Engine ({len(sub_hitos)} hito/s)..."):
            try:
                resultados_multihito = []
                for idx_h, texto_h in enumerate(sub_hitos, 1):
                    prefix_edu = ""
                    if st.session_state.get("input_educabilidad_modo") == "Con registro":
                        sueno_val = st.session_state.get("input_descanso", "N/A")
                        nutri_val = st.session_state.get("input_alimentacion", "N/A")
                        prefix_edu += f"Datos de educabilidad: Sueño: {sueno_val}, Soporte Nutricional: {nutri_val}.\n"

                    # Normalización e Inyección de Calificación Escalar
                    nota_esc = st.session_state.get("input_nota_escalar", 0.0)
                    if nota_esc > 0.0:
                        if nota_esc <= 10.0:
                            base_pct = nota_esc * 10.0
                            str_escalar = f"{nota_esc:.1f}/10 (Línea base: {base_pct:.0f}%)"
                        else:
                            str_escalar = f"{nota_esc:.1f}/100 (Línea base: {nota_esc:.0f}%)"
                        prefix_edu += f"Calificación Escalar Tradicional de Rúbrica: {str_escalar}.\n"
                    else:
                        prefix_edu += "Calificación Escalar Tradicional: Sin registro (Evaluación cualitativa pura).\n"

                    user_prompt = f"Estudiante: {nom_in}\n{prefix_edu}Nota narrativa: \"{texto_h}\""
                    
                    payload = {
                        "model": st.session_state.get("modelo_activo", "prisma-engine"),
                        "system": PROMPT_PRISMA_SYSTEM,
                        "prompt": user_prompt,
                        "format": "json",
                        "options": {"temperature": 0.0},
			"stream": False
                    }
                    
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json=payload,
                        timeout=120
                    )
                    if response.status_code == 200:
                        res_json = json.loads(response.json()["response"])
                        eval_ejes = res_json.get("evaluacion_ejes", {})
                        deltas_h = {}
                        for c_j, n_eje in MAPEO_EJES.items():
                            if c_j in eval_ejes:
                                deltas_h[n_eje] = float(eval_ejes[c_j].get("delta_db", 0.0))
                        
                        resultados_multihito.append({
                            "sub_idx": idx_h,
                            "nota": texto_h,
                            "deltas": deltas_h,
                            "resultado_ia": res_json
                        })
                    else:
                        st.error(f"Error HTTP {response.status_code} al procesar hito {idx_h}")
                        break
                        
                if len(resultados_multihito) == len(sub_hitos):
                    st.session_state.analisis_pendiente = {
                        "modo": "MULTIHITO" if len(sub_hitos) > 1 else "SIMPLE",
                        "hitos": resultados_multihito
                    }
            except Exception as e:
                st.error(f"Error de conexión con Ollama local: {e}")
            finally:
                st.session_state.procesando = False
                st.rerun()

    if st.button("💾 Exportar Expediente (.json)", use_container_width=True, disabled=st.session_state.procesando):
        if not nom_in.strip() or not grp_in.strip():
            st.error("⚠️ Por favor ingresa el nombre y grupo del estudiante antes de exportar.")
        else:
            fname, edata = guardar_expediente_disco(
                st.session_state.input_nombre,
                st.session_state.input_matricula,
                st.session_state.input_grupo
            )
            st.download_button(
                label="Descargar archivo generado",
                data=json.dumps(edata, indent=2, ensure_ascii=False),
                file_name=fname,
                mime="application/json",
                use_container_width=True
            )

    # --- STAGING / PREVISUALIZACIÓN DE IA ---
    if st.session_state.analisis_pendiente:
        st.markdown('<div class="staging-card">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Previsualización del análisis de la IA")
        
        hitos_p = st.session_state.analisis_pendiente["hitos"]
        st.caption(f"Se detectaron **{len(hitos_p)} hito/s cualitativo/s** en la nota docente.")
        
        deltas_acum_totales = {eje: 0.0 for eje in EJE_NOMBRES}
        
        for item in hitos_p:
            res_ia = item.get("resultado_ia", {})
            est_educ = res_ia.get("estado_educabilidad", {})
            semaforo = str(est_educ.get("semaforo", "VERDE")).upper()
            adv_pedag = est_educ.get("advertencia_pedagogica", "")

            if "ROJO" in semaforo:
                st.error(f"🔴 **Semáforo ROJO — Alerta de Educabilidad:** {adv_pedag}")
            elif "AMARILLO" in semaforo:
                st.warning(f"🟡 **Semáforo AMARILLO — Atención Pedagógica:** {adv_pedag}")
            elif "VERDE" in semaforo:
                st.success(f"🟢 **Semáforo VERDE — Condición Óptima:** {adv_pedag or 'Sin restricciones sociofisiológicas activas.'}")
            # Si es "N/A", simplemente no se dibuja ninguna tarjeta verde


            if len(hitos_p) > 1:
                st.markdown(f"**• Hito {item['sub_idx']}:** *\"{item['nota']}\"*")
            
            res_ejes = item["resultado_ia"].get("evaluacion_ejes", {})
            for c_j, n_eje in MAPEO_EJES.items():
                d_val = item["deltas"].get(n_eje, 0.0)
                deltas_acum_totales[n_eje] += d_val
                if abs(d_val) > 0.01:
                    razon = res_ejes.get(c_j, {}).get("razonamiento", "")
                    st.write(f"  └ **{n_eje}:** `{fmt_db(d_val)} dB` — *{razon}*")
                    
        st.markdown("---")
        col_s1, col_s2, col_s3 = st.columns([0.35, 0.3, 0.35])
        
        with col_s1:
            if st.button("✅ Aceptar y Registrar Hito(s)", type="primary", use_container_width=True, disabled=st.session_state.procesando):
                for item in hitos_p:
                    for eje, d_val in item["deltas"].items():
                        st.session_state.valores_db[eje] += d_val
                    
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
                
                guardar_expediente_disco(nom_in, mat_in, grp_in)
                st.session_state.mostrar_modal_resguardo = True
                st.rerun()
                
        with col_s2:
            if st.button("🎨 Ajustar Manualmente", use_container_width=True, disabled=st.session_state.procesando):
                for eje, d_val in deltas_acum_totales.items():
                    val_f = float(d_val)
                    st.session_state[f"slider_{eje}"] = val_f
                    st.session_state[f"num_{eje}"] = val_f
                st.session_state.analisis_pendiente = None
                st.rerun()
                
        with col_s3:
            if st.button("❌ Rechazar análisis", use_container_width=True, disabled=st.session_state.procesando):
                st.session_state.analisis_pendiente = None
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- META-ANÁLISIS DE TRAYECTORIA (DOCENTE/USUARIO) ---
    st.markdown("---")
    st.subheader("3. Meta-Análisis de Trayectoria")
    st.caption("Evaluación holística multidimensional recomendada por PRISMA.")
    
    if st.button("🌌 Meta-Análisis PRISMA", use_container_width=True, disabled=st.session_state.procesando):
        if not nom_in.strip() or not grp_in.strip():
            st.error("⚠️ Por favor completa el Nombre y Grupo del estudiante antes de ejecutar el Meta-Análisis.")
        elif len(st.session_state.historial_observaciones) < 2:
            st.warning("⚠️ Se requieren al menos 2 hitos acumulados para realizar un Meta-Análisis de Trayectoria.")
        else:
            with st.spinner("Analizando trayectoria multidimensional integral en ℝ⁸ (PRISMA-Engine)..."):
                try:
                    summary_prompt = f"Evaluación holística de trayectoria en R8 para {nom_in}:\nVector Acumulado Actual: {json.dumps(st.session_state.valores_db)}\nTotal de hitos evaluados: {len(st.session_state.historial_observaciones)}"
                    
                    response_meta = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "prisma-engine",
                            "prompt": f"MODO_META_ANALISIS: {summary_prompt}",
                            "stream": False,
                            "format": "json"
                        },
                        timeout=120
                    )
                    if response_meta.status_code == 200:
                        meta_res = json.loads(response_meta.json()["response"])
                        eval_meta = meta_res.get("evaluacion_ejes", meta_res)
                        
                        st.info("🌌 **Diagnóstico Holístico Sugerido por PRISMA:**")
                        
                        diag_gen = meta_res.get("diagnostico_general", meta_res.get("resumen", ""))
                        if diag_gen:
                            st.write(f"*{diag_gen}*")
                            
                        overrides_sugeridos = {}
                        if isinstance(eval_meta, dict):
                            for c_j, n_eje in MAPEO_EJES.items():
                                if c_j in eval_meta:
                                    item_m = eval_meta[c_j]
                                    delta_m = float(item_m.get("delta_db", 0.0)) if isinstance(item_m, dict) else 0.0
                                    razon_m = item_m.get("razonamiento", "") if isinstance(item_m, dict) else str(item_m)
                                    overrides_sugeridos[n_eje] = delta_m
                                    st.write(f"• **{n_eje}:** `{fmt_db(delta_m)} dB` — {razon_m if razon_m else 'Sin observaciones adicionales'}")
                        
                        if st.button("Aceptar y registrar Meta-Análisis PRISMA como Hito", disabled=st.session_state.procesando):
                            for eje, d_m in overrides_sugeridos.items():
                                st.session_state.valores_db[eje] += d_m
                                
                            st.session_state.historial_observaciones.append({
                                "tipo": "META_ANALISIS",
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "justificacion": "Ajuste holístico de trayectoria por Meta-Análisis PRISMA.",
                                "deltas": overrides_sugeridos,
                                "resultado_ia": meta_res,
                                "vector_snapshot": dict(st.session_state.valores_db)
                            })
                            guardar_expediente_disco(nom_in, mat_in, grp_in)
                            st.rerun()
                    else:
                        st.error("No se pudo obtener la respuesta del Meta-Análisis.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # --- HISTORIAL DE HITOS ACUMULADOS ---
    if st.session_state.historial_observaciones:
        st.markdown("---")
        st.subheader(f"📋 Historial de hitos acumulados ({len(st.session_state.historial_observaciones)})")
        
        for idx, obs in enumerate(reversed(st.session_state.historial_observaciones), 1):
            num_obs = len(st.session_state.historial_observaciones) - idx + 1
            tipo_hito = obs.get("tipo", "IA")
            
            if tipo_hito == "IA":
                etiqueta_tipo = "🌌 Inferencia PRISMA"
            elif tipo_hito == "MANUAL":
                etiqueta_tipo = "🎨 Calibración manual docente"
            elif tipo_hito == "META_ANALISIS":
                etiqueta_tipo = "🌌 Meta-Análisis PRISMA"
            else:
                etiqueta_tipo = "🔄 Transición: Año nuevo, vida nueva"
                
            ts = obs.get("timestamp", "")
            
            with st.expander(f"Hito #{num_obs} — {ts} [{etiqueta_tipo}]", expanded=(num_obs == len(st.session_state.historial_observaciones))):
                if tipo_hito in ["IA", "META_ANALISIS"]:
                    if "nota" in obs:
                        st.write(f"**Nota narrativa docente:** *\"{obs['nota']}\"*")
                    
                    st.markdown("**Desglose e Inferencia de PRISMA:**")
                    eval_ejes = obs.get("resultado_ia", {}).get("evaluacion_ejes", {})
                    hubo_cambios = False
                    if isinstance(eval_ejes, dict):
                        for clave_json, datos in eval_ejes.items():
                            if isinstance(datos, dict):
                                delta = datos.get("delta_db", 0.0)
                                if abs(delta) > 0.01:
                                    hubo_cambios = True
                                    nombre_eje = MAPEO_EJES.get(clave_json, clave_json)
                                    razon = datos.get("razonamiento", "")
                                    st.caption(f"• **{nombre_eje}:** `{fmt_db(delta)} dB` — {razon}")
                    if not hubo_cambios:
                        st.caption("ℹ️ *El motor no detectó evidencias para aplicar deltas en este hito.*")
                        
                elif tipo_hito == "MANUAL":
                    st.write(f"**Razonamiento pedagógico docente:** *\"{obs.get('justificacion', '')}\"*")
                    deltas_manuales = obs.get("deltas", {})
                    for eje_nom, delta_val in deltas_manuales.items():
                        if abs(delta_val) > 0.01:
                            st.caption(f"• **{eje_nom}:** `{fmt_db(delta_val)} dB` (Ajuste directo)")
                else:
                    st.write(f"**Registro de transición:** *\"{obs.get('justificacion', '')}\"*")

    # --- CALIBRACIÓN MANUAL DOCENTE (EN 2 TIEMPOS) ---
    st.markdown("---")
    st.subheader("4. Calibración manual docente (dB)")
    st.caption("Ajusta los valores deseados y presiona 'Previsualizar calibración manual en el mapa' para proyectar la propuesta en el mapa vectorial antes de registrarla.")
    
    for eje in EJE_NOMBRES:
        col_c1, col_c2 = st.columns([0.7, 0.3])
        
        with col_c1:
            st.slider(
                eje,
                min_value=-6.0,
                max_value=6.0,
                step=0.1,
                key=f"slider_{eje}",
                on_change=sync_slider_a_num,
                args=(eje,),
                disabled=st.session_state.procesando,
                help=f"Estado actual: {fmt_db(st.session_state.valores_db[eje])} dB"
            )
        with col_c2:
            st.number_input(
                f"Valor {eje}",
                min_value=-6.0,
                max_value=6.0,
                step=0.1,
                key=f"num_{eje}",
                on_change=sync_num_a_slider,
                args=(eje,),
                disabled=st.session_state.procesando,
                label_visibility="collapsed"
            )
    
    justificacion_docente = st.text_area(
        "Razonamiento / Justificación pedagógica del ajuste (Obligatorio):",
        key="input_justificacion",
        height=80,
        disabled=st.session_state.procesando,
        placeholder="Ejemplo: Incremento en Razonamiento ético tras observar la mediación espontánea del estudiante."
    )
    
    # PASO 1: BOTÓN DE PREVISUALIZACIÓN MANUAL
    btn_previsualizar_manual = st.button(
        "👁️ Previsualizar calibración manual en el mapa",
        type="secondary",
        use_container_width=True,
        disabled=st.session_state.procesando
    )

    if btn_previsualizar_manual:
        if not nom_in.strip() or not grp_in.strip():
            st.error("⚠️ Por favor completa el Nombre y Grupo del estudiante antes de previsualizar.")
        elif justificacion_docente.strip():
            deltas_propuestos = {eje: float(st.session_state[f"num_{eje}"]) for eje in EJE_NOMBRES}
            hubo_ajuste = any(abs(v) > 0.001 for v in deltas_propuestos.values())
            if hubo_ajuste:
                st.session_state.previsualizacion_manual = deltas_propuestos
                st.rerun()
            else:
                st.error("⚠️ Ajusta al menos un valor diferente de 0.0 dB para previsualizar.")
        else:
            st.error("⚠️ Ingresa el razonamiento pedagógico para justificar el ajuste manual.")

    # PASO 2: CONFIRMACIÓN DE STAGING MANUAL
    if st.session_state.previsualizacion_manual:
        st.markdown('<div class="manual-staging-card">', unsafe_allow_html=True)
        st.markdown("#### 🎨 Previsualización de Calibración Manual")
        st.caption("Verifica la proyección punteada morada en el mapa visual a la derecha.")
        
        for eje, d_v in st.session_state.previsualizacion_manual.items():
            if abs(d_v) > 0.001:
                val_nuevo = st.session_state.valores_db[eje] + d_v
                st.write(f"• **{eje}:** `{fmt_db(st.session_state.valores_db[eje])} dB` ➔ **`{fmt_db(val_nuevo)} dB`** (`{fmt_db(d_v)} dB`) ")
                
        st.write(f"**Justificación registrada:** *\"{st.session_state.input_justificacion}\"*")
        
        st.markdown("---")
        col_m1, col_m2 = st.columns([0.6, 0.4])
        
        with col_m1:
            if st.button("🎨 Confirmar y registrar calibración manual como hito", type="primary", use_container_width=True, disabled=st.session_state.procesando):
                for eje in EJE_NOMBRES:
                    st.session_state.valores_db[eje] += st.session_state.previsualizacion_manual[eje]
                
                st.session_state.historial_observaciones.append({
                    "tipo": "MANUAL",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "justificacion": st.session_state.input_justificacion,
                    "deltas": st.session_state.previsualizacion_manual,
                    "vector_snapshot": dict(st.session_state.valores_db)
                })
                
                st.session_state.previsualizacion_manual = None
                st.session_state.flag_limpiar_justificacion = True
                st.session_state.flag_reset_calib = True
                
                guardar_expediente_disco(nom_in, mat_in, grp_in)
                st.session_state.mostrar_modal_resguardo = True
                st.rerun()
                
        with col_m2:
            if st.button("❌ Cancelar previsualización", use_container_width=True, disabled=st.session_state.procesando):
                st.session_state.previsualizacion_manual = None
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

# --- COLUMNA DERECHA: ESPEJO METACOGNITIVO Y RADAR (STICKY CONTAINER) ---
with col_der:
    st.markdown('<div class="sticky-radar-container">', unsafe_allow_html=True)
    
    st.subheader("Espejo metacognitivo — Espacio vectorial ℝ⁸")
    
    modo_vis = st.radio(
        "Visualización:",
        options=["Trayectoria completa (todos los hitos)", "Comparativa personalizada"],
        horizontal=True,
        disabled=st.session_state.procesando
    )
    
    tiene_ciclos_previos = any(obs.get("tipo") == "TABULA_RASA" for obs in st.session_state.historial_observaciones)
    label_historico = "Vista de trayectoria histórica" if es_admin else "Vista de trayectoria histórica 🔒 Admin"
    
    ver_historico = st.checkbox(
        label_historico,
        disabled=not (es_admin and tiene_ciclos_previos) or st.session_state.procesando,
        value=False,
        help="Habilitado para Administrador tras ejecutar 'Año nuevo, vida nueva'."
    )
    
    nombre_tit = st.session_state.input_nombre.strip()
    grupo_tit = st.session_state.input_grupo.strip()
    
    if nombre_tit and grupo_tit:
        id_estudiante = f"{nombre_tit} ({grupo_tit})"
    elif nombre_tit:
        id_estudiante = nombre_tit
    elif grupo_tit:
        id_estudiante = f"Grupo {grupo_tit}"
    else:
        id_estudiante = ""
        
    if id_estudiante:
        st.markdown(f"#### Mapa Visual de Crecimiento — {id_estudiante}")
    else:
        st.markdown("#### Mapa Visual de Crecimiento")

    valores_live = {eje: float(st.session_state.valores_db[eje]) for eje in EJE_NOMBRES}
    
    ejes_etiquetados = [FORMATO_EJES_RADAR[eje] for eje in EJE_NOMBRES]
    angles_8 = list(range(0, 360, 45)) + [360]
    angles_360 = np.linspace(0, 360, 361)
    
    # Filtrado de hitos según vista activa
    hitos_activos = []
    paso_tabula = False
    for obs in st.session_state.historial_observaciones:
        if obs.get("tipo") == "TABULA_RASA":
            paso_tabula = True
            continue
        if paso_tabula or not tiene_ciclos_previos:
            hitos_activos.append(obs)

    hitos_a_dibujar = st.session_state.historial_observaciones if (ver_historico and es_admin) else hitos_activos

    todos_vectores = [list(valores_live.values())]
    for obs in hitos_a_dibujar:
        if "vector_snapshot" in obs:
            todos_vectores.append(list(obs["vector_snapshot"].values()))
            
    max_valor_global = max([val for vec in todos_vectores for val in vec] + [0.0])
    
    # Límite exterior dinámico del mapa (12.0, 18.0 o 24.0 dB)
    limite_radar = 12.0 if max_valor_global <= 12.0 else (18.0 if max_valor_global <= 18.0 else 24.0)
    
    fig = go.Figure()

    # --- FUNCIÓN AUXILIAR DE ÓRBITAS CIRCULARES CONTINUAS ---
    def agregar_orbita_circular(fig_obj, r_val, nombre, color="#475569", width=1.5, dash="solid"):
        fig_obj.add_trace(go.Scatterpolar(
            r=[r_val] * 361,
            theta=angles_360,
            mode="lines",
            line=dict(color=color, width=width, dash=dash),
            name=nombre,
            hoverinfo="skip"
        ))

    # --- DIBUJO DE ÓRBITAS CLAVE Y FRONTERAS PERIMETRALES EN GRIS PIZARRA SUAVE ---
    
    # 0.0 dB (Línea base) — Círculo continuo suave en gris pizarra oscuro
    agregar_orbita_circular(fig, 0.0, "Línea base (0.0 dB)", color="#334155", width=1.8)

    # +6.0 dB (Principiante) — Círculo continuo suave en gris pizarra
    agregar_orbita_circular(fig, 6.0, "+6.0 dB (Principiante)", color="#475569", width=1.5)

    # +12.0 dB (Intermedio / Marco exterior inicial)
    # Es el perímetro sólido inicial; si se expande a +18 dB, se mantiene como hito interno.
    is_perimeter_12 = (limite_radar == 12.0)
    agregar_orbita_circular(
        fig, 12.0, "+12.0 dB (Intermedio)",
        color="#334155" if is_perimeter_12 else "#475569",
        width=1.8 if is_perimeter_12 else 1.5,
        dash="solid"
    )

    # +18.0 dB (Avanzado) — Se activa cuando el mapa se expande a 18 dB
    if limite_radar >= 18.0:
        is_perimeter_18 = (limite_radar == 18.0)
        agregar_orbita_circular(
            fig, 18.0, "+18.0 dB (Avanzado)",
            color="#334155" if is_perimeter_18 else "#475569",
            width=1.8 if is_perimeter_18 else 1.5,
            dash="solid"
        )

    # +24.0 dB (Experto) — Se activa cuando el mapa se expande a 24 dB
    if limite_radar >= 24.0:
        agregar_orbita_circular(
            fig, 24.0, "+24.0 dB (Experto)",
            color="#334155",
            width=1.8,
            dash="solid"
        )

    num_hitos = len(hitos_a_dibujar)
    
    PALETA_COLORES = [
        ("rgba(236, 72, 153, 0.8)", "rgba(236, 72, 153, 0.1)"),
        ("rgba(168, 85, 247, 0.8)", "rgba(168, 85, 247, 0.12)"),
        ("rgba(59, 130, 246, 0.85)", "rgba(59, 130, 246, 0.15)"),
        ("rgba(16, 185, 129, 0.9)", "rgba(16, 185, 129, 0.18)"),
        ("rgba(99, 102, 241, 1.0)", "rgba(99, 102, 241, 0.35)")
    ]

    sin_staging = (st.session_state.analisis_pendiente is None and st.session_state.previsualizacion_manual is None)

    if modo_vis == "Trayectoria completa (todos los hitos)":
        if num_hitos > 0:
            for i, obs in enumerate(hitos_a_dibujar):
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [v_snap[eje] for eje in EJE_NOMBRES]
                vals_cerrados = vals + [vals[0]]
                
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                is_last = (i == num_hitos - 1) and sin_staging
                tipo_hito = obs.get("tipo", "IA")
                
                tag_tipo = "PRISMA" if tipo_hito == "IA" else ("Manual" if tipo_hito == "MANUAL" else "Transición")
                
                fig.add_trace(go.Scatterpolar(
                    r=vals_cerrados,
                    theta=angles_8,
                    fill="toself" if is_last else "none",
                    fillcolor=color_fill,
                    line=dict(color=color_line, width=3 if is_last else 1.8, dash="solid" if is_last else "dot"),
                    marker=dict(size=6, color=color_line),
                    name=f"Hito #{i+1} [{tag_tipo}]",
                    hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
                ))
        else:
            vals = [valores_live[eje] for eje in EJE_NOMBRES]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=angles_8,
                fill="toself" if sin_staging else "none",
                fillcolor="rgba(99, 102, 241, 0.35)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#4F46E5"),
                name="Estado actual",
                hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
            ))

    elif modo_vis == "Comparativa personalizada":
        if num_hitos > 0:
            opciones_hitos = [f"Hito #{i+1} [{obs.get('tipo', 'IA')}] — {obs.get('timestamp', '')}" for i, obs in enumerate(hitos_a_dibujar)]
            hitos_seleccionados = st.multiselect(
                "Superponer hitos para comparativa:",
                options=opciones_hitos,
                default=[opciones_hitos[-1]],
                disabled=st.session_state.procesando
            )
            
            for idx_str in hitos_seleccionados:
                i = int(idx_str.split("#")[1].split(" ")[0]) - 1
                obs = hitos_a_dibujar[i]
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [v_snap[eje] for eje in EJE_NOMBRES]
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=angles_8,
                    fill="toself",
                    fillcolor=color_fill,
                    line=dict(color=color_line, width=2.5),
                    marker=dict(size=6, color=color_line),
                    name=f"Hito #{i+1}",
                    hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
                ))
        else:
            vals = [valores_live[eje] for eje in EJE_NOMBRES]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=angles_8,
                fill="toself",
                fillcolor="rgba(99, 102, 241, 0.35)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#4F46E5"),
                name="Estado actual",
                hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
            ))

    # --- PREVISUALIZACIÓN / VECTOR FANTASMA (IA) ---
    if st.session_state.analisis_pendiente:
        hitos_p = st.session_state.analisis_pendiente.get("hitos", [])
        deltas_p_tot = {eje: 0.0 for eje in EJE_NOMBRES}
        for item in hitos_p:
            for eje, d_v in item.get("deltas", {}).items():
                deltas_p_tot[eje] += d_v
                
        vals_proyectados = [valores_live[eje] + deltas_p_tot.get(eje, 0.0) for eje in EJE_NOMBRES]
        vals_proyectados_cerrados = vals_proyectados + [vals_proyectados[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=vals_proyectados_cerrados,
            theta=angles_8,
            fill="toself",
            fillcolor="rgba(168, 85, 247, 0.15)",
            line=dict(color="#A855F7", width=2.5, dash="dot"),
            marker=dict(size=7, color="#A855F7"),
            name="Previsualización IA",
            hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
        ))

    # --- PREVISUALIZACIÓN / VECTOR FANTASMA (MANUAL) ---
    if st.session_state.previsualizacion_manual:
        vals_manuales = [valores_live[eje] + st.session_state.previsualizacion_manual.get(eje, 0.0) for eje in EJE_NOMBRES]
        vals_manuales_cerrados = vals_manuales + [vals_manuales[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=vals_manuales_cerrados,
            theta=angles_8,
            fill="toself",
            fillcolor="rgba(168, 85, 247, 0.18)",
            line=dict(color="#9333EA", width=2.5, dash="dash"),
            marker=dict(size=7, color="#9333EA"),
            name="Previsualización manual",
            hovertemplate="<b>%{r:+.1f} dB</b><extra></extra>"
        ))

    # Construcción de ticks de 2 en 2 dB
    tick_vals_2db = list(range(-6, int(limite_radar) + 1, 2))
    tick_texts_2db = []
    for tv in tick_vals_2db:
        if tv == 0:
            tick_texts_2db.append("0.0 dB (Línea base)")
        elif tv == 6:
            tick_texts_2db.append("+6.0 dB (Principiante)")
        elif tv == 12:
            tick_texts_2db.append("+12.0 dB (Intermedio)")
        elif tv == 18:
            tick_texts_2db.append("+18.0 dB (Avanzado)")
        elif tv == 24:
            tick_texts_2db.append("+24.0 dB (Experto)")
        else:
            tick_texts_2db.append("")

    fig.update_layout(
        uirevision=True,
        polar=dict(
            gridshape="circular",
            radialaxis=dict(
                visible=True,
                range=[-6, limite_radar],
                tickvals=tick_vals_2db,
                ticktext=tick_texts_2db,
                angle=22.5,
                gridcolor="#CBD5E1",
                gridwidth=0.8,
                tickfont=dict(size=8, color="#334155")
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=list(range(0, 360, 45)),
                ticktext=ejes_etiquetados,
                tickfont=dict(size=9, color="#1E293B"),
                rotation=90,
                direction="clockwise",
                gridcolor="#E2E8F0"
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(size=9.0)
        ),
        height=510,
        margin=dict(l=40, r=40, t=75, b=80)
    )

    # Configuración limpia de barra de herramientas: sin logo de Plotly, conserva Pantalla Completa y Descargar PNG
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'zoom2d', 'pan2d', 'select2d', 'lasso2d', 
                'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d'
            ],
            'scrollZoom': False
        }
    )

    st.markdown('</div>', unsafe_allow_html=True)

# --- DESPLIEGUE DE DIÁLOGOS ---
if st.session_state.mostrar_modal_resguardo and not st.session_state.analisis_pendiente and not st.session_state.previsualizacion_manual:
    modal_exportar_resguardo(
        st.session_state.input_nombre,
        st.session_state.input_matricula,
        st.session_state.input_grupo
    )

if st.session_state.mostrar_modal_confirmar_reiniciar:
    modal_confirmar_reiniciar()
