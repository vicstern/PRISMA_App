import streamlit as st
import plotly.graph_objects as go
import json
import requests
import os
import re
from datetime import datetime

st.set_page_config(
    page_title="Aula Viva — Motor PRISMA R8",
    page_icon="🌌",
    layout="wide"
)

st.title("Aula Viva® — Sub-motor PRISMA (R⁸)")
st.markdown("### **PRISMA**: **P**lataforma de **R**eflexión e **I**nterpretación para el **S**eguimiento **M**ultidimensional del **A**prendizaje")
st.caption("Analítica cualitativa vectorizada | Aula Viva® (IMPI Exp. 3724582) | Ecosistema ASPIRE® (INDAUTOR Reg. 03-2024-080811234500-01)")

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

if "valores_db" not in st.session_state:
    st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}

if "historial_observaciones" not in st.session_state:
    st.session_state.historial_observaciones = []

if "mostrar_modal_resguardo" not in st.session_state:
    st.session_state.mostrar_modal_resguardo = False

for eje in EJE_NOMBRES:
    key_temp = f"temp_{eje}"
    if key_temp not in st.session_state:
        st.session_state[key_temp] = float(st.session_state.valores_db[eje])

@st.dialog("💾 Resguardo de expediente vectorial")
def modal_exportar_resguardo(nombre, grupo):
    nombre_mostrar = nombre if nombre else "Estudiante"
    st.write(f"Se ha acumulado un nuevo hito en el expediente de **{nombre_mostrar}**.")
    st.write("¿Deseas descargar una copia de resguardo local (`.json`) en este momento?")
    
    fecha_iso = datetime.now().strftime("%y%m%d")
    nom_clean = limpiar_cadena(nombre)
    grp_clean = limpiar_cadena(grupo)
    filename_export = f"{fecha_iso}_{nom_clean}_{grp_clean}_PRISMA.json"
    
    expediente_data = {
        "estudiante": nombre,
        "grupo": grupo,
        "fecha_exportacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "vector_actual_db": st.session_state.valores_db,
        "historial_observaciones": st.session_state.historial_observaciones
    }
    
    col_m1, col_m2 = st.columns([0.6, 0.4])
    with col_m1:
        descargado = st.download_button(
            label="Sí, descargar (.json)",
            data=json.dumps(expediente_data, indent=2, ensure_ascii=False),
            file_name=filename_export,
            mime="application/json",
            type="primary",
            use_container_width=True
        )
        if descargado:
            st.session_state.mostrar_modal_resguardo = False
            st.rerun()
            
    with col_m2:
        if st.button("No por ahora", use_container_width=True):
            st.session_state.mostrar_modal_resguardo = False
            st.rerun()

