import streamlit as st
import plotly.graph_objects as go
import json
import requests
import os
import re
from datetime import datetime

# --- CONFIGURACIÓN Y ESTILOS DE INTERFAZ ---
st.set_page_config(
    page_title="Aula Viva — PRISMA",
    page_icon="🌌",
    layout="wide"
)

# Estilos CSS inyectados para fijar el mapa en la columna derecha al hacer scroll
st.markdown("""
<style>
    /* Habilita sticky real en la segunda columna de Streamlit */
    [data-testid="stColumn"]:nth-of-type(2) {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 2rem !important;
        align-self: flex-start !important;
        z-index: 99;
    }
    .sticky-radar-container {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 2rem !important;
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
</style>
""", unsafe_allow_html=True)

st.title("Aula Viva® — PRISMA")
st.markdown("### Plataforma de Reflexión e Interpretación para el Seguimiento Multidimensional del Aprendizaje")
st.caption("Analítica cualitativa vectorizada en ℝ⁸ | Aula Viva® | Ecosistema ASPIRE®")

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

# --- INICIALIZACIÓN Y CONTROL DE ESTADO LIMPIO ---
if "valores_db" not in st.session_state:
    st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}

if "historial_observaciones" not in st.session_state:
    st.session_state.historial_observaciones = []

if "analisis_pendiente" not in st.session_state:
    st.session_state.analisis_pendiente = None

if "estudiantes_db" not in st.session_state:
    st.session_state.estudiantes_db = {}

if "mostrar_modal_resguardo" not in st.session_state:
    st.session_state.mostrar_modal_resguardo = False

