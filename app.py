import streamlit as st
from controllers.auth_controller import handle_login
from controllers.xray_controller import process_file
from views.xray_view import show_main

handle_login()

idioma_jira, uploaded_file = show_main()

if uploaded_file:
    result = process_file(uploaded_file, idioma_jira)

    json_str = result["json"]
    resumen = result["resumen"]

    st.success("✅ JSON generado correctamente")

    st.subheader("📊 Resumen de generación")

    col1, col2 = st.columns(2)

    col1.metric("Test Sets", resumen["testsets"])
    col1.metric("Tests", resumen["tests"])

    col2.metric("Marcas", len(resumen["marcas"]))
    col2.metric("Plataformas", len(resumen["plataformas"]))

    with st.expander("🔍 Ver detalles"):
        st.write("Marcas:", list(resumen["marcas"]))
        st.write("Plataformas:", list(resumen["plataformas"]))
        st.write("Ambientes:", list(resumen["ambientes"]))
        st.write("Directorios:", list(resumen["directorios"]))
        st.write("Labels:", list(resumen["labels"]))

    st.download_button(
        "⬇️ Descargar JSON",
        json_str,
        file_name="xray.json",
        mime="application/json"
    )
