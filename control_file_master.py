import streamlit as st
import pandas as pd
import numpy as np
import os
import re
from io import BytesIO

# =========================================================
#                        FUNCTIONS
# =========================================================

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
    for c in codes:
        if c in teams:
            names.extend(teams[c])

    return ", ".join(names) if names else "UNKNOWN"


# =========================================================
#                        MAPPINGS
# =========================================================

project_mapping = {
    "Jonathon Mcclung": ["Ayrshire", "PCB"],
    "Gary MacDonald": ["Ayrshire", "LV"],
    "Jim Gaffney": ["Lanark", "PCB"],
    "Calum Thomson": ["Ayrshire", "Connections"],
    "David Jamieson": ["Lanark", "11kV"],
}

mapping_region = {
    "Newmilns": ["Irvine Valley"],
    "Kilwinning": ["Kilwinning"],
    "Ayr": ["Ayr East", "Ayr West"],
}

teams = {
    "A": ["Paulo Marques"],
    "B": ["Rui Rocha"],
    "C": ["Craig Kerr"],
}

# =========================================================
#                        STREAMLIT UI
# =========================================================

st.title("📊 Excel Aggregation System")

uploaded_files = st.file_uploader(
    "Upload Excel files",
    type=["xlsx", "xlsm", "xls", "xlsb"],
    accept_multiple_files=True
)

# =========================================================
#                        PROCESS BUTTON
# =========================================================

if st.button("🚀 Run Processing"):

    if not uploaded_files:
        st.warning("Please upload files first.")
        st.stop()

    aggregated_df = pd.DataFrame()
    resume_list_dfs = []

    progress = st.progress(0)

    for i, file in enumerate(uploaded_files):

        file_name = file.name
        st.write(f"Processing: {file_name}")

        # ===================== BLOCK 1 =====================
        try:
            df = pd.read_excel(file, sheet_name="Block1")

            df.columns = df.columns.str.strip().str.lower()

            if "plan1" in df.columns:
                df["plan1"] = df["plan1"].apply(parse_excel_date)

            if "done" in df.columns:
                df["done"] = df["done"].apply(parse_excel_date)

            if "segment" in df.columns:
                df[["type", "segmentdesc", "segmentcode", "projectmanager"]] = df["segment"].apply(
                    lambda x: parse_segment_info(x, project_mapping)
                )

            df["sourcefile"] = file_name

            aggregated_df = pd.concat([aggregated_df, df], ignore_index=True)

            st.success(f"Block1 loaded: {len(df)} rows")

        except Exception as e:
            st.error(f"Block1 error: {e}")

        # ===================== PA CONTROL =====================
        try:
            pa_df = pd.read_excel(file, sheet_name="PA CONTROL")

            pa_df.columns = ["section", "value_eur", "completion"]

            pa_df = pa_df[pa_df["section"].astype(str).str.match(r"^[MC]", na=False)]

            pa_df["value_eur"] = pd.to_numeric(pa_df["value_eur"], errors="coerce")
            pa_df["completion"] = pd.to_numeric(pa_df["completion"], errors="coerce")

            pa_df["%complete"] = (
                pa_df["completion"] / pa_df["value_eur"].replace(0, np.nan)
            ) * 100

            pa_df["sourcefile"] = file_name

            resume_list_dfs.append(pa_df)

            st.success(f"PA CONTROL loaded: {len(pa_df)} rows")

        except Exception as e:
            st.warning(f"PA CONTROL error: {e}")

        progress.progress((i + 1) / len(uploaded_files))

    # =========================================================
    #                        OUTPUT
    # =========================================================

    st.success("Processing complete!")

    st.write("### Preview Aggregated Data")
    st.dataframe(aggregated_df.head())

    # ---------------- Excel Export ----------------
    excel_buffer = BytesIO()

    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        aggregated_df.to_excel(writer, index=False, sheet_name="Aggregated")

        if resume_list_dfs:
            pd.concat(resume_list_dfs).to_excel(
                writer,
                index=False,
                sheet_name="Resume"
            )

    excel_buffer.seek(0)

    st.download_button(
        "📥 Download Excel",
        data=excel_buffer,
        file_name="aggregated_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------------- Parquet Export ----------------
    parquet_buffer = BytesIO()
    aggregated_df.to_parquet(parquet_buffer, index=False)
    parquet_buffer.seek(0)

    st.download_button(
        "📥 Download Parquet",
        data=parquet_buffer,
        file_name="aggregated.parquet",
        mime="application/octet-stream"
    )

else:
    st.info("Upload files and click Run Processing")
