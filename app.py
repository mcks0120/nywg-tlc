import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="NYWG TLC Compliance Dashboard", layout="wide")

st.title("NYWG Training Leader of Cadets")
st.subheader("Subordinate Unit Compliance Dashboard")

uploaded_file = st.file_uploader("Upload TLC Progression CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df["BasicCompleted"] = pd.to_datetime(df["BasicCompleted"], errors='coerce')
    df["IntermediateCompleted"] = pd.to_datetime(df["IntermediateCompleted"], errors='coerce')

    cutoff_date = datetime.now() - timedelta(days=4*365)

    df["HasValidTLC"] = ((df["BasicCompleted"] >= cutoff_date) | (df["IntermediateCompleted"] >= cutoff_date))

    compliance_df = df.groupby("Organization").agg(
        Total_Members=pd.NamedAgg(column="CAPID", aggfunc="nunique"),
        Members_Valid_TLC=pd.NamedAgg(column="HasValidTLC", aggfunc="sum")
    ).reset_index()

    compliance_df["Compliant"] = compliance_df["Members_Valid_TLC"].apply(lambda x: "Yes" if x >= 2 else "No")

    total_units = compliance_df.shape[0]
    compliant_units = compliance_df[compliance_df["Compliant"] == "Yes"].shape[0]
    compliance_rate = (compliant_units / total_units * 100) if total_units > 0 else 0

    st.metric(label="Overall Compliance Rate", value=f"{compliance_rate:.1f}%")

    st.subheader("Detailed Compliance by Unit")
    st.dataframe(compliance_df, use_container_width=True)

    non_compliant_units = compliance_df[compliance_df["Compliant"] == "No"]

    st.subheader("Non-Compliant Units")
    st.dataframe(non_compliant_units, use_container_width=True)
