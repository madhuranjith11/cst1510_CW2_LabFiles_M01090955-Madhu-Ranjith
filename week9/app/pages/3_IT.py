import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
from datetime import datetime

# Path setup
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
APP_ROOT = ROOT / "app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app.db.tickets import (
    get_all_tickets, insert_ticket, update_ticket_status, delete_ticket
)

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login first.")
    st.stop()

st.title("💻 IT Ticket Dashboard")

# ---------------- Fetch Data ----------------
df = get_all_tickets()

# ---------------- Visualization ----------------
if not df.empty:
    st.subheader("📊 Tickets Overview")
    fig = px.histogram(df, x="priority", color="status", title="Tickets by Priority")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Display Tickets Table ----------------
st.subheader("📋 All Tickets")
st.dataframe(df, use_container_width=True)

# ---------------- CRUD Operations ----------------

# Create Ticket
with st.expander("➕ Create Ticket", expanded=False):
    tid = st.text_input("Ticket ID", key="add_tid")
    pr = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="add_pr")
    stts = st.selectbox("Status", ["Open", "In Progress", "Resolved"], key="add_stts")
    cat = st.text_input("Category", key="add_cat")
    sub = st.text_input("Subject", key="add_sub")
    desc = st.text_area("Description", key="add_desc")

    if st.button("Submit Ticket"):
        insert_ticket(
            tid, pr, stts, cat, sub, desc,
            created_date=str(datetime.now().date())
        )
        st.success("Ticket Created!")
        st.experimental_rerun()

# Update Ticket Status
with st.expander("🛠 Update Ticket Status", expanded=False):
    uid = st.number_input("Ticket DB ID", step=1, key="update_uid")
    new_status = st.selectbox("New Status", ["Open", "In Progress", "Resolved"], key="update_status")
    if st.button("Update Status"):
        update_ticket_status(uid, new_status)
        st.success("Ticket Status Updated!")
        st.experimental_rerun()

# Delete Ticket
with st.expander("🗑 Delete Ticket", expanded=False):
    del_id = st.number_input("Delete Ticket ID", step=1, key="del_tid")
    if st.button("Delete Ticket"):
        rows = delete_ticket(del_id)
        if rows:
            st.success(f"Ticket {del_id} deleted successfully!")
        else:
            st.warning(f"No ticket found with ID {del_id}")
        st.experimental_rerun()
