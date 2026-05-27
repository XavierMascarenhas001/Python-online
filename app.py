import streamlit as st
from io import BytesIO
import pandas as pd

# Import your modules (you must refactor them into functions)
from Control_file_master import run_control_file_master
from Project_Tracker import run_project_tracker
from Merge_Control_File_Tracker import run_merge_tracker
from Outputs import run_outputs
from Target_Price_reader import run_target_price_reader
from Workbank import run_workbank


st.set_page_config(page_title="Multi Tool System", layout="wide")

st.title("📊 Project Processing Suite")

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx", "xlsm", "xls", "xlsb"],
    accept_multiple_files=True
)

if uploaded_files:

    st.success(f"{len(uploaded_files)} files uploaded")

    # ---------------- BUTTONS ----------------
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    # ---- CONTROL FILE MASTER ----
    with col1:
        if st.button("Run Control File Master"):
            excel, parquet = run_control_file_master(uploaded_files)

            st.download_button(
                "Download Control Excel",
                excel,
                file_name="control_output.xlsx"
            )

            st.download_button(
                "Download Control Parquet",
                parquet,
                file_name="control_output.parquet"
            )

    # ---- PROJECT TRACKER ----
    with col2:
        if st.button("Run Project Tracker"):
            excel = run_project_tracker(uploaded_files)

            st.download_button(
                "Download Project Tracker",
                excel,
                file_name="project_tracker.xlsx"
            )

    # ---- MERGE TRACKER ----
    with col3:
        if st.button("Run Merge Tracker"):
            excel = run_merge_tracker(uploaded_files)

            st.download_button(
                "Download Merge Output",
                excel,
                file_name="merge_output.xlsx"
            )

    # ---- OUTPUTS ----
    with col4:
        if st.button("Run Outputs"):
            excel = run_outputs(uploaded_files)

            st.download_button(
                "Download Outputs",
                excel,
                file_name="outputs.xlsx"
            )

    # ---- TARGET PRICE ----
    with col5:
        if st.button("Run Target Price Reader"):
            excel = run_target_price_reader(uploaded_files)

            st.download_button(
                "Download Target Price",
                excel,
                file_name="target_price.xlsx"
            )

    # ---- WORKBANK ----
    with col6:
        if st.button("Run Workbank"):
            excel = run_workbank(uploaded_files)

            st.download_button(
                "Download Workbank",
                excel,
                file_name="workbank.xlsx"
            )

else:
    st.info("Upload files to begin")
