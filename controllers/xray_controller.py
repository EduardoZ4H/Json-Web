import pandas as pd
import streamlit as st
from models.xray_model import validate_dataframe, generate_xray_json
from utils.mappings import mappings

def process_file(uploaded_file, idioma_jira):

    df = pd.read_excel(uploaded_file)

    required_columns = [
        "REQ", "Flujo-ID Caso", "Importancia", "Tipo de prueba",
        "Descripción del caso de prueba", "Precondiciones",
        "Pasos para ejecutar", "Resultados esperados",
        "Responsable", "Etiquetas", "Directorio", "Test Set"
    ]

    missing_rows = validate_dataframe(df, required_columns)

    if not missing_rows.empty:
        st.error(f"❌ El archivo tiene {len(missing_rows)} filas incompletas")
        st.stop()

    return generate_xray_json(df, mappings, idioma_jira)
