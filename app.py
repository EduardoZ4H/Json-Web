import streamlit as st
import bcrypt
from controllers.xray_controller import process_file

# --- CONFIG ---
st.set_page_config(page_title="Excel → Xray JSON", layout="centered")

# --- LOGIN ---
def handle_login():
    st.title("Bienvenidos")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    try:
        users = st.secrets["users"]
    except Exception:
        # Fallback local
        users = {"admin": bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode()}

    if st.button("Ingresar"):
        if username in users:
            stored_hash = users[username].encode()
            if bcrypt.checkpw(password.encode(), stored_hash):
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
        else:
            st.error("Usuario o contraseña incorrectos")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    handle_login()
    st.stop()

st.sidebar.success(f"Usuario: {st.session_state['user']}")
if st.sidebar.button("Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

# --- APP ---
st.title("Convertir Excel a JSON (Jira / Xray)")

idioma_jira = st.selectbox("Idioma de Jira", ["es", "en"])

uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])

if uploaded_file:
    try:
        result = process_file(uploaded_file, idioma_jira)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    json_str = result["json"]
    resumen = result["resumen"]
    testset_details = result["testset_details"]

    st.success("JSON generado correctamente")

    # --- Tabla de Test Sets ---
    import pandas as pd
    data = []
    for ts, info in testset_details.items():
        data.append({
            "Test Set": ts,
            "# Casos": info["num_casos"],
            "Marca": info["marca"],
            "Etiquetas": ", ".join(info["etiquetas"]),
            "Directorio": info["directorio"]
        })
    df_details = pd.DataFrame(data)
    st.subheader("Detalles de Test Sets")
    st.dataframe(df_details)

    # --- Leyenda final ---
    total_casos = sum([info["num_casos"] for info in testset_details.values()])
    st.markdown(f"**Total de casos de prueba: {total_casos}**")

    # --- Botón de descarga JSON ---
    st.download_button(
        "Descargar JSON",
        json_str,
        file_name="xray.json",
        mime="application/json"
    )
