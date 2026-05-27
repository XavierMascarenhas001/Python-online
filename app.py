import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# =========================================================
# PAGE SETUP
# =========================================================
st.set_page_config(page_title="Operations Dashboard", layout="wide")
st.title("⚙️ Operations Dashboard")

# =========================================================
# SESSION STATE INIT
# =========================================================
if "output_file" not in st.session_state:
    st.session_state.output_file = None


# =========================================================
# TOOL 1 — CONTROL FILE MASTER
# =========================================================
def control_file_master(uploaded_files):

    aggregated_df = pd.DataFrame()

    for file in uploaded_files:
        df = pd.read_excel(file)
        df["sourcefile"] = file.name
        aggregated_df = pd.concat([aggregated_df, df], ignore_index=True)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        aggregated_df.to_excel(writer, index=False, sheet_name="Aggregated")

    output.seek(0)

    return output


# =========================================================
# TOOL 2 — PROJECT TRACKER (placeholder logic)
# =========================================================
def project_tracker(uploaded_files):

    df_all = pd.DataFrame()

    for file in uploaded_files:
        df = pd.read_excel(file)
        df["sourcefile"] = file.name
        df_all = pd.concat([df_all, df], ignore_index=True)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False)

    output.seek(0)

    return output


# =========================================================
# TOOL 3 — MERGE CONTROL FILE TRACKER
# =========================================================
def merge_control_files(uploaded_files):

    df_all = pd.concat(
        [pd.read_excel(f) for f in uploaded_files],
        ignore_index=True
    )

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False)

    output.seek(0)

    return output


# =========================================================
# TOOL 4 — OUTPUTS
# =========================================================
def outputs_tool(uploaded_files):

    df_all = pd.DataFrame()

    for f in uploaded_files:
        df = pd.read_excel(f)
        df_all = pd.concat([df_all, df], ignore_index=True)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False)

    output.seek(0)

    return output


# =========================================================
# TOOL 5 — TARGET PRICE READER
# =========================================================
def target_price_reader(uploaded_files):

    df_all = pd.DataFrame()

    for f in uploaded_files:
        df = pd.read_excel(f)
        df_all = pd.concat([df_all, df], ignore_index=True)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False)

    output.seek(0)

    return output


# =========================================================
# TOOL 6 — WORKBANK
# =========================================================
def workbank(uploaded_files):

    df_all = pd.DataFrame()

    for f in uploaded_files:
        df = pd.read_excel(f)
        df_all = pd.concat([df_all, df], ignore_index=True)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_all.to_excel(writer, index=False)

    output.seek(0)

    return output


# =========================================================
# UI MENU (BUTTONS)
# =========================================================

st.subheader("Select Tool")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Control File Master"):
        st.session_state.tool = "control"

with col2:
    if st.button("📁 Project Tracker"):
        st.session_state.tool = "tracker"

with col3:
    if st.button("🔀 Merge Control Tracker"):
        st.session_state.tool = "merge"


col4, col5, col6 = st.columns(3)

with col4:
    if st.button("📤 Outputs"):
        st.session_state.tool = "outputs"

with col5:
    if st.button("💰 Target Price Reader"):
        st.session_state.tool = "target"

with col6:
    if st.button("🏗️ Workbank"):
        st.session_state.tool = "workbank"


st.divider()


# =========================================================
# ROUTER (RUN SELECTED TOOL)
# =========================================================

tool = st.session_state.get("tool", None)

if not tool:
    st.info("Click a tool above to begin")

# =========================================================
# CONTROL FILE MASTER
# =========================================================
elif tool == "control":

    st.header("📊 Control File Master")

    uploaded_files = st.file_uploader(
        "Upload Excel files",
        type=["xlsx", "xlsm", "xls", "xlsb"],
        accept_multiple_files=True,
        key="control_upload"
    )

    if uploaded_files and st.button("Run Control File Master"):

        result = control_file_master(uploaded_files)

        st.download_button(
            "📥 Download Output",
            result,
            file_name="control_file_master.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# PROJECT TRACKER
# =========================================================
elif tool == "tracker":

    st.header("📁 Project Tracker")

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key="tracker_upload"
    )

    if uploaded_files and st.button("Run Project Tracker"):

        result = project_tracker(uploaded_files)

        st.download_button(
            "📥 Download Output",
            result,
            file_name="project_tracker.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# MERGE CONTROL
# =========================================================
elif tool == "merge":

    st.header("🔀 Merge Control File Tracker")

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key="merge_upload"
    )

    if uploaded_files and st.button("Run Merge"):

        result = merge_control_files(uploaded_files)

        st.download_button(
            "📥 Download Output",
            result,
            file_name="merge_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# OUTPUTS
# =========================================================
elif tool == "outputs":

    st.header("📤 Outputs")

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key="outputs_upload"
    )

    if uploaded_files and st.button("Generate Outputs"):

        result = outputs_tool(uploaded_files)

        st.download_button(
            "📥 Download Output",
            result,
            file_name="outputs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# TARGET PRICE
# =========================================================
elif tool == "target":

    st.header("💰 Target Price Reader")

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key="target_upload"
    )

    if uploaded_files and st.button("Run Target Price Reader"):

        result = target_price_reader(uploaded_files)

        st.download_button(
            "📥 Download Output",
            result,
            file_name="target_price.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# =========================================================
# WORKBANK
# =========================================================
elif tool == "workbank":

    st.header("🏗️ Workbank")

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key="workbank_upload"
    )

    if uploaded_files and st.button("Run Workbank"):

        result = workbank(uploaded_files)

        st.download_button(
            "📥 Download Output",
            result,
            file_name="workbank.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
