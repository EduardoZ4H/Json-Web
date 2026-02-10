import streamlit as st
import pandas as pd
import json
import bcrypt


def login():
    st.title("🔐 Acceso restringido")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    users = st.secrets["users"]

    if st.button("Ingresar"):
        if username in users:
            stored_hash = users[username].encode()
            if bcrypt.checkpw(password.encode(), stored_hash):
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
        else:
            st.error("❌ Usuario o contraseña incorrectos")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

st.sidebar.success(f"👤 Usuario: {st.session_state['user']}")

if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()




# --- CONFIG ---
st.set_page_config(page_title="Excel → Xray JSON", layout="centered")
st.title("📄 Excel → Xray JSON (Jira / Xray)")

# --- MAPEOS de Jira ---
map_plataforma = {
    "iOS": 10110, "Android": 10111, "iOS & Android": 10112, "POS": 10024, "Web": 10026,
    "Web & Apps": 10025, "Web, Apps & POS": 10027, "Otro": 10113,
    "Call Center Ordering": 10154, "Web & Apps & Call Center Ordering": 10155,
    "Agregadores": 10161, "WhatsApp": 10168, "MDW": 10169, "Core": 10170,
    "PC Gerente": 10172
}

map_ambiente = {
    "QA": 10086, "PROD": 10087
}

map_marca = {
    "Chilis": 10043, "VIPS": 10044, "Italiannis": 10045, "PFChangs": 10046,
    "El Portón": 10047, "The Cheesecake Factory": 10048, "Starbucks": 10049,
    "Domino's Pizza": 10050, "Burger King": 10051, "WOW+": 10052,
    "ClubBy": 10053, "Foster’s Hollywood": 10054, "Archies": 10055,
    "Ginos": 10056, "TGI Fridays": 10057, "MyALSEA": 10147,
    "COG": 10148, "Delivery ALSEA": 10149, "ANS": 10150,
    "Casuales (Todos)": 10171, "MDW Spain": 10186
}

# --- UI ---
idioma_jira = st.selectbox("🌎 Idioma de Jira", ["es", "en"])
precond_key = "data" if idioma_jira == "en" else "precondiciones"

uploaded_file = st.file_uploader(
    "📤 Sube el archivo Excel",
    type=["xlsx"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    required_columns = [
        "REQ", "Flujo-ID Caso", "Importancia", "Tipo de prueba",
        "Descripción del caso de prueba", "Precondiciones",
        "Pasos para ejecutar", "Resultados esperados",
        "Responsable", "Etiquetas", "Directorio", "Test Set"
    ]

    missing_rows = df[df[required_columns].isnull().any(axis=1)]

    if not missing_rows.empty:
        st.error(
            f"❌ El archivo tiene {len(missing_rows)} filas con campos obligatorios vacíos"
        )
        st.stop()

    output_json = []
    testset_ids = {}
    current_id = 1

    # --- Crear Test Sets ---
    for testset, group in df.groupby("Test Set"):
        etiquetas_raw = group["Etiquetas"].dropna().astype(str).tolist()
        etiquetas = [e.strip() for e in etiquetas_raw[0].split(",") if e.strip()] if etiquetas_raw else []

        testset_ids[testset] = str(current_id)

        output_json.append({
            "xray_issue_type": "testset",
            "xray_id": str(current_id),
            "fields": {
                "summary": testset,
                "labels": etiquetas
            }
        })

        current_id += 1

    # --- Crear Tests ---
    for _, row in df.iterrows():
        plataforma_id = map_plataforma.get(str(row.get("Plataforma")).strip())
        ambiente_id = map_ambiente.get(str(row.get("Ambiente")).strip())
        marca_id = map_marca.get(str(row.get("Marca")).strip())

        steps = [{
            "action": str(row["Pasos para ejecutar"]).strip(),
            "result": str(row["Resultados esperados"]).strip(),
            precond_key: str(row["Precondiciones"]).strip()
        }]

        etiquetas = [e.strip() for e in str(row["Etiquetas"]).split(",") if e.strip()]

        test_entry = {
            "xray_issue_type": "test",
            "fields": {
                "summary": str(row["Descripción del caso de prueba"]),
                "priority": {"name": "High"},
                "description": str(row["Flujo-ID Caso"]),
                "labels": etiquetas,
                "customfield_10039": {"id": str(marca_id)} if marca_id else None,
                "customfield_10037": {"id": str(plataforma_id)} if plataforma_id else None,
                "customfield_10057": {"id": str(ambiente_id)} if ambiente_id else None,
                "assignee": {"name": str(row["Responsable"])} if pd.notna(row["Responsable"]) else None
            },
            "xray_test_repository_folder": str(row["Directorio"]),
            "xray_testtype": "Manual",
            "steps": steps,
            "xray_test_sets": [testset_ids.get(row["Test Set"])]
        }

        test_entry["fields"] = {k: v for k, v in test_entry["fields"].items() if v is not None}
        output_json.append(test_entry)

    json_str = json.dumps(output_json, indent=2, ensure_ascii=False)

    st.success("✅ JSON generado correctamente")
    st.download_button(
        "⬇️ Descargar JSON",
        json_str,
        file_name="xray.json",
        mime="application/json"
    )
