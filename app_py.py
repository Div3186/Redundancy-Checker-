import streamlit as st
import pandas as pd
import numpy as np
import io
import re

st.title("📊 Redundancy Theme Matrix with Cell Locations")

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

            theme_locations = []

            for row_idx, row in scan_data.iterrows():
                for col_name, cell_value in row.items():
                    words = re.findall(r'\w+', str(cell_value).lower())
                    for word in words:
                        theme_locations.append({
                            'Theme': word,
                            'Row Index': row_idx,
                            'Column': col_name,
                            'Cell Value': cell_value
                        })

            # Convert to DataFrame
            theme_df = pd.DataFrame(theme_locations)
            if theme_df.empty:
                st.info("No themes/words found in this sheet or column.")
                continue

            # Summary matrix: row vs. themes
            summary = theme_df.pivot_table(index='Row Index', columns='Theme', aggfunc='size', fill_value=0)
            summary = summary.applymap(lambda x: '✓' if x > 0 else '')

            st.subheader("✅ Redundancy Theme Matrix")
            st.dataframe(summary)

            st.subheader("📍 Exact Cell Locations (Row, Column, Value)")
            st.dataframe(theme_df)

            # Downloadable Excel report
            excel_bytes = io.BytesIO()
            with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
                summary.to_excel(writer, sheet_name=f"{sheet_name}_Matrix")
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
