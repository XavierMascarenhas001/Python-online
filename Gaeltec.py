import streamlit as st
            resume_list_dfs.append(pa_df)

            st.success(f"✅ PA CONTROL loaded — {len(pa_df)} rows")

        except Exception as e:
            st.warning(f"⚠️ Could not read PA CONTROL: {e}")

        progress_bar.progress((idx + 1) / len(uploaded_files))


    # ---------------- OUTPUT ----------------
    if not aggregated_df.empty:

        if 'datetouse' in aggregated_df.columns:
            aggregated_df = aggregated_df.sort_values(
                by='datetouse'
            ).reset_index(drop=True)

        # ---------------- Excel Output ----------------
        excel_buffer = BytesIO()

        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:

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

        for col in agg_df_copy.select_dtypes(include=['object']).columns:
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
