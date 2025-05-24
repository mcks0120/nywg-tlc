# app.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import importlib.util

st.set_page_config(page_title="NYWG TLC Compliance Dashboard", layout="wide")
st.title("NYWG Training Leaders of Cadets Compliance Dashboard")

st.markdown("""
**Instructions:** Upload the latest `TLC_Progression.csv` file.
This report will show:
- How many members in each squadron have valid TLC (within 4 years)
- Whether or not the unit is compliant (2 or more valid TLC holders)
Only cadet, composite, and flight squadrons are included.
""")

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

    # Check required columns
    required_cols = ['Organization', 'OnDemandCompleted', 'BasicCompleted', 'IntCompleted', 'AdvCompleted']
    if not all(col in tlc_df.columns for col in required_cols):
        st.error(f"CSV is missing one or more required columns: {required_cols}")
    else:
        # Convert TLC dates
        date_columns = ['OnDemandCompleted', 'BasicCompleted', 'IntCompleted', 'AdvCompleted']
        for col in date_columns:
            tlc_df[col] = pd.to_datetime(tlc_df[col], errors='coerce')

        expiration_threshold = datetime.now() - timedelta(days=4*365)

        # Determine if member has any valid TLC
        tlc_df['HasValidTLC'] = tlc_df[date_columns].apply(
            lambda row: any(pd.notnull(date) and date > expiration_threshold for date in row), axis=1
        )

        valid_tlc_df = tlc_df[tlc_df['HasValidTLC']]
        tlc_counts = valid_tlc_df.groupby('Organization').size().reset_index(name='Valid TLC Members')

        # Merge TLC counts into unit list
        report_df = unit_df.merge(
            tlc_counts, left_on='Unit Number', right_on='Organization', how='left'
        ).fillna({'Valid TLC Members': 0})
        report_df['Valid TLC Members'] = report_df['Valid TLC Members'].astype(int)
        report_df['TLC Compliant'] = report_df['Valid TLC Members'] >= 2

        # Final display table
        final_report = report_df[['Group', 'Unit Name', 'Unit Type', 'Unit Number', 'Valid TLC Members', 'TLC Compliant']].sort_values(by='Group')

        st.subheader("TLC Compliance Report")
        st.dataframe(final_report, use_container_width=True)

        st.download_button(
            label="Download Full Report as CSV",
            data=final_report.to_csv(index=False).encode(),
            file_name="tlc_compliance_report.csv",
            mime="text/csv"
        )
else:
    st.info("Awaiting file upload...")
