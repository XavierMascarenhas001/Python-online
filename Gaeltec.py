import streamlit as st
from io import BytesIO

st.set_page_config(page_title="Excel Aggregator", layout="wide")

st.title("Excel Aggregator")

uploaded_files = st.file_uploader(
    "Upload Excel files",
    type=["xlsx", "xlsm", "xls", "xlsb"],
    accept_multiple_files=True
)

if uploaded_files:

    aggregated_df = pd.DataFrame()
    resume_list_dfs = []

    progress_bar = st.progress(0)

    for idx, uploaded_file in enumerate(uploaded_files):

        file_name = uploaded_file.name
        ext = os.path.splitext(file_name)[1].lower()

        st.write(f"📘 Reading file: {file_name}")

        # --- Detect project + shire from filename ---
        project, shire = extract_project_shire(file_name)

        st.write(f"Project: {project} | Shire: {shire}")

        # =========================
        # BLOCK1
        # =========================
        try:

            read_kwargs = dict(
                sheet_name="Block1",
                header=2,
                skiprows=range(3, 29),
                usecols="A,B,C,D,E,F,U,V,AL,AM,AO,CG,CH"
            )

            if ext == ".xlsb":
                read_kwargs["engine"] = "pyxlsb"

            df = pd.read_excel(uploaded_file, **read_kwargs)

            df.columns = df.columns.str.strip().str.lower()
            df.columns = df.columns.str.strip()

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

            date_cols = [c for c in df.columns if c.startswith('date')]

            for col in date_cols:
                df[col] = df[col].apply(parse_excel_date)

            # Parse segment info
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

            # Add project info
            df['project'] = project
            df['shire'] = shire

            if 'segmentdesc' in df.columns:
                df['location'] = df['segmentdesc'].apply(extract_location)

                df['region'] = df['location'].where(
                    df['location'].notna() &
                    (df['location'] != ""),
                    df['shire']
                )

            df['sourcefile'] = file_name

            # Team mapping
            if 'team' in df.columns:

                df['team'] = (
                    df['team']
                    .astype(str)
                    .str.strip()
                    .str.upper()
                )

                df['team_name'] = df['team'].apply(map_teams)

            # Item mapping
            if 'item' in df.columns:

                df['mapped'] = (
                    df['item']
                    .map(mapping_dict)
                    .fillna(df['item'])
                )

                for col in ['qty', 'qsub']:

                    if col in df.columns:

                        df.loc[
                            df['item'].astype(str).str.contains(
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

        # =========================
        # PA CONTROL
        # =========================
        try:

            pa_kwargs = dict(
                sheet_name="PA CONTROL",
                header=0,
                skiprows=1,
                usecols=[0, 2, 4]
            )

            if ext == ".xlsb":
                pa_kwargs["engine"] = "pyxlsb"

            uploaded_file.seek(0)

            pa_df = pd.read_excel(uploaded_file, **pa_kwargs)

            pa_df.columns = [
                "section",
                "value_eur",
                "completion"
            ]

            pa_df = pa_df[
                pa_df['section']
                .astype(str)
                .str.match(r'^[MC]', na=False)
            ]

            pa_df['value_eur'] = pd.to_numeric(
                pa_df['value_eur'],
                errors='coerce'
            )

            pa_df['completion'] = pd.to_numeric(
                pa_df['completion'],
                errors='coerce'
            )

            pa_df['%complete'] = (
                pa_df['completion'] /
                pa_df['value_eur'].replace(0, np.nan)
            ) * 100

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

            pa_df['project'] = project
            pa_df['shire'] = shire

            pa_df['location'] = pa_df[
                'segmentdesc'
            ].apply(extract_location)

            pa_df['region'] = pa_df['location'].where(
                pa_df['location'].notna() &
                (pa_df['location'] != ""),
                pa_df['shire']
            )

            pa_df['sourcefile'] = file_name

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

    # =========================
    # OUTPUTS
    # =========================
    if not aggregated_df.empty:

        if 'datetouse' in aggregated_df.columns:

            aggregated_df = aggregated_df.sort_values(
                by='datetouse'
            ).reset_index(drop=True)

        # =========================
        # EXCEL DOWNLOAD
        # =========================
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
            label="📥 Download Excel Report",
            data=excel_buffer,
            file_name="aggregated_output.xlsx",
            mime=(
                "application/vnd.openxmlformats-"
                "officedocument.spreadsheetml.sheet"
            )
        )

        # =========================
        # PARQUET DOWNLOAD
        # =========================
        parquet_buffer = BytesIO()

        agg_df_copy = aggregated_df.copy()

        for col in agg_df_copy.select_dtypes(
            include=['object']
        ).columns:

            agg_df_copy[col] = (
                agg_df_copy[col]
                .astype(str)
            )

        agg_df_copy.to_parquet(
            parquet_buffer,
            index=False
        )

        parquet_buffer.seek(0)

        st.download_button(
            label="📥 Download Parquet",
            data=parquet_buffer,
            file_name="aggregated_output.parquet",
            mime="application/octet-stream"
        )

        st.success("✅ Processing complete")

        st.dataframe(
            aggregated_df.head(100),
            use_container_width=True
        )

else:

    st.info("Upload Excel files to begin.")
