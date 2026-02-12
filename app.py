import streamlit as st
from controllers.auth_controller import handle_login
from controllers.xray_controller import process_file
from views.xray_view import show_main

handle_login()

idioma_jira, uploaded_file = show_main()

if uploaded_file:
    json_str = process_file(uploaded_file, idioma_jira)

    st.success("✅ JSON generado correctamente")
    st.download_button(
        "⬇️ Descargar JSON",
        json_str,
        file_name="xray.json",
        mime="application/json"
    )