if "mostrar_modal_confirmar_reiniciar" not in st.session_state:
    st.session_state.mostrar_modal_confirmar_reiniciar = False

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
def guardar_expediente_disco(nombre, matricula, grupo):
    fecha_iso = datetime.now().strftime("%y%m%d")
    hora_iso = datetime.now().strftime("%H%M%S")
    nom_clean = limpiar_cadena(nombre)
    grp_clean = limpiar_cadena(grupo)
    filename = f"{fecha_iso}_{hora_iso}_{nom_clean}_{grp_clean}_PRISMA.json"
    filepath = os.path.join(DIR_EXPEDIENTES, filename)
    
    exp_data = {
        "estudiante": nombre,
        "matricula": matricula,
        "grupo": grupo,
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vector_actual_db": st.session_state.valores_db,
        "historial_observaciones": st.session_state.historial_observaciones
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(exp_data, f, indent=2, ensure_ascii=False)
    return filename, exp_data

# --- DIÁLOGOS DE CONTROL (MODALES) ---
@st.dialog("💾 Resguardo de expediente vectorial")
def modal_exportar_resguardo(nombre, matricula, grupo):
    nombre_mostrar = nombre if nombre else "Estudiante"
    st.write(f"Se ha consolidado un nuevo hito en el expediente de **{nombre_mostrar}**.")
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

    st.download_button(
        label="💾 Descargar resguardo (.json) y reiniciar",
        data=json.dumps(exp_data, indent=2, ensure_ascii=False),
        file_name=filename_export,
        mime="application/json",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    col_r1, col_r2 = st.columns([0.5, 0.5])
    with col_r1:
        if st.button("🗑️ Reiniciar sin descargar", type="secondary", use_container_width=True):
            st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
            st.session_state.historial_observaciones = []
            st.session_state.analisis_pendiente = None
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
    if st.button("✨ Reiniciar pantalla de registro", use_container_width=True, type="primary"):
        st.session_state.mostrar_modal_confirmar_reiniciar = True
        st.rerun()

    st.markdown("---")
    
    st.header("🔒 Herramientas de administrador")
    
    clave_admin = st.text_input(
        "🔑 Clave de administrador:",
        type="password",
        placeholder="Ingresa clave de acceso",
        help="Habilita la carga de expedientes y la transición de ciclo escolar."
    )
    
    es_admin = (clave_admin == "prisma2026" or clave_admin == "prisma26")
    
    if es_admin:
        st.success("Acceso concedido — Modo Administrador")
        if st.button("🔴 Salir del modo administrador", use_container_width=True):
            clave_admin = ""
            st.rerun()
    else:
        st.info("ℹ️ **Modo Usuario**: Funciones avanzadas reservadas para administración.")

    st.markdown("---")
    
    label_carga = "2. Cargar expediente (.json)" if es_admin else "2. Cargar expediente (.json) 🔒 Admin"
    st.subheader(label_carga)
    archivo_cargado = st.file_uploader(
        "Selecciona expediente JSON:",
        type=["json"],
        disabled=not es_admin,
        help="Carga de expedientes históricos" if es_admin else "Función exclusiva para nivel Administrador"
    )
    
    btn_importar = st.button("📥 Cargar expediente", disabled=(not es_admin or archivo_cargado is None), use_container_width=True)
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
    st.caption("Aplica 'Tabula Rasa': restablece el vector a 0.0 dB registrando el cierre de ciclo en el historial, preservando la continuidad longitudinal.")
    btn_tabula = st.button("🔄 Ejecutar 'Año nuevo, vida nueva'", disabled=not es_admin, use_container_width=True)
    if btn_tabula and es_admin:
        st.session_state.historial_observaciones.append({
            "tipo": "TABULA_RASA",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "justificacion": "Cierre de ciclo escolar ('Año nuevo, vida nueva'). Vector restablecido a línea base (0.0 dB) preservando la trazabilidad longitudinal.",
            "vector_snapshot": dict(st.session_state.valores_db)
        })
        st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
        st.success("Transición registrada. Vector restablecido a 0.0 dB con trazabilidad longitudinal resguardada.")
        st.rerun()

# --- LAYOUT PRINCIPAL A DOS COLUMNAS ---
col_izq, col_der = st.columns([0.45, 0.55])

with col_izq:
    st.subheader("1. Ficha del estudiante y registro")
    
    col_f1, col_f2, col_f3 = st.columns([0.35, 0.4, 0.25])
    
    with col_f2:
        mat_in = st.text_input("Matrícula ID:", key="input_matricula", placeholder="Ej: A012345")
        if mat_in in st.session_state.estudiantes_db:
            st.session_state.input_nombre = st.session_state.estudiantes_db[mat_in]["nombre"]
            st.session_state.input_grupo = st.session_state.estudiantes_db[mat_in]["grupo"]

    with col_f1:
        nom_in = st.text_input("Nombre del estudiante:", key="input_nombre", placeholder="Nombre_Apellido")
        if mat_in and nom_in:
            st.session_state.estudiantes_db[mat_in] = {
                "nombre": nom_in,
                "grupo": st.session_state.input_grupo
            }
            
    with col_f3:
        grp_in = st.text_input("Grupo:", key="input_grupo", placeholder="Grupo")

    st.markdown("---")
    st.subheader("2. Registro de Nota Narrativa Docente")
    
    # Formulario habilitante para captura nativa de Cmd+Enter / Ctrl+Enter
    with st.form(key="form_nota_docente", clear_on_submit=False):
        nota_docente = st.text_area(
            "Dictado / Nota narrativa del docente:",
            key="input_nota",
            height=130,
            placeholder="Ingresa la observación cualitativa. Presiona Cmd+Enter o Ctrl+Enter para procesar."
        )
        btn_analizar = st.form_submit_button("⚡ Ejecutar análisis de nota", type="primary", use_container_width=True)

    if btn_analizar:
        if not nom_in.strip():
            st.error("⚠️ Por favor ingresa el nombre del estudiante antes de procesar.")
        elif not grp_in.strip():
            st.error("⚠️ Por favor ingresa el grupo del estudiante antes de procesar.")
        elif not nota_docente.strip():
            st.error("⚠️ Por favor ingresa una nota de observación cualitativa.")
        else:
            with st.spinner("Procesando inferencia cualitativa en ℝ⁸ (PRISMA-Engine)..."):
                try:
                    user_prompt = f"Estudiante: {nom_in.strip()}\nNota narrativa del docente: \"{nota_docente}\""
                    
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "prisma-engine",
                            "prompt": user_prompt,
                            "stream": False,
                            "format": "json"
                        },
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        resultado = json.loads(response.json()["response"])
                        eval_ejes = resultado.get("evaluacion_ejes", {})
                        deltas_aplicados = {}
                        
                        for clave_json, nombre_oficial in MAPEO_EJES.items():
                            if clave_json in eval_ejes:
                                delta = float(eval_ejes[clave_json].get("delta_db", 0.0))
                                deltas_aplicados[nombre_oficial] = delta
                        
                        st.session_state.analisis_pendiente = {
                            "nota": nota_docente,
                            "deltas": deltas_aplicados,
                            "resultado_ia": resultado
                        }
                        st.rerun()
                    else:
                        st.error(f"Error en Ollama local (Código HTTP {response.status_code})")
                except Exception as e:
                    st.error(f"Error de conexión con Ollama local: {e}")

    # Exportación directa colocada estratégicamente debajo de Ejecutar análisis
    if st.button("💾 Exportar Expediente (.json)", use_container_width=True):
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

    # --- FLUJO DE 3 TIEMPOS: ÁREA DE PREVISUALIZACIÓN / STAGING ---
    if st.session_state.analisis_pendiente:
        st.markdown('<div class="staging-card">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Previsualización del análisis de la IA")
        st.caption("Revisa el impacto sugerido en el mapa vectorial antes de consolidar el hito.")
        
        deltas_p = st.session_state.analisis_pendiente["deltas"]
        resultado_p = st.session_state.analisis_pendiente["resultado_ia"].get("evaluacion_ejes", {})
        
        for clave_j, n_eje in MAPEO_EJES.items():
            if n_eje in deltas_p and abs(deltas_p[n_eje]) > 0.01:
                razon = resultado_p.get(clave_j, {}).get("razonamiento", "")
                st.write(f"• **{n_eje}:** `{fmt_db(deltas_p[n_eje])} dB` — *{razon}*")
                
        st.markdown("---")
        col_s1, col_s2, col_s3 = st.columns([0.35, 0.3, 0.35])
        
        with col_s1:
            if st.button("✅ Aceptar y Registrar Hito", type="primary", use_container_width=True):
                for eje, d_val in deltas_p.items():
                    st.session_state.valores_db[eje] += d_val
                
                st.session_state.historial_observaciones.append({
                    "tipo": "IA",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "nota": st.session_state.analisis_pendiente["nota"],
                    "deltas": deltas_p,
                    "resultado_ia": st.session_state.analisis_pendiente["resultado_ia"],
                    "vector_snapshot": dict(st.session_state.valores_db)
                })
                
                st.session_state.analisis_pendiente = None
                st.session_state.flag_limpiar_nota = True
                
                guardar_expediente_disco(nom_in, mat_in, grp_in)
                st.session_state.mostrar_modal_resguardo = True
                st.rerun()
                
        with col_s2:
            if st.button("🎨 Ajustar Manualmente", use_container_width=True):
                for eje, d_val in deltas_p.items():
                    val_f = float(d_val)
                    st.session_state[f"slider_{eje}"] = val_f
                    st.session_state[f"num_{eje}"] = val_f
                st.session_state.analisis_pendiente = None
                st.rerun()
                
        with col_s3:
            if st.button("❌ Rechazar análisis / modificar nota docente", use_container_width=True):
                st.session_state.analisis_pendiente = None
                st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

    # --- META-ANÁLISIS DE TRAYECTORIA POR PRISMA ---
    st.markdown("---")
    st.subheader("3. Meta-Análisis de Trayectoria")
    st.caption("Pide a PRISMA analizar la trayectoria multidimensional integral durante el periodo seleccionado para detectar patrones y sugerir ajustes en los ejes.")
    
    if st.button("🌌 Meta-Análisis PRISMA", use_container_width=True):
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
                        eval_meta = meta_res.get("evaluacion_ejes", {})
                        
                        st.info("🌌 **Diagnóstico Holístico Sugerido por PRISMA:**")
                        overrides_sugeridos = {}
                        for c_j, n_eje in MAPEO_EJES.items():
                            if c_j in eval_meta:
                                delta_m = float(eval_meta[c_j].get("delta_db", 0.0))
                                if abs(delta_m) > 0.01:
                                    overrides_sugeridos[n_eje] = delta_m
                                    st.write(f"• **{n_eje}:** Ajuste holístico de `{fmt_db(delta_m)} dB` — {eval_meta[c_j].get('razonamiento', '')}")
                        
                        if st.button("Aceptar y registrar Meta-Análisis PRISMA como Hito"):
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
                        st.error("No se pudo obtener el Meta-Análisis de Ollama.")
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
                    for clave_json, datos in eval_ejes.items():
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

    # --- CALIBRACIÓN MANUAL DOCENTE HÍBRIDA ---
    st.markdown("---")
    st.subheader("4. Calibración manual docente (dB)")
    st.caption("Ajusta los valores ingresando directamente el número o desplazando la barra táctil.")
    
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
                label_visibility="collapsed"
            )
    
    justificacion_docente = st.text_area(
        "Razonamiento / Justificación pedagógica del ajuste (Obligatorio):",
        key="input_justificacion",
        height=80,
        placeholder="Ejemplo: Incremento en Razonamiento ético tras observar la mediación espontánea del estudiante."
    )
    
    btn_aplicar_ajustes = st.button("🎨 Registrar calibración manual como hito", type="secondary", use_container_width=True)

    if btn_aplicar_ajustes:
        if not nom_in.strip() or not grp_in.strip():
            st.error("⚠️ Por favor completa el Nombre y Grupo del estudiante antes de registrar la calibración manual.")
        elif justificacion_docente.strip():
            deltas_confirmados = {eje: float(st.session_state[f"num_{eje}"]) for eje in EJE_NOMBRES}
            hubo_ajuste = any(abs(v) > 0.001 for v in deltas_confirmados.values())
            if hubo_ajuste:
                for eje in EJE_NOMBRES:
                    st.session_state.valores_db[eje] += deltas_confirmados[eje]
                
                st.session_state.historial_observaciones.append({
                    "tipo": "MANUAL",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "justificacion": justificacion_docente,
                    "deltas": deltas_confirmados,
                    "vector_snapshot": dict(st.session_state.valores_db)
                })
                
                # Activar banderas de reinicio seguro post-renderizado
                st.session_state.flag_limpiar_justificacion = True
                st.session_state.flag_reset_calib = True
                
                guardar_expediente_disco(nom_in, mat_in, grp_in)
                st.session_state.mostrar_modal_resguardo = True
                st.rerun()
            else:
                st.error("⚠️ Ajusta al menos un valor diferente de 0.0 dB para registrar.")
        else:
            st.error("⚠️ Ingrese el razonamiento pedagógico para justificar el ajuste manual.")

# --- COLUMNA DERECHA: ESPEJO METACOGNITIVO Y RADAR (STICKY CONTAINER) ---
with col_der:
    st.markdown('<div class="sticky-radar-container">', unsafe_allow_html=True)
    
    st.subheader("Espejo metacognitivo — Espacio vectorial ℝ⁸")
    
    modo_vis = st.radio(
        "Visualización:",
        options=["Trayectoria completa (todos los hitos)", "Comparativa personalizada"],
        horizontal=True
    )
    
    label_historico = "Vista de trayectoria histórica" if es_admin else "Vista de trayectoria histórica 🔒 Admin"
    ver_historico = st.checkbox(label_historico, disabled=not es_admin, value=False)
    
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
    
    ejes_etiquetados = [
        f"<b>{FORMATO_EJES_RADAR[eje]}</b><br><span style='color:#4F46E5;'>({fmt_db(valores_live[eje])} dB)</span>"
        for eje in EJE_NOMBRES
    ]
    ejes_cerrados = ejes_etiquetados + [ejes_etiquetados[0]]
    
    # Filtrado de hitos según vista histórica o ciclo escolar activo
    hitos_activos = []
    paso_tabula = False
    for obs in st.session_state.historial_observaciones:
        if obs.get("tipo") == "TABULA_RASA":
            paso_tabula = True
            continue
        if paso_tabula:
            hitos_activos.append(obs)
        else:
            if not any(o.get("tipo") == "TABULA_RASA" for o in st.session_state.historial_observaciones):
                hitos_activos.append(obs)

    hitos_a_dibujar = st.session_state.historial_observaciones if (ver_historico and es_admin) else (hitos_activos if any(o.get("tipo") == "TABULA_RASA" for o in st.session_state.historial_observaciones) else st.session_state.historial_observaciones)

    todos_vectores = [list(valores_live.values())]
    for obs in hitos_a_dibujar:
        if "vector_snapshot" in obs:
            todos_vectores.append(list(obs["vector_snapshot"].values()))
            
    max_valor_global = max([val for vec in todos_vectores for val in vec] + [0.0])
    limite_radar = 12.0 if max_valor_global <= 12.0 else (18.0 if max_valor_global <= 18.0 else 24.0)
    
    fig = go.Figure()

    # Línea base (0.0 dB)
    fig.add_trace(go.Scatterpolar(
        r=[0.0] * 9,
        theta=ejes_cerrados,
        mode="lines",
        line=dict(color="#94A3B8", width=1.5, dash="dash"),
        name="Línea base (0.0 dB)",
        hoverinfo="skip"
    ))

    num_hitos = len(hitos_a_dibujar)
    
    PALETA_COLORES = [
        ("rgba(236, 72, 153, 0.8)", "rgba(236, 72, 153, 0.1)"),
        ("rgba(168, 85, 247, 0.8)", "rgba(168, 85, 247, 0.12)"),
        ("rgba(59, 130, 246, 0.85)", "rgba(59, 130, 246, 0.15)"),
        ("rgba(16, 185, 129, 0.9)", "rgba(16, 185, 129, 0.18)"),
        ("rgba(99, 102, 241, 1.0)", "rgba(99, 102, 241, 0.35)")
    ]

    if modo_vis == "Trayectoria completa (todos los hitos)":
        if num_hitos > 0:
            for i, obs in enumerate(hitos_a_dibujar):
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [v_snap[eje] for eje in EJE_NOMBRES]
                vals_cerrados = vals + [vals[0]]
                
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                is_last = (i == num_hitos - 1) and (st.session_state.analisis_pendiente is None)
                tipo_hito = obs.get("tipo", "IA")
                
                tag_tipo = "PRISMA" if tipo_hito == "IA" else ("Manual" if tipo_hito == "MANUAL" else "Año Nuevo")
                
                fig.add_trace(go.Scatterpolar(
                    r=vals_cerrados,
                    theta=ejes_cerrados,
                    fill="toself" if is_last else "none",
                    fillcolor=color_fill,
                    line=dict(color=color_line, width=3 if is_last else 1.8, dash="solid" if is_last else "dot"),
                    marker=dict(size=6, color=color_line),
                    name=f"Hito #{i+1} [{tag_tipo}]",
                    hovertemplate="%{theta}<extra></extra>"
                ))
        else:
            vals = [valores_live[eje] for eje in EJE_NOMBRES]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=ejes_cerrados,
                fill="toself" if st.session_state.analisis_pendiente is None else "none",
                fillcolor="rgba(99, 102, 241, 0.35)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#4F46E5"),
                name="Estado actual",
                hovertemplate="%{theta}<extra></extra>"
            ))

    elif modo_vis == "Comparativa personalizada":
        if num_hitos > 0:
            opciones_hitos = [f"Hito #{i+1} [{obs.get('tipo', 'IA')}] — {obs.get('timestamp', '')}" for i, obs in enumerate(hitos_a_dibujar)]
            hitos_seleccionados = st.multiselect(
                "Superponer hitos para comparativa:",
                options=opciones_hitos,
                default=[opciones_hitos[-1]]
            )
            
            for idx_str in hitos_seleccionados:
                i = int(idx_str.split("#")[1].split(" ")[0]) - 1
                obs = hitos_a_dibujar[i]
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [v_snap[eje] for eje in EJE_NOMBRES]
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=ejes_cerrados,
                    fill="toself",
                    fillcolor=color_fill,
                    line=dict(color=color_line, width=2.5),
                    marker=dict(size=6, color=color_line),
                    name=f"Hito #{i+1}",
                    hovertemplate="%{theta}<extra></extra>"
                ))
        else:
            st.info("Ingresa observaciones para habilitar la comparativa por hitos.")
            vals = [valores_live[eje] for eje in EJE_NOMBRES]
            fig.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=ejes_cerrados,
                fill="toself",
                fillcolor="rgba(99, 102, 241, 0.35)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#4F46E5"),
                name="Estado actual",
                hovertemplate="%{theta}<extra></extra>"
            ))

    # VECTOR FANTASMA: Dibuja la Previsualización (sugerida) en la etapa de Staging
    if st.session_state.analisis_pendiente:
        deltas_p = st.session_state.analisis_pendiente.get("deltas", {})
        vals_proyectados = [valores_live[eje] + deltas_p.get(eje, 0.0) for eje in EJE_NOMBRES]
        vals_proyectados_cerrados = vals_proyectados + [vals_proyectados[0]]
        
        fig.add_trace(go.Scatterpolar(
            r=vals_proyectados_cerrados,
            theta=ejes_cerrados,
            fill="toself",
            fillcolor="rgba(168, 85, 247, 0.15)",
            line=dict(color="#A855F7", width=2.5, dash="dot"),
            marker=dict(size=7, color="#A855F7"),
            name="Previsualización (sugerida)",
            hovertemplate="%{theta}<extra></extra>"
        ))

    fig.update_layout(
        uirevision=True,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-6, limite_radar],
                tickvals=[-6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                ticktext=[
                    "-6 dB (Mín)", "", "", "0.0 dB (Base)", "", "", "", "", "",
                    "+12 dB (Inicial)", "", "", "+18 dB (Intermedio)", "", "", "+24 dB (Experto)"
                ],
                angle=22.5,
                gridcolor="#E2E8F0",
                gridwidth=0.6,
                tickfont=dict(size=8, color="#475569")
            ),
            angularaxis=dict(
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
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(size=9.0)
        ),
        height=540,
        margin=dict(l=40, r=40, t=75, b=80)
    )

    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': False, 'displayModeBar': True})
    st.caption("ℹ️ *Las lecturas en decibeles (dB) indican el índice de crecimiento acumulado respecto a la línea base (0.0 dB).*")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- DESPLIEGUE FINAL DE DIÁLOGOS ---
if st.session_state.mostrar_modal_resguardo:
    modal_exportar_resguardo(
        st.session_state.input_nombre,
        st.session_state.input_matricula,
        st.session_state.input_grupo
    )

if st.session_state.mostrar_modal_confirmar_reiniciar:
    modal_confirmar_reiniciar()
