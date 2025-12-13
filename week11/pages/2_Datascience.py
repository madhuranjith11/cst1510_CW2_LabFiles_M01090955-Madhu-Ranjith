"""Data Science Dashboard - Refactored with OOP."""

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
from models.dataset import Dataset

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login first.")
    st.stop()

st.title("📊 Data Science Dashboard")

# Initialize database
@st.cache_resource
def get_db():
    return DatabaseManager(str(ROOT / "database" / "intelligence_platform.db"))

db = get_db()

# Helper functions
def fetch_all_datasets():
    """Fetch all datasets and return as Dataset objects."""
    rows = db.fetch_all(
        """SELECT id, dataset_name, category, source, last_updated,
           record_count, file_size_mb
           FROM datasets_metadata
           ORDER BY id DESC"""
    )

    datasets = []
    for row in rows:
        dataset = Dataset(
            dataset_id=row["id"],
            dataset_name=row["dataset_name"],
            category=row["category"],
            source=row["source"],
            upload_date=row["last_updated"],  # Changed from upload_date to last_updated
            record_count=row["record_count"],
            file_size_mb=row["file_size_mb"]
        )
        datasets.append(dataset)

    return datasets

def get_datasets_dataframe():
    """Get datasets as a pandas DataFrame for display."""
    datasets = fetch_all_datasets()
    if not datasets:
        return pd.DataFrame()

    data = [dataset.to_dict() for dataset in datasets]
    return pd.DataFrame(data)

# ---------------- Fetch Data ----------------
df = get_datasets_dataframe()

# ---------------- Visualizations ----------------
if not df.empty:
    st.subheader("📊 Dataset Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Datasets", len(df))

    with col2:
        total_records = df["Records"].sum()
        st.metric("Total Records", f"{total_records:,}")

    with col3:
        total_size = df["Size (MB)"].sum()
        st.metric("Total Size", f"{total_size:.2f} MB")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(
            df,
            names="Category",
            values="Records",
            title="Records by Category"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(
            df,
            x="Name",
            y="Size (MB)",
            title="Dataset Sizes",
            color="Category"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ---------------- Display Datasets Table ----------------
st.subheader("📋 All Datasets")

if df.empty:
    st.info("No datasets found. Add your first dataset below!")
else:
    st.dataframe(df, use_container_width=True)

# ---------------- CRUD Operations ----------------

# Add Dataset
with st.expander("➕ Add Dataset Metadata", expanded=False):
    name = st.text_input("Dataset Name", key="add_name", placeholder="e.g., Customer Data 2024")
    cat = st.text_input("Category", key="add_cat", placeholder="e.g., Sales, Marketing")
    src = st.text_input("Source", key="add_src", placeholder="e.g., Internal Database")
    rec = st.number_input("Record Count", min_value=0, step=1, key="add_rec")
    size = st.number_input("File Size (MB)", min_value=0.0, format="%.2f", key="add_size")

    if st.button("Add Dataset"):
        if name and cat and src:
            db.execute_query(
                """INSERT INTO datasets_metadata
                   (dataset_name, category, source, last_updated, record_count, file_size_mb)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, cat, src, str(datetime.now().date()), rec, size)
            )
            st.success("✅ Dataset Added!")
            st.rerun()
        else:
            st.warning("Please fill in all required fields (Name, Category, Source)")

# Update Dataset
with st.expander("🛠️ Update Dataset Metadata", expanded=False):
    datasets = fetch_all_datasets()

    if datasets:
        # Create selection options
        dataset_options = {f"ID {ds.get_id()}: {ds.get_name()}": ds.get_id()
                         for ds in datasets}

        selected_dataset = st.selectbox(
            "Select Dataset",
            options=list(dataset_options.keys()),
            key="update_select"
        )

        uid = dataset_options[selected_dataset]

        # Find the dataset object
        current_dataset = next((ds for ds in datasets if ds.get_id() == uid), None)

        if current_dataset:
            st.info(f"Current: {current_dataset}")

        new_name = st.text_input("New Dataset Name", key="update_name",
                                value=current_dataset.get_name() if current_dataset else "")
        new_cat = st.text_input("New Category", key="update_cat",
                               value=current_dataset.get_category() if current_dataset else "")
        new_src = st.text_input("New Source", key="update_src",
                               value=current_dataset.get_source() if current_dataset else "")
        new_rec = st.number_input("New Record Count", step=1, key="update_rec",
                                 value=current_dataset.get_record_count() if current_dataset else 0)
        new_size = st.number_input("New File Size (MB)", format="%.2f", key="update_size",
                                  value=current_dataset.get_file_size_mb() if current_dataset else 0.0)

        if st.button("Update Dataset"):
            if new_name and new_cat and new_src:
                db.execute_query(
                    """UPDATE datasets_metadata
                       SET dataset_name = ?, category = ?, source = ?,
                           record_count = ?, file_size_mb = ?
                       WHERE id = ?""",
                    (new_name, new_cat, new_src, new_rec, new_size, uid)
                )
                st.success(f"✅ Dataset {uid} updated!")
                st.rerun()
            else:
                st.warning("Please fill in all required fields")
    else:
        st.info("No datasets available to update")

# Delete Dataset
with st.expander("🗑️ Delete Dataset", expanded=False):
    datasets = fetch_all_datasets()

    if datasets:
        dataset_options = {f"ID {ds.get_id()}: {ds.get_name()} ({ds.get_category()})": ds.get_id()
                         for ds in datasets}

        selected_dataset = st.selectbox(
            "Select Dataset to Delete",
            options=list(dataset_options.keys()),
            key="del_select"
        )

        del_id = dataset_options[selected_dataset]

        # Show details
        current_dataset = next((ds for ds in datasets if ds.get_id() == del_id), None)
        if current_dataset:
            st.warning(f"⚠️ You are about to delete: {current_dataset}")

        if st.button("Delete Dataset", type="primary"):
            db.execute_query("DELETE FROM datasets_metadata WHERE id = ?", (del_id,))
            st.success(f"✅ Dataset {del_id} deleted!")
            st.rerun()
    else:
        st.info("No datasets available to delete")
