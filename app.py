import streamlit as st

# =========================================================
# PAGE SETUP
# =========================================================
st.set_page_config(
    page_title="Operations Dashboard",
    layout="wide"
)

st.title("⚙️ Operations Dashboard")

st.write("Select a tool below")

# =========================================================
# TOOL FUNCTIONS
# =========================================================

def run_control_file_master():

    st.header("📊 Control File Master")

    st.write("Run Control File Master logic here")

    uploaded_files = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        key="cfm"
    )

    if uploaded_files:

        if st.button("Run Control File Master"):

            st.success("✅ Control File Master completed")


def run_project_tracker():

    st.header("📁 Project Tracker")

    uploaded_files = st.file_uploader(
        "Upload tracker files",
        accept_multiple_files=True,
        key="pt"
    )

    if uploaded_files:

        if st.button("Run Project Tracker"):

            st.success("✅ Project Tracker completed")


def run_merge_control_tracker():

    st.header("🔀 Merge Control File Tracker")

    uploaded_files = st.file_uploader(
        "Upload merge files",
        accept_multiple_files=True,
        key="merge"
    )

    if uploaded_files:

        if st.button("Run Merge"):

            st.success("✅ Merge completed")


def run_outputs():

    st.header("📤 Outputs")

    uploaded_files = st.file_uploader(
        "Upload output files",
        accept_multiple_files=True,
        key="outputs"
    )

    if uploaded_files:

        if st.button("Generate Outputs"):

            st.success("✅ Outputs generated")


def run_target_price_reader():

    st.header("💰 Target Price Reader")

    uploaded_files = st.file_uploader(
        "Upload pricing files",
        accept_multiple_files=True,
        key="tp"
    )

    if uploaded_files:

        if st.button("Read Target Prices"):

            st.success("✅ Target prices processed")


def run_workbank():

    st.header("🏗️ Workbank")

    uploaded_files = st.file_uploader(
        "Upload workbank files",
        accept_multiple_files=True,
        key="workbank"
    )

    if uploaded_files:

        if st.button("Run Workbank"):

            st.success("✅ Workbank completed")


# =========================================================
# MAIN BUTTON GRID
# =========================================================

st.divider()

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


# =========================================================
# ROUTER
# =========================================================

if "tool" not in st.session_state:

    st.info("Select a tool to begin")

elif st.session_state.tool == "control":

    run_control_file_master()

elif st.session_state.tool == "tracker":

    run_project_tracker()

elif st.session_state.tool == "merge":

    run_merge_control_tracker()

elif st.session_state.tool == "outputs":

    run_outputs()

elif st.session_state.tool == "target":

    run_target_price_reader()

elif st.session_state.tool == "workbank":

    run_workbank()
