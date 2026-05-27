import streamlit as st
import pandas as pd
import os
import re
import numpy as np
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Excel Aggregator",
    layout="wide"
)

st.title("📊 Excel Aggregator Tool")

# ---------------- Utility Functions ----------------
def parse_excel_date(x):
    try:
        if pd.isna(x):
            return np.nan

        if isinstance(x, (int, float)):
            return pd.to_datetime(
                x,
                origin="1899-12-30",
                unit="D",
                errors="coerce"
            )

        return pd.to_datetime(str(x), errors="coerce")

    except Exception:
        return np.nan


def parse_segment_info(segment_str, project_mapping, default_pm=""):

    if not isinstance(segment_str, str) or not segment_str.strip():
        return pd.Series([None, None, None, default_pm])

    segment_str = segment_str.strip()

    # Extract type
    type_match = re.match(r"^\s*([MC])\s*-\s*", segment_str)
    segment_type = type_match.group(1) if type_match else None

    # Extract code
    code_match = re.search(r"\b([A-Z]{0,3}\d{5})\b", segment_str)
    segment_code = code_match.group(1) if code_match else None

    # Description cleanup
    segment_desc = re.sub(r"^\s*[MC]\s*-\s*", "", segment_str)

    if segment_code:
        segment_desc = re.sub(
            re.escape(segment_code),
            "",
            segment_desc
        )

    segment_desc = re.sub(
        r"\s+",
        " ",
        segment_desc
    ).strip(" -")

    # Detect PM
    project_manager = ""

    for pm, (pm_shire, pm_project) in project_mapping.items():

        if pm.lower() in segment_str.lower():

            project_manager = pm

            segment_desc = re.sub(
                re.escape(pm),
                "",
                segment_desc,
                flags=re.IGNORECASE
            )

            break

    if not project_manager and default_pm:
        project_manager = default_pm

    segment_desc = re.sub(
        r"\s+",
        " ",
        segment_desc
    ).strip(" -")

    return pd.Series([
        segment_type,
        segment_desc,
        segment_code,
        project_manager
    ])


def extract_project_shire(filename):

    filename_lower = filename.lower()

    for key, value in file_project_mapping.items():

        if key.lower() in filename_lower:

            shire, project = value
            return project, shire

    return "", ""


def extract_location(segment_desc):

    if not isinstance(segment_desc, str):
        return ""

    segment_desc_lower = segment_desc.lower()

    for key, locations in mapping_region.items():

        if key.lower() in segment_desc_lower:
            return ", ".join(locations)

    return ""


def map_teams(codes):

    if pd.isna(codes):
        return "UNKNOWN"

    codes = str(codes).upper().strip()

    if codes == "" or codes == "NAN":
        return "UNKNOWN"

    names = []

    for char in codes:

        if char in teams:
            names.extend(teams[char])

    return ", ".join(names) if names else "UNKNOWN"


# ---------------- MAPPINGS ----------------

project_mapping = {
    "Lee Fraser": ["Ayrshire", "Connections"],
    "Gary MacDonald": ["Ayrshire", "LV"],
    "Jim Gaffney": ["Lanark", "PCB"]
}

mapping_region = {
    "Newmilns": ["Irvine Valley"],
    "Kilwinning": ["Kilwinning"],
    "Ayr": ["Ayr East", "Ayr North", "Ayr West"]
}

teams = {
    "A": ["Paulo Marques"],
    "B": ["Rui Rocha"],
    "C": ["Craig Kerr"],
    "D": ["Robert Urie"],
    "E": ["Alistair Mcpherson"],
    "F": ["Kenny Campbell"],
    "S": ["Sub contracted"]
}

file_project_mapping = {
    "Connections 2025": ["Ayrshire", "Connections"],
    "PCB 2025 Ayrshire": ["Ayrshire", "PCB"],
    "Lanark 2025_Connections": ["Lanark", "Connections"]
}

mapping_dict = {
    "9x220 BIOCIDE LV POLE": "9m B",
    "9x275 BIOCIDE LV POLE": "9s B"
}

# ---------------- FILE UPLOAD ----------------

uploaded_files = st.file_uploader(
    "Upload Excel files",
    type=["xlsx", "xlsm", "xls", "xlsb"],
    accept_multiple_files=True
)

# ---------------- PROCESS FILES ----------------

