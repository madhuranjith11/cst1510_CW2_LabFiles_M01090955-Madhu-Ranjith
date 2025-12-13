"""Home page with login/register functionality."""

import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Path setup
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .streamlit/.env
ENV_PATH = ROOT / ".streamlit" / ".env"
load_dotenv(ENV_PATH)

from services.database_manager import DatabaseManager
from services.auth_manager import AuthManager

# Page config
st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="🔐",
    layout="centered"
)

# Initialize database and auth manager
@st.cache_resource
def get_managers():
    db_path = str(ROOT / "database" / "intelligence_platform.db")
    db = DatabaseManager(db_path)
    db.connect()
    auth = AuthManager(db)
    return db, auth

db, auth = get_managers()

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None

st.title("🔐 Multi-Domain Intelligence Platform")

# If logged in
if st.session_state.logged_in:
    st.success(f"✅ Logged in as **{st.session_state.username}** ({st.session_state.role})")

    st.markdown("---")
    st.subheader("📋 Available Modules")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("### 🛡️ Cybersecurity")
        st.write("Monitor incidents")

    with col2:
        st.markdown("### 📊 Data Science")
        st.write("Analyze datasets")

    with col3:
        st.markdown("### 💻 IT Operations")
        st.write("Manage tickets")

    with col4:
        st.markdown("### 🤖 AI Assistant")
        st.write("Chat with AI")

    st.markdown("---")
    st.info("👈 Use the sidebar to navigate between modules")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

    st.stop()

# Login/Register tabs
tab_login, tab_register = st.tabs(["Login", "Register"])

# ================= LOGIN ======================
with tab_login:
    st.subheader("Login")

    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):
        if not username or not password:
            st.warning("Please enter both username and password")
        else:
            try:
                user = auth.login_user(username, password)

                if user:
                    st.session_state.logged_in = True
                    st.session_state.username = user.get_username()
                    st.session_state.role = user.get_role()
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            except Exception as e:
                st.error(f"Login error: {str(e)}")

# ================= REGISTER ======================
with tab_register:
    st.subheader("Register")

    new_user = st.text_input("New Username", key="reg_username")
    pw = st.text_input("Password", type="password", key="reg_password")
    confirm_pw = st.text_input("Confirm Password", type="password", key="reg_confirm")

    if st.button("Register User", key="register_button"):
        # Validate username
        ok, msg = auth.validate_username(new_user)
        if not ok:
            st.error(msg)
            st.stop()

        # Validate password
        ok, msg = auth.validate_password(pw)
        if not ok:
            st.error(msg)
            st.stop()

        # Check password match
        if pw != confirm_pw:
            st.error("Passwords do not match")
            st.stop()

        # Show password strength
        strength = auth.check_password_strength(pw)
        st.info(f"Password Strength: {strength}")

        # Register user
        try:
            if auth.register_user(new_user, pw):
                st.success("User Registered Successfully! Please login.")
            else:
                st.error("Username already exists")
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
