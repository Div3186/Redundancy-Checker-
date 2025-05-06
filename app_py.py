import streamlit as st
import pandas as pd
import numpy as np
import io
import re

st.title("📊 Redundancy Matrix")

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

            # Prepare data
            if col_choice == "All Columns":
                scan_data = data.astype(str)
            else:
                scan_data = data[[col_choice]].astype(str)

            # Get file name column (assumed to be first column)
            file_name_col = data.columns[0]
            file_names = data[file_name_col].astype(str).tolist()

            word_matrix = []
            for idx, row in scan_data.iterrows():
                row_words = set()
                for val in row:
                    row_words.update(re.findall(r'\w+', val.lower()))
                word_matrix.append(row_words)

            all_words = sorted(set.union(*word_matrix))

            matrix = []
            for row_words in word_matrix:
                matrix.append([1 if word in row_words else 0 for word in all_words])

            matrix_df = pd.DataFrame(matrix, columns=all_words)
            matrix_df.insert(0, "File Name", file_names)
            matrix_df.insert(1, "Row", data.index)

            display_df = matrix_df.replace({1: "✓", 0: ""})

            st.subheader("✅ Redundancy Matrix")
            st.dataframe(display_df)

            # Exact cell locations report
            theme_locations = []
            for row_idx, row in scan_data.iterrows():
                for col_name, cell_value in row.items():
                    words = re.findall(r'\w+', str(cell_value).lower())
                    for word in words:
                        theme_locations.append({
                            'Theme': word,
                            'Row Index': row_idx,
                            'File Name': file_names[row_idx],
                            'Column': col_name,
                            'Cell Value': cell_value
                        })

            theme_df = pd.DataFrame(theme_locations)
            if not theme_df.empty:
                st.subheader("📍 Exact Cell Locations")
                st.dataframe(theme_df)

            # Downloadable Excel report
            excel_bytes = io.BytesIO()
            with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
                display_df.to_excel(writer, sheet_name=f"{sheet_name}_Matrix", index=False)
                if not theme_df.empty:
                    theme_df.to_excel(writer, sheet_name=f"{sheet_name}_Locations", index=False)
            excel_bytes.seek(0)
            st.download_button(
                label=f"📥 Download Excel Report for {sheet_name}",
                data=excel_bytes,
                file_name=f"redundancy_matrix_{sheet_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