if uploaded_files:

    aggregated_df = pd.DataFrame()
    resume_list_dfs = []

    progress_bar = st.progress(0)

    for idx, uploaded_file in enumerate(uploaded_files):

        file_name = uploaded_file.name
        ext = os.path.splitext(file_name)[1].lower()

        st.write(f"📘 Reading file: {file_name}")

        # Detect project + shire
        project, shire = extract_project_shire(file_name)

        st.write(f"➡️ Project: {project} | Shire: {shire}")

        # ---------------- BLOCK1 ----------------
        try:

            read_kwargs = dict(
                sheet_name="Block1",
                header=2,
                skiprows=range(3, 29),
                usecols="A,B,C,D,E,F,U,V,AL,AM,AO,CG,CH"
            )

            if ext == ".xlsb":
                read_kwargs["engine"] = "pyxlsb"

            df = pd.read_excel(
                uploaded_file,
                **read_kwargs
            )

            df.columns = df.columns.str.strip().str.lower()

            # Drop invalid rows
            col_a_name = df.columns[0]

            df = df[
                ~df[col_a_name]
                .astype(str)
                .str.lower()
                .isin(['stop'])
            ]

            df = df[df[col_a_name].notna()]

            # Parse dates
            if 'plan1' in df.columns:
                df['plan1'] = df['plan1'].apply(parse_excel_date)

            if 'done' in df.columns:
                df['done'] = df['done'].apply(parse_excel_date)

            if 'done' in df.columns and 'plan1' in df.columns:
                df['datetouse'] = df['done'].combine_first(df['plan1'])

            # Other date columns
            date_cols = [
                c for c in df.columns
                if c.startswith('date')
            ]

            for col in date_cols:
                df[col] = df[col].apply(parse_excel_date)

            # Segment parsing
            if 'segment' in df.columns:

                df[
                    [
                        'type',
                        'segmentdesc',
                        'segmentcode',
                        'projectmanager'
                    ]
                ] = df['segment'].apply(
                    lambda x: parse_segment_info(
                        x,
                        project_mapping
                    )
                )

            # Add metadata
            df['project'] = project
            df['shire'] = shire

            df['location'] = df['segmentdesc'].apply(
                extract_location
            )

            df['region'] = df['location'].where(
                df['location'].notna() &
                (df['location'] != ""),
                df['shire']
            )

            df['sourcefile'] = file_name

            # Teams
            if 'team' in df.columns:

                df['team'] = (
                    df['team']
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

                df['team_name'] = df['team'].apply(map_teams)

            # Mapping
            if 'item' in df.columns:

                df['mapped'] = (
                    df['item']
                    .map(mapping_dict)
                    .fillna(df['item'])
                )

                for col in ['qty', 'qsub']:

                    if col in df.columns:

                        df.loc[
                            df['item'].str.contains(
                                'H POLE',
                                na=False
                            ),
                            col
                        ] *= 2

            aggregated_df = pd.concat(
                [aggregated_df, df],
                ignore_index=True
            )

            st.success(f"✅ Block1 loaded — {len(df)} rows")

        except Exception as e:

            st.error(f"❌ Error reading Block1: {e}")

        # ---------------- PA CONTROL ----------------
        try:

            pa_kwargs = dict(
                sheet_name="PA CONTROL",
                header=0,
                skiprows=1,
                usecols=[0, 2, 4]
            )

            if ext == ".xlsb":
                pa_kwargs["engine"] = "pyxlsb"

            pa_df = pd.read_excel(
                uploaded_file,
                **pa_kwargs
            )

            pa_df.columns = [
                "section",
                "value_eur",
                "completion"
            ]

            # Keep only MC sections
            pa_df = pa_df[
                pa_df['section']
                .astype(str)
                .str.match(r'^[MC]', na=False)
            ]

            # Numeric conversion
            pa_df['value_eur'] = pd.to_numeric(
                pa_df['value_eur'],
                errors='coerce'
            )

            pa_df['completion'] = pd.to_numeric(
                pa_df['completion'],
                errors='coerce'
            )

            pa_df['%complete'] = (
                pa_df['completion']
                /
                pa_df['value_eur'].replace(0, np.nan)
            ) * 100

            # Parse segment info
            pa_df[
                [
                    'type',
                    'segmentdesc',
                    'segmentcode',
                    'projectmanager'
                ]
            ] = pa_df['section'].apply(
                lambda x: parse_segment_info(
                    x,
                    project_mapping
                )
            )

            # Metadata
            pa_df['project'] = project
            pa_df['shire'] = shire

            pa_df['location'] = pa_df['segmentdesc'].apply(
                extract_location
            )

            pa_df['region'] = pa_df['location'].where(
                pa_df['location'].notna() &
                (pa_df['location'] != ""),
                pa_df['shire']
            )

            pa_df['sourcefile'] = file_name

            # Append
            resume_list_dfs.append(pa_df)

            st.success(
                f"✅ PA CONTROL loaded — {len(pa_df)} rows"
            )

        except Exception as e:

            st.warning(
                f"⚠️ Could not read PA CONTROL: {e}"
            )

        progress_bar.progress(
            (idx + 1) / len(uploaded_files)
        )

    # ---------------- OUTPUT ----------------
    if not aggregated_df.empty:

        if 'datetouse' in aggregated_df.columns:

            aggregated_df = aggregated_df.sort_values(
                by='datetouse'
            ).reset_index(drop=True)

        # ---------------- Excel Output ----------------
        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="xlsxwriter"
        ) as writer:

            aggregated_df.to_excel(
                writer,
                index=False,
                sheet_name="Aggregated"
            )

            if resume_list_dfs:

                resume_df = pd.concat(
                    resume_list_dfs,
                    ignore_index=True
                )

                resume_df.to_excel(
                    writer,
                    index=False,
                    sheet_name="Resume"
                )

        excel_buffer.seek(0)

        st.download_button(
            label="📥 Download Aggregated Excel",
            data=excel_buffer,
            file_name="aggregated_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # ---------------- Parquet Output ----------------
        parquet_buffer = BytesIO()

        agg_df_copy = aggregated_df.copy()

        for col in agg_df_copy.select_dtypes(
            include=['object']
        ).columns:

            agg_df_copy[col] = agg_df_copy[col].astype(str)

        agg_df_copy.to_parquet(
            parquet_buffer,
            index=False
        )

        parquet_buffer.seek(0)

        st.download_button(
            label="📥 Download Aggregated Parquet",
            data=parquet_buffer,
            file_name="aggregated.parquet",
            mime="application/octet-stream"
        )

        st.success("✅ Processing complete")

    else:
        st.warning("⚠️ No valid data found")

else:
    st.info("Upload Excel files to begin")
