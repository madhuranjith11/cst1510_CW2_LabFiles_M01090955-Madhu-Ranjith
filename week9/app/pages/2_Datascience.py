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

from app.db.datasets import (
    get_all_datasets, insert_dataset, update_dataset, delete_dataset
)

# Check login
if not st.session_state.get("logged_in"):
    st.error("⛔ Please login first.")
    st.stop()

st.title("📊 Data Science Dashboard")

# ---------------- Fetch Data ----------------
df = get_all_datasets()

# ---------------- Visualizations ----------------
if not df.empty:
    st.subheader("📊 Dataset Statistics")
    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.pie(df, names="category", values="record_count", title="Records by Category")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.bar(df, x="dataset_name", y="file_size_mb", title="Dataset Sizes")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------- Display Datasets Table ----------------
st.subheader("📋 All Datasets")
st.dataframe(df, use_container_width=True)

# ---------------- CRUD Operations ----------------

# Add Dataset
with st.expander("➕ Add Dataset Metadata", expanded=False):
    name = st.text_input("Dataset Name", key="add_name")
    cat = st.text_input("Category", key="add_cat")
    src = st.text_input("Source", key="add_src")
    rec = st.number_input("Record Count", step=1, key="add_rec")
    size = st.number_input("File Size (MB)", format="%.2f", key="add_size")

    if st.button("Add Dataset"):
        insert_dataset(name, cat, src, str(datetime.now().date()), rec, size)
        st.success("Dataset Added!")
        st.experimental_rerun()

# Update Dataset
with st.expander("🛠 Update Dataset Metadata", expanded=False):
    uid = st.number_input("Dataset ID to Update", min_value=1, step=1, key="update_ds_id")
    new_name = st.text_input("New Dataset Name", key="update_name")
    new_cat = st.text_input("New Category", key="update_cat")
    new_src = st.text_input("New Source", key="update_src")
    new_rec = st.number_input("New Record Count", step=1, key="update_rec")
    new_size = st.number_input("New File Size (MB)", format="%.2f", key="update_size")

    if st.button("Update Dataset"):
        rows = update_dataset(uid, new_name, new_cat, new_src, new_rec, new_size)
        if rows:
            st.success(f"Dataset {uid} updated successfully!")
        else:
            st.warning(f"No dataset found with ID {uid}")
        st.experimental_rerun()

# Delete Dataset
with st.expander("🗑 Delete Dataset", expanded=False):
    del_id = st.number_input("Dataset ID to Delete", min_value=1, step=1, key="del_ds_id")
    if st.button("Delete Dataset"):
        rows = delete_dataset(del_id)
        if rows:
            st.success(f"Dataset {del_id} deleted successfully!")
        else:
            st.warning(f"No dataset found with ID {del_id}")
        st.experimental_rerun()
