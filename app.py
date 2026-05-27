import streamlit as st

from modules.control_file_master import run_control_file_master
from modules.project_tracker import run_project_tracker
from modules.merge_control_tracker import run_merge_control_tracker
from modules.outputs import run_outputs
from modules.target_price_reader import run_target_price_reader
from modules.workbank import run_workbank

# ======================================================
# PAGE CONFIG
# ======================================================

st.set_page_config(
    page_title="Operations Dashboard",
    layout="wide"
)

st.title("📊 Operations Dashboard")

# ======================================================
# FILE UPLOADER
# ======================================================

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx", "xlsm", "xls", "xlsb"],
    accept_multiple_files=True
)

st.divider()

# ======================================================
# BUTTONS
# ======================================================

col1, col2, col3 = st.columns(3)

with col1:
    run_control = st.button("🚀 Control File Master")

with col2:
    run_tracker = st.button("📈 Project Tracker")

with col3:
    run_merge = st.button("🔗 Merge Control + Tracker")

col4, col5, col6 = st.columns(3)

with col4:
    run_output_btn = st.button("📦 Outputs")

with col5:
    run_target = st.button("💰 Target Price Reader")

with col6:
    run_workbank_btn = st.button("🛠 Workbank")

st.divider()

# ======================================================
# VALIDATION
# ======================================================

if (
    run_control
    or run_tracker
    or run_merge
    or run_output_btn
    or run_target
    or run_workbank_btn
):
    if not uploaded_files:
        st.warning("Please upload files first.")
        st.stop()

# ======================================================
# MODULE EXECUTION
# ======================================================

if run_control:
    run_control_file_master(uploaded_files)

if run_tracker:
    run_project_tracker(uploaded_files)

if run_merge:
    run_merge_control_tracker(uploaded_files)

if run_output_btn:
    run_outputs(uploaded_files)

if run_target:
    run_target_price_reader(uploaded_files)

if run_workbank_btn:
    run_workbank(uploaded_files)
