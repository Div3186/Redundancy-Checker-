import streamlit as st
import pandas as pd

st.title("📊 Redundancy Checker")

uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            excel_file = pd.ExcelFile(uploaded_file)
            for sheet in excel_file.sheet_names:
                df = pd.read_excel(uploaded_file, sheet_name=sheet)
                dup_rows = df[df.duplicated()]
                dup_columns = df.columns[df.apply(pd.Series.duplicated).any()].tolist()

                st.subheader(f"Sheet: {sheet}")
                st.write(f"✅ Duplicate rows: {len(dup_rows)}")
                st.write(f"✅ Duplicate fields: {dup_columns if dup_columns else 'None'}")

                if not dup_rows.empty:
                    st.write("Sample duplicate rows:")
                    st.dataframe(dup_rows.head())

        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            dup_rows = df[df.duplicated()]
            dup_columns = df.columns[df.apply(pd.Series.duplicated).any()].tolist()

            st.subheader("CSV File")
            st.write(f"✅ Duplicate rows: {len(dup_rows)}")
            st.write(f"✅ Duplicate fields: {dup_columns if dup_columns else 'None'}")

            if not dup_rows.empty:
                st.write("Sample duplicate rows:")
                st.dataframe(dup_rows.head())
        else:
            st.error("Unsupported file type. Please upload .xlsx or .csv files only.")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
