import streamlit as st
import pandas as pd
import io

st.title("📊 Redundancy Checker")

uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        output = {}
        if uploaded_file.name.endswith('.xlsx'):
            excel_file = pd.ExcelFile(uploaded_file)
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(uploaded_file, sheet_name=sheet)
                dup_rows = df[df.duplicated()]
                dup_columns = [col for col in df.columns if df[col].duplicated().any()]

                # Save for Excel report
                output[f"{sheet}_duplicate_rows"] = dup_rows if not dup_rows.empty else pd.DataFrame(["No duplicate rows"])
                output[f"{sheet}_duplicate_columns"] = pd.DataFrame({'Duplicate Columns': dup_columns}) if dup_columns else pd.DataFrame(["No duplicate columns"])

                st.subheader(f"Sheet: {sheet}")
                st.write(f"✅ Duplicate rows: {len(dup_rows)}")
                st.write(f"✅ Duplicate fields: {dup_columns if dup_columns else 'None'}")

                # Search/filter box for duplicate rows
                if not dup_rows.empty:
                    search = st.text_input(f"Search in {sheet}", key=sheet)
                    if search:
                        filtered = dup_rows[dup_rows.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
                        st.dataframe(filtered)
                    else:
                        st.dataframe(dup_rows)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            dup_rows = df[df.duplicated()]
            dup_columns = [col for col in df.columns if df[col].duplicated().any()]

            output["CSV_duplicate_rows"] = dup_rows if not dup_rows.empty else pd.DataFrame(["No duplicate rows"])
            output["CSV_duplicate_columns"] = pd.DataFrame({'Duplicate Columns': dup_columns}) if dup_columns else pd.DataFrame(["No duplicate columns"])

            st.subheader("CSV File")
            st.write(f"✅ Duplicate rows: {len(dup_rows)}")
            st.write(f"✅ Duplicate fields: {dup_columns if dup_columns else 'None'}")

            if not dup_rows.empty:
                search = st.text_input("Search in CSV")
                if search:
                    filtered = dup_rows[dup_rows.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]
                    st.dataframe(filtered)
                else:
                    st.dataframe(dup_rows)

        # Downloadable Excel report
        if output:
            excel_bytes = io.BytesIO()
            with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
                for sheet_name, df_out in output.items():
                    df_out.to_excel(writer, sheet_name=sheet_name, index=False)
            excel_bytes.seek(0)
            st.download_button(
                label="📥 Download Excel Report",
                data=excel_bytes,
                file_name="redundancy_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
