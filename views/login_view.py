import streamlit as st

def show_login():
    st.title("🔐 Acceso restringido")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_clicked = st.button("Ingresar")

    return username, password, login_clicked
