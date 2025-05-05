import streamlit as st
import pandas as pd
import numpy as np
import io
import re

st.title("📊 Redundancy Theme Matrix Checker")

uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        df = None
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, sheet_name=None)  # all sheets
        elif uploaded_file.name.endswith('.csv'):
            df = {"CSV": pd.read_csv(uploaded_file)}

        for sheet_name, data in df.items():
            st.subheader(f"Sheet: {sheet_name}")

            st.write("Columns available:", list(data.columns))
            col_options = ["All Columns"] + list(data.columns)
            col_choice = st.selectbox(f"Select column to analyze in {sheet_name}:", col_options, key=sheet_name)

            # Build data to scan
            if col_choice == "All Columns":
                scan_data = data.astype(str)
            else:
                scan_data = data[[col_choice]].astype(str)

            # Flatten all text into row-wise lists of words
            word_matrix = []
            for idx, row in scan_data.iterrows():
                row_words = set()
                for val in row:
                    row_words.update(re.findall(r'\w+', val.lower()))
                word_matrix.append(row_words)

            # Identify all unique words
            all_words = sorted(set.union(*word_matrix))

            # Build binary matrix
            matrix = []
            for row_words in word_matrix:
                matrix.append([1 if word in row_words else 0 for word in all_words])

            matrix_df = pd.DataFrame(matrix, columns=all_words)
            matrix_df.insert(0, "Row", data.index)

            # Replace 1/0 with checkmark or blank
            display_df = matrix_df.replace({1: "✓", 0: ""})

            st.write("✅ Redundancy Theme Matrix")
            st.dataframe(display_df)

            # Downloadable Excel
            excel_bytes = io.BytesIO()
            with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
                display_df.to_excel(writer, sheet_name=f"{sheet_name}_Matrix", index=False)
            excel_bytes.seek(0)
            st.download_button(
                label=f"📥 Download Excel Report for {sheet_name}",
                data=excel_bytes,
                file_name=f"redundancy_matrix_{sheet_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
