"""AI Assistant Dashboard - Refactored with OOP."""

import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import os

# Path setup
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .streamlit/.env
ENV_PATH = ROOT / ".streamlit" / ".env"
load_dotenv(ENV_PATH)

# Verify the API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    api_key = api_key.strip()
    os.environ["OPENAI_API_KEY"] = api_key  # Make sure it's set

from services.ai_assistant import AIAssistant

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

st.title("🤖 AI Assistant Dashboard")

# System prompts for each domain
SYSTEM_PROMPTS = {
    "Cybersecurity": """You are a cybersecurity expert assistant.
Analyze incidents, threats, and provide technical guidance on security matters.""",

    "Data Science": """You are a data science expert assistant.
Help with analysis, visualization, statistical insights, and machine learning concepts.""",

    "IT Operations": """You are an IT operations expert assistant.
Help troubleshoot issues, optimize systems, manage tickets, and provide technical support."""
}

# Initialize AI assistants in session state
if "ai_assistants" not in st.session_state:
    st.session_state.ai_assistants = {
        domain: AIAssistant(system_prompt=prompt)
        for domain, prompt in SYSTEM_PROMPTS.items()
    }

# Check if API key is valid
api_valid = st.session_state.ai_assistants["Cybersecurity"].is_api_key_valid()

if not api_valid:
    st.warning("⚠️ OpenAI API key not configured or invalid.")

# ---------------- Tabs ----------------
tabs = st.tabs(["🛡️ Cybersecurity", "📊 Data Science", "💻 IT Operations"])

# ---------------- UI Loop for Tabs ----------------
for i, (domain, system_prompt) in enumerate(SYSTEM_PROMPTS.items()):
    with tabs[i]:
        st.subheader(f"💬 {domain} AI Assistant")

        # Get the AI assistant for this domain
        ai_assistant = st.session_state.ai_assistants[domain]

        # Display chat history
        chat_history = ai_assistant.get_history()

        if chat_history:
            chat_container = st.container()
            with chat_container:
                for msg in chat_history:
                    if msg["role"] == "user":
                        st.markdown(f"**🧑 You:** {msg['content']}")
                    else:
                        st.markdown(f"**🤖 AI:** {msg['content']}")
        else:
            st.info(f"Start a conversation with the {domain} AI assistant!")

        # Input area
        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                "Type your message:",
                key=f"input_{domain}",
                placeholder=f"Ask something about {domain.lower()}..."
            )

        with col2:
            send_button = st.button("Send", key=f"send_{domain}", use_container_width=True)
            clear_button = st.button("Clear", key=f"clear_{domain}", use_container_width=True)

        # Handle send
        if send_button and user_input.strip():
            if not api_valid:
                st.error("❌ Cannot send message. API key not configured.")
            else:
                with st.spinner("🤔 Thinking..."):
                    response = ai_assistant.send_message(user_input.strip())
                    st.rerun()

        # Handle clear
        if clear_button:
            ai_assistant.clear_history()
            st.success("Chat history cleared!")
            st.rerun()
