import sys
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import openai
import os

# ---------------- Path Setup ----------------
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
APP_ROOT = ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# ---------------- Load API Key ----------------
load_dotenv(APP_ROOT / ".env")
api_key = os.getenv("OPENAI_API_KEY")

# Validate API key
if not api_key:
    st.error("❌ OPENAI_API_KEY not found in .env file")
    st.stop()

api_key = api_key.strip()
if not api_key.startswith("sk-"):
    st.error("❌ Invalid API key format. Should start with 'sk-'")
    st.info("Get your API key from: https://platform.openai.com/api-keys")
    st.stop()

openai.api_key = api_key

# ---------------- Check Login ----------------
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

st.title("🤖 AI Assistant Dashboard")

# ---------------- Tabs ----------------
tabs = st.tabs(["Cybersecurity", "Data Science", "IT Operations"])

# System prompts
system_prompts = {
    "Cybersecurity": """You are a cybersecurity expert assistant.
Analyze incidents, threats, and provide technical guidance.""",
    "Data Science": """You are a data science expert assistant.
Help with analysis, visualization, and statistical insights.""",
    "IT Operations": """You are an IT operations expert assistant.
Help troubleshoot issues, optimize systems, and manage tickets."""
}

# ---------------- Initialize chat history ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {d: [] for d in system_prompts.keys()}

# ---------------- Helper Function ----------------
def chat_with_gpt(domain, user_message):
    try:
        # Append user message
        st.session_state.chat_history[domain].append({"role": "user", "content": user_message})

        # Build messages for API
        messages = [{"role": "system", "content": system_prompts[domain]}] + st.session_state.chat_history[domain]

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=500
        )

        answer = response.choices[0].message.content
        st.session_state.chat_history[domain].append({"role": "assistant", "content": answer})
        return answer

    except openai.AuthenticationError:
        st.error("❌ Invalid API key. Please check your .env file.")
        st.info("Get your API key from: https://platform.openai.com/api-keys")
        # Remove the failed user message
        if st.session_state.chat_history[domain][-1]["role"] == "user":
            st.session_state.chat_history[domain].pop()
        return None

    except openai.RateLimitError:
        st.error("⚠️ Rate limit exceeded. Please wait a moment.")
        if st.session_state.chat_history[domain][-1]["role"] == "user":
            st.session_state.chat_history[domain].pop()
        return None

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        if st.session_state.chat_history[domain][-1]["role"] == "user":
            st.session_state.chat_history[domain].pop()
        return None

# ---------------- UI Loop for Tabs ----------------
for i, domain in enumerate(system_prompts.keys()):
    with tabs[i]:
        st.subheader(f"💬 {domain} Chat")

        # Display previous messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history[domain]:
                if msg["role"] == "user":
                    st.markdown(f"**You:** {msg['content']}")
                else:
                    st.markdown(f"**AI:** {msg['content']}")

        # Input box and buttons
        user_input = st.text_input("Type your message:", key=f"input_{domain}")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Send", key=f"send_{domain}") and user_input.strip():
                with st.spinner("Thinking..."):
                    result = chat_with_gpt(domain, user_input.strip())
                    if result:  # Only rerun if successful
                        st.rerun()
        with col2:
            if st.button("Clear Chat", key=f"clear_{domain}"):
                st.session_state.chat_history[domain] = []
                st.rerun()
