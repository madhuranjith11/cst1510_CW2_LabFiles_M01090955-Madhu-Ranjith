import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

APP_ROOT = ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

import streamlit as st
from auth import (
    login_user, register_user,
    validate_username, validate_password,
    check_password_strength, create_session
)


st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

# Initialize session
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

st.title("🔐 Multi-Domain Intelligence Platform")

# If logged in
if st.session_state.logged_in:
    st.success(f"Logged in as **{st.session_state.username}**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
    st.stop()

# ------------------------ Tabs ------------------------
tab_login, tab_register = st.tabs(["Login", "Register"])

# ================= LOGIN ======================
with tab_login:
    st.subheader("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            create_session(username)
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

# ================= REGISTER ======================
with tab_register:
    st.subheader("Register")

    new_user = st.text_input("New Username", key="reg_username")
    pw = st.text_input("Password", type="password", key="reg_password")
    confirm_pw = st.text_input("Confirm Password", type="password", key="reg_confirm")

    if st.button("Register User", key="register_button"):
        ok, msg = validate_username(new_user)
        if not ok:
            st.error(msg)
            st.stop()

        ok, msg = validate_password(pw)
        if not ok:
            st.error(msg)
            st.stop()

        if pw != confirm_pw:
            st.error("Passwords do not match.")
            st.stop()

        st.info(f"Password Strength: {check_password_strength(pw)}")

        if register_user(new_user, pw):
            st.success("User Registered Successfully!")
        else:
            st.error("Username already exists.")
