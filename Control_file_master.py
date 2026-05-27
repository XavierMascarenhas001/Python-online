import streamlit as st
import pandas as pd
import numpy as np
import os
import re
from io import BytesIO

# ---------------- Utility Functions ----------------
def parse_excel_date(x):
    try:
        if pd.isna(x):
            return np.nan

        if isinstance(x, (int, float)):
            return pd.to_datetime(x, origin="1899-12-30", unit="D", errors="coerce")

        return pd.to_datetime(str(x), errors="coerce")
    except:
        return np.nan


def parse_segment_info(segment_str, project_mapping, default_pm=""):
    if not isinstance(segment_str, str) or not segment_str.strip():
        return pd.Series([None, None, None, default_pm])

    segment_str = segment_str.strip()

    type_match = re.match(r"^\s*([MC])\s*-\s*", segment_str)
    segment_type = type_match.group(1) if type_match else None

    code_match = re.search(r"\b([A-Z]{0,3}\d{5})\b", segment_str)
    segment_code = code_match.group(1) if code_match else None

    segment_desc = re.sub(r"^\s*[MC]\s*-\s*", "", segment_str)
    if segment_code:
        segment_desc = re.sub(re.escape(segment_code), "", segment_desc)

    project_manager = ""
    text_lower = segment_str.lower()

    for pm in project_mapping:
        if pm.lower() in text_lower:
            project_manager = pm
            break

    return pd.Series([segment_type, segment_desc.strip(), segment_code, project_manager])


def extract_location(segment_desc, mapping_region):
    if not isinstance(segment_desc, str):
        return ""

    for key, loc in mapping_region.items():
        if key.lower() in segment_desc.lower():
            return ", ".join(loc)
    return ""


def map_teams(codes, teams):
    if pd.isna(codes):
        return "UNKNOWN"

    codes = str(codes).upper().strip()

    names = []
    for char in codes:
        if char in teams:
            names.extend(teams[char])

    return ", ".join(names) if names else "UNKNOWN"


# ---------------- Streamlit UI ----------------
st.title("📊 Excel Aggregator App")

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx", "xlsm", "xls", "xlsb"],
    accept_multiple_files=True
)

# ---------------- SESSION STORAGE ----------------
if "aggregated_df" not in st.session_state:
    st.session_state.aggregated_df = pd.DataFrame()

if "resume_list_dfs" not in st.session_state:
    st.session_state.resume_list_dfs = []

# ---------------- PROCESS BUTTON ----------------
if st.button("🚀 Run Processing"):

    aggregated_df = pd.DataFrame()
    resume_list_dfs = []

    if not uploaded_files:
        st.warning("Upload files first")
        st.stop()

    progress = st.progress(0)

    for idx, file in enumerate(uploaded_files):
        file_name = file.name
        ext = os.path.splitext(file_name)[1].lower()

        st.write(f"Processing: {file_name}")

        # -------- BLOCK1 --------
        try:
            df = pd.read_excel(file, sheet_name="Block1")

            df.columns = df.columns.str.strip().str.lower()

            if "plan1" in df.columns:
                df["plan1"] = df["plan1"].apply(parse_excel_date)

            if "done" in df.columns:
                df["done"] = df["done"].apply(parse_excel_date)

            if "segment" in df.columns:
                df[["type", "segmentdesc", "segmentcode", "projectmanager"]] = df["segment"].apply(
                    lambda x: parse_segment_info(x, {})
                )

            df["sourcefile"] = file_name

            aggregated_df = pd.concat([aggregated_df, df], ignore_index=True)

            st.success(f"Block1 loaded: {len(df)} rows")

        except Exception as e:
            st.error(f"Block1 error: {e}")

        # -------- PA CONTROL --------
        try:
            pa_df = pd.read_excel(file, sheet_name="PA CONTROL")
            pa_df.columns = ["section", "value_eur", "completion"]

            pa_df = pa_df[pa_df["section"].astype(str).str.match(r"^[MC]", na=False)]

            pa_df["value_eur"] = pd.to_numeric(pa_df["value_eur"], errors="coerce")
            pa_df["completion"] = pd.to_numeric(pa_df["completion"], errors="coerce")

            pa_df["%complete"] = (pa_df["completion"] / pa_df["value_eur"].replace(0, np.nan)) * 100

            pa_df["sourcefile"] = file_name

            resume_list_dfs.append(pa_df)

            st.success(f"PA CONTROL loaded: {len(pa_df)} rows")

        except Exception as e:
            st.warning(f"PA CONTROL error: {e}")

        progress.progress((idx + 1) / len(uploaded_files))

    st.session_state.aggregated_df = aggregated_df
    st.session_state.resume_list_dfs = resume_list_dfs


# ---------------- OUTPUT SECTION ----------------
if not st.session_state.aggregated_df.empty:

    df = st.session_state.aggregated_df
    resume_list_dfs = st.session_state.resume_list_dfs

    st.write("### Preview")
    st.dataframe(df.head())

    # -------- EXCEL DOWNLOAD --------
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Aggregated")

        if resume_list_dfs:
            pd.concat(resume_list_dfs).to_excel(writer, index=False, sheet_name="Resume")

    output.seek(0)

    st.download_button(
        "📥 Download Excel",
        data=output,
        file_name="output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # -------- PARQUET --------
    parquet_buffer = BytesIO()
    df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    st.download_button(
        "📥 Download Parquet",
        data=parquet_buffer,
        file_name="output.parquet",
        mime="application/octet-stream"
    )

else:
    st.info("Upload files and click Run Processing")
