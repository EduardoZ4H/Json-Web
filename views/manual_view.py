import streamlit as st
from controllers.xray_controller import process_manual_cases

def manual_cases_view():
    st.subheader("📝 Crear casos de prueba desde cero")
    
    req = st.text_input("REQ (identificador principal, obligatorio)")
    num_casos = st.number_input("Número de casos", min_value=1, value=1)

    if req and num_casos > 0:
        casos = []
        for i in range(1, num_casos + 1):
            with st.expander(f"Caso {i}", expanded=True):
                descripcion = st.text_input(f"Descripción del caso de prueba #{i}", key=f"desc_{i}")
                precond = st.text_area(f"Precondiciones #{i}", key=f"pre_{i}")
                pasos = st.text_area(f"Pasos para ejecutar #{i}", key=f"steps_{i}")
                resultados = st.text_area(f"Resultados esperados #{i}", key=f"res_{i}")
                responsable = st.text_input(f"Responsable #{i}", key=f"resp_{i}")
                test_set = st.text_input(f"Test Set #{i}", key=f"ts_{i}")
                etiquetas = st.text_input(f"Etiquetas #{i}", key=f"lab_{i}")
                directorio = st.text_input(f"Directorio #{i}", key=f"dir_{i}")

                casos.append({
                    "Descripción del caso de prueba": descripcion,
                    "Precondiciones": precond,
                    "Pasos para ejecutar": pasos,
                    "Resultados esperados": resultados,
                    "Responsable": responsable,
                    "Test Set": test_set,
                    "Etiquetas": etiquetas,
                    "Directorio": directorio
                })

        if st.button("✅ Generar JSON manual"):
            try:
                json_str = process_manual_cases(req, casos)
                st.success("✅ JSON generado correctamente")
                st.download_button(
                    "⬇️ Descargar JSON",
                    json_str,
                    file_name="xray_manual.json",
                    mime="application/json"
                )
            except ValueError as e:
                st.error(str(e))
