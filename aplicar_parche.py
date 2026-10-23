import pathlib
import ast
import shutil

app_path = pathlib.Path.home() / "PRISMA_App" / "app.py"
if not app_path.exists():
    app_path = pathlib.Path("app.py")

if not app_path.exists():
    print("❌ No se encontró ~/PRISMA_App/app.py")
    exit(1)

# Crear respaldo de seguridad
backup_path = app_path.with_suffix(".py.bak")
shutil.copy(app_path, backup_path)

code = app_path.read_text(encoding="utf-8")

def insert_with_indent(full_code, target_part, replacement_multiline):
    lines = full_code.splitlines(keepends=True)
    out_lines = []
    matched = False
    for line in lines:
        if target_part in line and not matched:
            matched = True
            indent = line[:len(line) - len(line.lstrip())]
            replacement_lines = replacement_multiline.strip().splitlines()
            for r_line in replacement_lines:
                out_lines.append(indent + r_line + "\n")
        else:
            out_lines.append(line)
    return "".join(out_lines)

# 1. UI de Educabilidad
ui_block = """st.subheader("2. Registro de Nota Narrativa Docente")

st.markdown("##### Nota de Estado de Educabilidad")
tipo_reg = st.radio("Registro de educabilidad:", ["Sin registro", "Con registro"], horizontal=True, key="input_educabilidad_modo")

if tipo_reg == "Con registro":
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.selectbox("Sueño / Descanso:", ["> 7 horas (Óptimo)", "5 - 6 horas (Atención / Fatiga)", "< 5 horas (Vulnerabilidad Severa)"], key="input_descanso")
    with col_e2:
        st.selectbox("Alimentación / Nutrición:", ["Completa / Adecuada", "Insuficiente / Parcial", "Sin Alimento / Ayuno"], key="input_alimentacion")"""

# 2. Prompt Prefix de Educabilidad
prompt_block = """prefix_edu = ""
if st.session_state.get("input_educabilidad_modo") == "Con registro":
    sueno_val = st.session_state.get("input_descanso", "N/A")
    nutri_val = st.session_state.get("input_alimentacion", "N/A")
    prefix_edu = f"Datos de educabilidad: Sueño: {sueno_val}, Soporte Nutricional: {nutri_val}.\n"

user_prompt = f"Estudiante: {nom_in}\n{prefix_edu}Nota narrativa: \"{nota_docente}\"" """

if 'key="input_educabilidad_modo"' not in code:
    code = insert_with_indent(code, 'st.subheader("2. Registro de Nota Narrativa Docente")', ui_block)

if 'prefix_edu =' not in code:
    code = insert_with_indent(code, 'user_prompt = f"Estudiante:', prompt_block)

# 3. Payload System Prompt
if '"system": PROMPT_PRISMA_SYSTEM' not in code and '"prompt": user_prompt' in code:
    code = code.replace('"prompt": user_prompt,', '"system": PROMPT_PRISMA_SYSTEM,\n                "prompt": user_prompt,', 1)

try:
    ast.parse(code)
    app_path.write_text(code, encoding="utf-8")
    print("✅ ¡Sintaxis validada de Python! Parche aplicado con éxito en app.py")
except SyntaxError as err:
    print(f"❌ Error de sintaxis en línea {err.lineno}: {err.msg}")
    shutil.copy(backup_path, app_path)
    print("Se restauró la versión de respaldo ~/PRISMA_App/app.py.bak")
