import streamlit as st
from models.user_model import authenticate

def handle_login():
    users = st.secrets["users"]

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        from views.login_view import show_login
        username, password, login_clicked = show_login()

        if login_clicked:
            if authenticate(username, password, users):
                st.session_state["logged_in"] = True
                st.session_state["user"] = username
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")

        st.stop()

    st.sidebar.success(f"👤 Usuario: {st.session_state['user']}")

    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
