"""Cybersecurity Dashboard - Refactored with OOP."""

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
from models.security_incident import SecurityIncident

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login from Home Page")
    st.stop()

st.title("🛡️ Cybersecurity Dashboard")

# Initialize database
@st.cache_resource
def get_db():
    return DatabaseManager(str(ROOT / "database" / "intelligence_platform.db"))

db = get_db()

# Helper function to fetch incidents as objects
def fetch_all_incidents():
    """Fetch all incidents and return as SecurityIncident objects."""
    rows = db.fetch_all(
        """SELECT id, date, incident_type, severity, status,
           description, reported_by
           FROM cyber_incidents
           ORDER BY id DESC"""
    )

    incidents = []
    for row in rows:
        incident = SecurityIncident(
            incident_id=row["id"],
            incident_date=row["date"],  # Changed from incident_date to date
            incident_type=row["incident_type"],
            severity=row["severity"],
            status=row["status"],
            description=row["description"],
            reported_by=row["reported_by"]
        )
        incidents.append(incident)

    return incidents

def get_incidents_dataframe():
    """Get incidents as a pandas DataFrame for display."""
    incidents = fetch_all_incidents()
    if not incidents:
        return pd.DataFrame()

    data = [incident.to_dict() for incident in incidents]
    return pd.DataFrame(data)

def get_incident_statistics():
    """Calculate statistics from incidents."""
    incidents = fetch_all_incidents()

    if not incidents:
        return None

    # Count by type
    type_counts = {}
    severity_counts = {}
    status_counts = {}

    for incident in incidents:
        # By type
        incident_type = incident.get_incident_type()
        type_counts[incident_type] = type_counts.get(incident_type, 0) + 1

        # By severity
        severity = incident.get_severity()
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # By status
        status = incident.get_status()
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "by_type": pd.DataFrame(list(type_counts.items()), columns=["incident_type", "count"]),
        "by_severity": pd.DataFrame(list(severity_counts.items()), columns=["severity", "count"]),
        "by_status": pd.DataFrame(list(status_counts.items()), columns=["status", "count"])
    }

# ---------------- Fetch Data ----------------
df = get_incidents_dataframe()
stats = get_incident_statistics()

# ---------------- Visualization ----------------
if stats:
    st.subheader("📊 Incident Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        fig1 = px.bar(
            stats["by_type"],
            x="incident_type",
            y="count",
            title="Count by Type",
            labels={"incident_type": "Incident Type", "count": "Count"}
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            stats["by_severity"],
            x="severity",
            y="count",
            title="Count by Severity",
            labels={"severity": "Severity", "count": "Count"},
            color="severity",
            color_discrete_map={
                "Low": "green",
                "Medium": "yellow",
                "High": "orange",
                "Critical": "red"
            }
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        fig3 = px.pie(
            stats["by_status"],
            names="status",
            values="count",
            title="Status Distribution"
        )
        st.plotly_chart(fig3, use_container_width=True)

# ---------------- Display Incidents Table ----------------
st.subheader("📋 All Cybersecurity Incidents")

if df.empty:
    st.info("No incidents found. Add your first incident below!")
else:
    st.dataframe(df, use_container_width=True)

# ---------------- CRUD Operations ----------------

# Add Incident
with st.expander("➕ Add Incident", expanded=False):
    date = st.date_input("Incident Date", value=datetime.now().date())
    incident_type = st.text_input("Type", key="add_type", placeholder="e.g., Phishing Attack")
    severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"], key="add_severity")
    status = st.selectbox("Status", ["Open", "Investigating", "Resolved"], key="add_status")
    desc = st.text_area("Description", key="add_desc", placeholder="Describe the incident...")

    if st.button("Submit Incident"):
        if incident_type and desc:
            db.execute_query(
                """INSERT INTO cyber_incidents
                   (date, incident_type, severity, status, description, reported_by)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (str(date), incident_type, severity, status, desc, st.session_state.username)
            )
            st.success("✅ Incident Added!")
            st.rerun()
        else:
            st.warning("Please fill in all required fields")

# Update Incident
with st.expander("✏️ Update Incident Status", expanded=False):
    # Get all incidents for selection
    incidents = fetch_all_incidents()

    if incidents:
        # Create selection options
        incident_options = {f"ID {inc.get_id()}: {inc.get_incident_type()}": inc.get_id()
                          for inc in incidents}

        selected_incident = st.selectbox(
            "Select Incident",
            options=list(incident_options.keys()),
            key="upd_select"
        )

        upd_id = incident_options[selected_incident]

        # Find the incident object
        current_incident = next((inc for inc in incidents if inc.get_id() == upd_id), None)

        if current_incident:
            st.info(f"Current Status: **{current_incident.get_status()}**")
            st.write(f"**Description:** {current_incident.get_description()}")

        new_status = st.selectbox(
            "New Status",
            ["Open", "Investigating", "Resolved", "Closed"],
            key="upd_status"
        )

        if st.button("Update Status"):
            db.execute_query(
                "UPDATE cyber_incidents SET status = ? WHERE id = ?",
                (new_status, upd_id)
            )
            st.success(f"✅ Incident {upd_id} updated to '{new_status}'!")
            st.rerun()
    else:
        st.info("No incidents available to update")

# Delete Incident
with st.expander("🗑️ Delete Incident", expanded=False):
    incidents = fetch_all_incidents()

    if incidents:
        incident_options = {f"ID {inc.get_id()}: {inc.get_incident_type()} [{inc.get_severity()}]": inc.get_id()
                          for inc in incidents}

        selected_incident = st.selectbox(
            "Select Incident to Delete",
            options=list(incident_options.keys()),
            key="del_select"
        )

        del_id = incident_options[selected_incident]

        # Show details
        current_incident = next((inc for inc in incidents if inc.get_id() == del_id), None)
        if current_incident:
            st.warning(f"⚠️ You are about to delete: {current_incident}")

        if st.button("Delete Incident", type="primary"):
            db.execute_query("DELETE FROM cyber_incidents WHERE id = ?", (del_id,))
            st.success(f"✅ Incident {del_id} deleted!")
            st.rerun()
    else:
        st.info("No incidents available to delete")
