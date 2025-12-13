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

from app.db.incidents import (
    get_all_incidents, insert_incident, update_incident_status, delete_incident, get_incident_statistics
)

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

st.title("🛡 Cybersecurity Dashboard")

# ---------------- Fetch Data ----------------
df = get_all_incidents()
stats = get_incident_statistics() if not df.empty else None

# ---------------- Visualization ----------------
if stats:
    st.subheader("📊 Incident Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig1 = px.bar(stats["by_type"], x="incident_type", y="count", title="Count by Type")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(stats["by_severity"], x="severity", y="count", title="Count by Severity")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.pie(stats["by_status"], names="status", values="count", title="Status Distribution")
        st.plotly_chart(fig3, use_container_width=True)

# ---------------- Display Incidents Table ----------------
st.subheader("📋 All Cybersecurity Incidents")
st.dataframe(df, use_container_width=True)

# ---------------- CRUD Operations ----------------

# Add Incident
with st.expander("➕ Add Incident", expanded=False):
    date = st.date_input("Incident Date")
    incident_type = st.text_input("Type", key="add_type")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], key="add_severity")
    status = st.selectbox("Status", ["Open", "Investigating", "Resolved"], key="add_status")
    desc = st.text_area("Description", key="add_desc")

    if st.button("Submit Incident"):
        insert_incident(
            str(date), incident_type, severity, status, desc,
            reported_by=st.session_state.username
        )
        st.success("Incident Added!")
        st.experimental_rerun()

# Update Incident
with st.expander("✏️ Update Incident Status", expanded=False):
    upd_id = st.number_input("Incident ID", min_value=1, step=1, key="upd_id")
    new_status = st.selectbox("New Status", ["Open", "Investigating", "Resolved"], key="upd_status")

    if st.button("Update Status"):
        rows = update_incident_status(upd_id, new_status)
        if rows:
            st.success(f"Incident {upd_id} updated successfully!")
        else:
            st.warning(f"No incident found with ID {upd_id}")
        st.experimental_rerun()

# Delete Incident
with st.expander("🗑 Delete Incident", expanded=False):
    del_id = st.number_input("Incident ID", min_value=1, step=1, key="del_id")
    if st.button("Delete Incident"):
        rows = delete_incident(del_id)
        if rows:
            st.success(f"Incident {del_id} deleted successfully!")
        else:
            st.warning(f"No incident found with ID {del_id}")
        st.experimental_rerun()
