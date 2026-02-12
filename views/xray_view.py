import streamlit as st

def show_main():
    st.set_page_config(page_title="Excel → Xray JSON", layout="centered")
    st.title("📄 Excel → Xray JSON (Jira / Xray)")

    idioma_jira = st.selectbox("🌎 Idioma de Jira", ["es", "en"])
    uploaded_file = st.file_uploader("📤 Sube el archivo Excel", type=["xlsx"])

    return idioma_jira, uploaded_file
