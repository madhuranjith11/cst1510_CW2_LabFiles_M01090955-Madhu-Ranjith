"""IT Operations Dashboard - Refactored with OOP."""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
from datetime import datetime
import pandas as pd

# Path setup
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.database_manager import DatabaseManager
from models.it_ticket import ITTicket

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login first.")
    st.stop()

st.title("💻 IT Ticket Dashboard")

# Initialize database
@st.cache_resource
def get_db():
    return DatabaseManager(str(ROOT / "database" / "intelligence_platform.db"))

db = get_db()

# Helper functions
def fetch_all_tickets():
    """Fetch all tickets and return as ITTicket objects."""
    rows = db.fetch_all(
        """SELECT id, ticket_id, priority, status, category,
           subject, description, created_date
           FROM it_tickets
           ORDER BY id DESC"""
    )

    tickets = []
    for row in rows:
        ticket = ITTicket(
            ticket_id=row["id"],
            ticket_ref=row["ticket_id"],
            priority=row["priority"],
            status=row["status"],
            category=row["category"],
            subject=row["subject"],
            description=row["description"],
            created_date=row["created_date"]
        )
        tickets.append(ticket)

    return tickets

def get_tickets_dataframe():
    """Get tickets as a pandas DataFrame for display."""
    tickets = fetch_all_tickets()
    if not tickets:
        return pd.DataFrame()

    data = [ticket.to_dict() for ticket in tickets]
    return pd.DataFrame(data)

# ---------------- Fetch Data ----------------
df = get_tickets_dataframe()

# ---------------- Visualization ----------------
if not df.empty:
    st.subheader("📊 Tickets Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Tickets", len(df))

    with col2:
        open_tickets = len(df[df["Status"] == "Open"])
        st.metric("Open Tickets", open_tickets)

    with col3:
        resolved_tickets = len(df[df["Status"] == "Resolved"])
        st.metric("Resolved Tickets", resolved_tickets)

    fig = px.histogram(
        df,
        x="Priority",
        color="Status",
        title="Tickets by Priority and Status",
        barmode="group"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Display Tickets Table ----------------
st.subheader("📋 All Tickets")

if df.empty:
    st.info("No tickets found. Create your first ticket below!")
else:
    st.dataframe(df, use_container_width=True)

# ---------------- CRUD Operations ----------------

# Create Ticket
with st.expander("➕ Create Ticket", expanded=False):
    tid = st.text_input("Ticket Reference ID", key="add_tid", placeholder="e.g., TKT-001")
    pr = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], key="add_pr")
    stts = st.selectbox("Status", ["Open", "In Progress", "Resolved"], key="add_stts")
    cat = st.text_input("Category", key="add_cat", placeholder="e.g., Hardware, Software")
    sub = st.text_input("Subject", key="add_sub", placeholder="Brief description")
    desc = st.text_area("Description", key="add_desc", placeholder="Detailed description of the issue...")

    if st.button("Submit Ticket"):
        if tid and sub and desc:
            db.execute_query(
                """INSERT INTO it_tickets
                   (ticket_id, priority, status, category, subject, description, created_date)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (tid, pr, stts, cat, sub, desc, str(datetime.now().date()))
            )
            st.success("✅ Ticket Created!")
            st.rerun()
        else:
            st.warning("Please fill in all required fields (Ticket ID, Subject, Description)")

# Update Ticket Status
with st.expander("🛠️ Update Ticket Status", expanded=False):
    tickets = fetch_all_tickets()

    if tickets:
        # Create selection options
        ticket_options = {f"ID {tk.get_id()}: {tk.get_ticket_ref()} - {tk.get_subject()}": tk.get_id()
                        for tk in tickets}

        selected_ticket = st.selectbox(
            "Select Ticket",
            options=list(ticket_options.keys()),
            key="update_select"
        )

        uid = ticket_options[selected_ticket]

        # Find the ticket object
        current_ticket = next((tk for tk in tickets if tk.get_id() == uid), None)

        if current_ticket:
            st.info(f"Current Status: **{current_ticket.get_status()}**")
            st.write(f"**Subject:** {current_ticket.get_subject()}")
            st.write(f"**Priority:** {current_ticket.get_priority()}")

        new_status = st.selectbox(
            "New Status",
            ["Open", "In Progress", "Resolved"],
            key="update_status"
        )

        if st.button("Update Status"):
            db.execute_query(
                "UPDATE it_tickets SET status = ? WHERE id = ?",
                (new_status, uid)
            )
            st.success(f"✅ Ticket {uid} updated to '{new_status}'!")
            st.rerun()
    else:
        st.info("No tickets available to update")

# Delete Ticket
with st.expander("🗑️ Delete Ticket", expanded=False):
    tickets = fetch_all_tickets()

    if tickets:
        ticket_options = {f"ID {tk.get_id()}: {tk.get_ticket_ref()} - {tk.get_subject()} [{tk.get_priority()}]": tk.get_id()
                        for tk in tickets}

        selected_ticket = st.selectbox(
            "Select Ticket to Delete",
            options=list(ticket_options.keys()),
            key="del_select"
        )

        del_id = ticket_options[selected_ticket]

        # Show details
        current_ticket = next((tk for tk in tickets if tk.get_id() == del_id), None)
        if current_ticket:
            st.warning(f"⚠️ You are about to delete: {current_ticket}")

        if st.button("Delete Ticket", type="primary"):
            db.execute_query("DELETE FROM it_tickets WHERE id = ?", (del_id,))
            st.success(f"✅ Ticket {del_id} deleted!")
            st.rerun()
    else:
        st.info("No tickets available to delete")
