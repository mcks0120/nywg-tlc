# app.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import importlib.util

st.set_page_config(page_title="NYWG TLC Compliance Dashboard", layout="wide")

st.title("NYWG Training Leaders of Cadets Compliance Dashboard")
st.markdown("Upload the **TLC_Progression.csv** to see which units are non-compliant. Compliance requires at least two members with valid TLC (Basic, Intermediate, or Advanced) within the past 4 years.")

# Load unit reference data
@st.cache_data
def load_unit_reference():
    spec = importlib.util.spec_from_file_location("unit_reference_data", "unit_reference_data.py")
    unit_ref = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(unit_ref)
    df = pd.DataFrame(unit_ref.unit_reference_data)
    df = df[df['Unit Type'].isin(['cadet', 'comp', 'flight'])]
    return df

unit_df = load_unit_reference()

uploaded_file = st.file_uploader("Upload TLC_Progression.csv", type=["csv"])

if uploaded_file:
    tlc_df = pd.read_csv(uploaded_file)

    # Convert dates
    date_columns = ['OnDemandCompleted', 'BasicCompleted', 'IntCompleted', 'AdvCompleted']
    for col in date_columns:
        if col in tlc_df.columns:
            tlc_df[col] = pd.to_datetime(tlc_df[col], errors='coerce')

    expiration_threshold = datetime.now() - timedelta(days=4*365)

    # Determine if member has any valid TLC
    tlc_df['HasValidTLC'] = tlc_df[date_columns].apply(
        lambda row: any(pd.notnull(date) and date > expiration_threshold for date in row), axis=1
    )

    valid_tlc_df = tlc_df[tlc_df['HasValidTLC']]
    tlc_counts = valid_tlc_df.groupby('Organization').size().reset_index(name='Valid TLC Count')

    # Merge with unit data
    unit_status_df = unit_df.merge(
        tlc_counts, left_on='Unit Number', right_on='Organization', how='left'
    ).fillna({'Valid TLC Count': 0})
    unit_status_df['Valid TLC Count'] = unit_status_df['Valid TLC Count'].astype(int)
    unit_status_df['TLC Compliant'] = unit_status_df['Valid TLC Count'] >= 2

    non_compliant_units = unit_status_df[~unit_status_df['TLC Compliant']]
    compliant_units = unit_status_df[unit_status_df['TLC Compliant']]

    st.subheader("Non-Compliant Units")
    st.dataframe(non_compliant_units[['Group', 'Unit Name', 'Unit Type', 'Unit Number', 'Valid TLC Count']])

    st.download_button(
        label="Download Non-Compliant Units as CSV",
        data=non_compliant_units.to_csv(index=False).encode(),
        file_name="non_compliant_units.csv",
        mime="text/csv"
    )

    with st.expander("Show All Units (including compliant)"):
        st.dataframe(unit_status_df[['Group', 'Unit Name', 'Unit Type', 'Unit Number', 'Valid TLC Count', 'TLC Compliant']])
else:
    st.info("Awaiting file upload.")