# --- SIDEBAR: OPERACIÓN Y CONTROLES DE ADMINISTRADOR ---
with st.sidebar:
    st.header("⚙️ Gestión de registro")
    
    # 1. Operación general (Usuario / Docente)
    st.subheader("1. Flujo de trabajo")
    if st.button("✨ Reiniciar pantalla de registro", use_container_width=True, type="primary"):
        st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
        st.session_state.historial_observaciones = []
        for eje in EJE_NOMBRES:
            st.session_state[f"temp_{eje}"] = 0.0
        st.success("Pantalla de registro reiniciada. Listo para un nuevo expediente.")
        st.rerun()

    st.markdown("---")
    
    # 2. Herramientas de Administrador
    st.header("🔒 Herramientas de Administrador")
    
    clave_admin = st.text_input(
        "🔑 Clave de Administrador:",
        type="password",
        placeholder="Ingresa clave de acceso",
        help="Requerida para importar expedientes externos o aplicar cierres de ciclo."
    )
    
    es_admin = (clave_admin == "prisma2026")
    
    if es_admin:
        st.success("Acceso concedido — Controles de Administrador habilitados")
    else:
        st.info("ℹ️ **Modo Usuario**: Las herramientas de importación y transición de ciclo ('Año nuevo, vida nueva') requieren clave de Administrador.")

    st.markdown("---")
    
    # Cargar expediente
    st.subheader("2. Cargar expediente (.json)")
    archivo_cargado = st.file_uploader(
        "Selecciona expediente JSON:",
        type=["json"],
        disabled=not es_admin,
        help="🔒 Habilitado únicamente en Modo Administrador" if not es_admin else "Importa expedientes vectoriales históricos"
    )
    
    btn_importar = st.button("📥 Importar expediente", disabled=(not es_admin or archivo_cargado is None), use_container_width=True)
    if btn_importar and archivo_cargado is not None and es_admin:
        try:
            datos = json.load(archivo_cargado)
            st.session_state.valores_db = datos.get("vector_actual_db", {eje: 0.0 for eje in EJE_NOMBRES})
            st.session_state.historial_observaciones = datos.get("historial_observaciones", [])
            for eje in EJE_NOMBRES:
                st.session_state[f"temp_{eje}"] = float(st.session_state.valores_db[eje])
            st.success("Expediente cargado correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"Error al leer el archivo JSON: {e}")

    st.markdown("---")
    
    # Transición "Año nuevo, vida nueva" (Tabula Rasa / Continuidad longitudinal)
    st.subheader("3. Transición: 'Año nuevo, vida nueva'")
    st.caption("Aplica 'Tabula Rasa': restablece el vector a 0.0 dB registrando el cierre de ciclo en el historial para iniciar el nuevo periodo, preservando la continuidad longitudinal en el expediente.")
    btn_tabula = st.button("🔄 Ejecutar 'Año nuevo, vida nueva' 🔒" if not es_admin else "🔄 Ejecutar 'Año nuevo, vida nueva'", disabled=not es_admin, use_container_width=True)
    if btn_tabula and es_admin:
        st.session_state.historial_observaciones.append({
            "tipo": "TABULA_RASA",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "justificacion": "Cierre de ciclo escolar ('Año nuevo, vida nueva'). Vector restablecido a línea base (0.0 dB) preservando la trazabilidad longitudinal.",
            "vector_snapshot": dict(st.session_state.valores_db)
        })
        st.session_state.valores_db = {eje: 0.0 for eje in EJE_NOMBRES}
        for eje in EJE_NOMBRES:
            st.session_state[f"temp_{eje}"] = 0.0
        st.success("Transición registrada. Vector restablecido a 0.0 dB con trazabilidad longitudinal resguardada.")
        st.rerun()

col_izq, col_der = st.columns([0.42, 0.58])

with col_izq:
    st.subheader("1. Ficha del estudiante y registro")
    
    col_f1, col_f2 = st.columns([0.7, 0.3])
    with col_f1:
        nombre_alumno = st.text_input("Nombre del estudiante:", placeholder="Nombre_Apellido")
    with col_f2:
        grupo_alumno = st.text_input("Grupo / Sección:", placeholder="Grupo")
    
    with st.form(key="form_observacion_prisma", clear_on_submit=False):
        nota_docente = st.text_area(
            "Dictado / Nota narrativa del docente:",
            height=130,
            placeholder="Ingresa la observación cualitativa. Presiona Cmd+Enter o Ctrl+Enter para procesar."
        )
        
        btn_analizar = st.form_submit_button("➕ Acumular observación (prisma-engine)", type="primary")

    if btn_analizar:
        if not nombre_alumno.strip():
            st.error("⚠️ Por favor ingresa el nombre del estudiante antes de procesar.")
        elif not grupo_alumno.strip():
            st.error("⚠️ Por favor ingresa el grupo o sección del estudiante antes de procesar.")
        elif not nota_docente.strip():
            st.error("⚠️ Por favor ingresa una nota de observación cualitativa.")
        else:
            with st.spinner("Procesando y acumulando vector en R⁸..."):
                try:
                    nom_eval = nombre_alumno.strip()
                    user_prompt = f"Estudiante: {nom_eval}\nNota narrativa del docente: \"{nota_docente}\""
                    
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
                                st.session_state.valores_db[nombre_oficial] += delta
                                st.session_state[f"temp_{nombre_oficial}"] = float(st.session_state.valores_db[nombre_oficial])
                                deltas_aplicados[nombre_oficial] = delta
                        
                        st.session_state.historial_observaciones.append({
                            "tipo": "IA",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "nota": nota_docente,
                            "deltas": deltas_aplicados,
                            "resultado_ia": resultado,
                            "vector_snapshot": dict(st.session_state.valores_db)
                        })
                        
                        fecha_iso = datetime.now().strftime("%y%m%d")
                        nom_clean = limpiar_cadena(nombre_alumno)
                        grp_clean = limpiar_cadena(grupo_alumno)
                        filename_auto = f"{fecha_iso}_{nom_clean}_{grp_clean}_PRISMA.json"
                        filepath_auto = os.path.join(DIR_EXPEDIENTES, filename_auto)
                        
                        exp_auto = {
                            "estudiante": nombre_alumno,
                            "grupo": grupo_alumno,
                            "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "vector_actual_db": st.session_state.valores_db,
                            "historial_observaciones": st.session_state.historial_observaciones
                        }
                        with open(filepath_auto, "w", encoding="utf-8") as f:
                            json.dump(exp_auto, f, indent=2, ensure_ascii=False)

                        st.session_state.mostrar_modal_resguardo = True
                        st.rerun()
                    else:
                        st.error(f"Error en Ollama (Código HTTP {response.status_code})")
                except requests.exceptions.Timeout:
                    st.error("Tiempo de espera agotado (Timeout).")
                except Exception as e:
                    st.error(f"Error de conexión con Ollama local: {e}")

    if st.session_state.historial_observaciones:
        st.markdown("---")
        st.subheader(f"📋 Historial de hitos acumulados ({len(st.session_state.historial_observaciones)})")
        
        for idx, obs in enumerate(reversed(st.session_state.historial_observaciones), 1):
            num_obs = len(st.session_state.historial_observaciones) - idx + 1
            tipo_hito = obs.get("tipo", "IA")
            if tipo_hito == "IA":
                etiqueta_tipo = "🤖 Inferencia IA"
            elif tipo_hito == "MANUAL":
                etiqueta_tipo = "🎨 Calibración manual docente"
            else:
                etiqueta_tipo = "🔄 Transición: Año nuevo, vida nueva"
                
            ts = obs.get("timestamp", "")
            
            with st.expander(f"Hito #{num_obs} — {ts} [{etiqueta_tipo}]", expanded=(num_obs == len(st.session_state.historial_observaciones))):
                if tipo_hito == "IA":
                    nota_txt = obs.get("nota", "")
                    st.write(f"**Nota de campo:** *\"{nota_txt}\"*")
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
                        st.caption("ℹ️ *El motor no detectó evidencias suficientes para aplicar deltas en esta nota.*")
                elif tipo_hito == "MANUAL":
                    just_txt = obs.get("justificacion", "")
                    st.write(f"**Razonamiento pedagógico del docente:** *\"{just_txt}\"*")
                    deltas_manuales = obs.get("deltas", {})
                    for eje_nom, delta_val in deltas_manuales.items():
                        if abs(delta_val) > 0.01:
                            st.caption(f"• **{eje_nom}:** `{fmt_db(delta_val)} dB` (Ajuste manual directo)")
                else:
                    just_txt = obs.get("justificacion", "")
                    st.write(f"**Registro de transición:** *\"{just_txt}\"*")

    st.markdown("---")
    st.subheader("2. Calibración manual docente (dB)")
    
    with st.form(key="form_calibracion_manual"):
        slider_vals_temporales = {}
        for eje in EJE_NOMBRES:
            slider_vals_temporales[eje] = st.slider(
                eje,
                min_value=-6.0,
                max_value=24.0,
                step=0.1,
                key=f"temp_{eje}"
            )
        
        justificacion_docente = st.text_area(
            "Razonamiento / Justificación pedagógica del ajuste (Obligatorio):",
            height=80,
            placeholder="Ejemplo: Se incrementa +1.5 dB en Razonamiento ético tras observar la mediación espontánea del alumno en el taller."
        )
        
        btn_aplicar_ajustes = st.form_submit_button("🎨 Registrar calibración manual como hito", type="secondary")

    if btn_aplicar_ajustes:
        if justificacion_docente.strip():
            deltas_manuales_hito = {}
            for eje in EJE_NOMBRES:
                delta_calc = slider_vals_temporales[eje] - st.session_state.valores_db[eje]
                deltas_manuales_hito[eje] = delta_calc
                st.session_state.valores_db[eje] = slider_vals_temporales[eje]
            
            st.session_state.historial_observaciones.append({
                "tipo": "MANUAL",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "justificacion": justificacion_docente,
                "deltas": deltas_manuales_hito,
                "vector_snapshot": dict(st.session_state.valores_db)
            })
            
            st.session_state.mostrar_modal_resguardo = True
            st.rerun()
        else:
            st.error("⚠️ Por favor ingresa el razonamiento pedagógico para registrar el ajuste manual.")

with col_der:
    st.subheader("3. Espejo metacognitivo — Espacio vectorial ℝ⁸")
    
    modo_vis = st.radio(
        "Visualización:",
        options=["Trayectoria completa (Todos los hitos)", "Comparativa personalizada", "Último estado vs base"],
        horizontal=True
    )
    
    valores_live = {eje: float(st.session_state.valores_db[eje]) for eje in EJE_NOMBRES}
    
    ejes_etiquetados = [
        f"<b>{FORMATO_EJES_RADAR[eje]}</b><br><span style='color:#4F46E5;'>({fmt_db(valores_live[eje])} dB)</span>"
        for eje in EJE_NOMBRES
    ]
    ejes_cerrados = ejes_etiquetados + [ejes_etiquetados[0]]
    
    todos_vectores = [list(valores_live.values())]
    for obs in st.session_state.historial_observaciones:
        if "vector_snapshot" in obs:
            todos_vectores.append(list(obs["vector_snapshot"].values()))
    
    max_valor_global = max([val for vec in todos_vectores for val in vec] + [0.0])
    limite_radar = 12.0 if max_valor_global <= 12.0 else (18.0 if max_valor_global <= 18.0 else 24.0)
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[0.0] * 9,
        theta=ejes_cerrados,
        mode="lines",
        line=dict(color="#94A3B8", width=1.5, dash="dash"),
        name="Línea base (0.0 dB)",
        hoverinfo="skip"
    ))

    num_hitos = len(st.session_state.historial_observaciones)
    
    PALETA_COLORES = [
        ("rgba(236, 72, 153, 0.8)", "rgba(236, 72, 153, 0.1)"),
        ("rgba(168, 85, 247, 0.8)", "rgba(168, 85, 247, 0.12)"),
        ("rgba(59, 130, 246, 0.85)", "rgba(59, 130, 246, 0.15)"),
        ("rgba(16, 185, 129, 0.9)", "rgba(16, 185, 129, 0.18)"),
        ("rgba(99, 102, 241, 1.0)", "rgba(99, 102, 241, 0.35)")
    ]

    if modo_vis == "Trayectoria completa (Todos los hitos)":
        if num_hitos > 0:
            for i, obs in enumerate(st.session_state.historial_observaciones):
                v_snap = obs.get("vector_snapshot", valores_live)
                vals = [v_snap[eje] for eje in EJE_NOMBRES]
                vals_cerrados = vals + [vals[0]]
                
                color_line, color_fill = PALETA_COLORES[i % len(PALETA_COLORES)]
                is_last = (i == num_hitos - 1)
                tipo_hito = obs.get("tipo", "IA")
                if tipo_hito == "IA":
                    tag_tipo = "IA"
                elif tipo_hito == "MANUAL":
                    tag_tipo = "Manual"
                else:
                    tag_tipo = "Año Nuevo"
                
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
                fill="toself",
                fillcolor="rgba(99, 102, 241, 0.35)",
                line=dict(color="#6366F1", width=3),
                marker=dict(size=7, color="#4F46E5"),
                name="Estado actual",
                hovertemplate="%{theta}<extra></extra>"
            ))

    elif modo_vis == "Comparativa personalizada":
        if num_hitos > 0:
            opciones_hitos = [f"Hito #{i+1} [{obs.get('tipo', 'IA')}] — {obs.get('timestamp', '')}" for i, obs in enumerate(st.session_state.historial_observaciones)]
            hitos_seleccionados = st.multiselect(
                "Selecciona los hitos a superponer:",
                options=opciones_hitos,
                default=[opciones_hitos[-1]]
            )
            
            for idx_str in hitos_seleccionados:
                i = int(idx_str.split("#")[1].split(" ")[0]) - 1
                obs = st.session_state.historial_observaciones[i]
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

    else:
        vals = [valores_live[eje] for eje in EJE_NOMBRES]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=ejes_cerrados,
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.35)",
            line=dict(color="#6366F1", width=3),
            marker=dict(size=7, color="#4F46E5"),
            name="Estado actual acumulado",
            hovertemplate="%{theta}<extra></extra>"
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-6, limite_radar],
                tickvals=[-6, 0, 12, 18, 24],
                ticktext=[
                    "-6 dB (Mínimo)",
                    "0.0 dB (Base)",
                    "+12 dB (Inicial / Fundamental)",
                    "+18 dB (Intermedio / Autónomo)",
                    "+24 dB (Avanzado / Experto)"
                ],
                angle=22.5,
                gridcolor="#CBD5E1",
                gridwidth=0.8,
                tickfont=dict(size=9, color="#475569")
            ),
            angularaxis=dict(
                tickfont=dict(size=10.5, color="#1E293B"),
                rotation=90,
                direction="clockwise",
                gridcolor="#E2E8F0"
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
        height=720,
        margin=dict(l=150, r=150, t=50, b=90)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("ℹ️ *Las lecturas en decibeles (dB) indican el **Índice de crecimiento** acumulado en cada dimensión respecto a la Línea base (0.0 dB).*")

if st.session_state.mostrar_modal_resguardo:
    modal_exportar_resguardo(nombre_alumno, grupo_alumno)
