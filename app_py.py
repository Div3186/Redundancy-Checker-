import streamlit as st
import pandas as pd
import io
from collections import Counter
import re

st.title("📊 Redundancy Theme Checker")

uploaded_file = st.file_uploader("Upload Excel or CSV File", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        df = None
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)

        if df is not None:
            st.write("Columns available:", list(df.columns))
            col_name = st.selectbox("Select the column to check redundancy/themes:", df.columns)

            # Clean and split text into words
            all_text = df[col_name].dropna().astype(str).str.lower()
            words = []
            for line in all_text:
                tokens = re.findall(r'\w+', line)
                words.extend(tokens)

            # Count word frequencies
            word_counts = Counter(words)
            word_freq_df = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False)

            st.subheader("Top Redundant Words / Themes")
            st.dataframe(word_freq_df)

            # Filter/search box
            search = st.text_input("Search themes (words) here")
            if search:
                filtered = word_freq_df[word_freq_df['Word'].str.contains(search, case=False)]
                st.dataframe(filtered)

            # Download report
            excel_bytes = io.BytesIO()
            with pd.ExcelWriter(excel_bytes, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='OriginalData', index=False)
                word_freq_df.to_excel(writer, sheet_name='RedundancyThemes', index=False)
            excel_bytes.seek(0)
            st.download_button(
                label="📥 Download Excel Report with Themes",
                data=excel_bytes,
                file_name="redundancy_themes_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
