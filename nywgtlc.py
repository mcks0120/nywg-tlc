import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

st.title("NYWG TLC Validity Report Generator")

uploaded_file = st.file_uploader("Upload TLC_Progression CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        df["BasicCompleted_Date"] = pd.to_datetime(df["BasicCompleted"], errors='coerce')
        df["IntCompleted_Date"] = pd.to_datetime(df["IntCompleted"], errors='coerce')

        cutoff_date = datetime.now() - timedelta(days=4*365)

        df["Valid_TLC"] = (
            (df["BasicCompleted_Date"] >= cutoff_date) |
            (df["IntCompleted_Date"] >= cutoff_date)
        )

        valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
        unit_counts = valid_df.groupby("Organization")["CAPID"].nunique().reset_index()
        unit_counts.columns = ["Unit", "Members_with_Valid_TLC"]

        st.subheader("Members with Valid TLC per Unit")
        st.dataframe(unit_counts)

        output = BytesIO()
        unit_counts.to_excel(output, index=False)
        st.download_button(
            label="Download Excel Report",
            data=output.getvalue(),
            file_name="tlcreport.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error processing file: {e}")
