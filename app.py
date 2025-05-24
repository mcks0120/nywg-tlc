import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import importlib.util

# === Page config ===
st.set_page_config(page_title="NYWG TLC Compliance Dashboard", layout="wide")
st.title("NYWG TLC Compliance Dashboard")

st.markdown("""
Upload the **TLC_Progression.csv** file. This tool will:
- Evaluate TLC completion (Basic, Intermediate, Advanced, On-Demand)
- Determine if squadrons are compliant (2+ members with valid TLC in the last 4 years)
- Allow you to download full and non-compliant reports
""")

# === File upload ===
uploaded_file = st.file_uploader("Upload TLC_Progression.csv", type="csv")

if not uploaded_file:
    st.stop()

# === Load uploaded TLC data ===
df = pd.read_csv(uploaded_file)

# === Replace "Incomplete" with missing and parse dates ===
date_columns = ["OnDemandCompleted", "BasicCompleted", "IntCompleted", "AdvCompleted"]
for col in date_columns:
    df[col] = df[col].replace("Incomplete", pd.NA)
    df[col + "_Date"] = pd.to_datetime(df[col], errors='coerce')

# === Define TLC expiration threshold ===
cutoff_date = datetime.now() - timedelta(days=4*365)

# === Check if member has valid TLC ===
df["Valid_TLC"] = df[[col + "_Date" for col in date_columns]].apply(
    lambda row: any(pd.notnull(date) and date >= cutoff_date for date in row), axis=1
)

# === Filter and count unique CAPIDs with valid TLC ===
valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
tlc_counts = valid_df.groupby("Organization")["CAPID"].nunique().reset_index()
tlc_counts.columns = ["Unit Number", "Members_with_Valid_TLC"]

# === Load unit reference data ===
spec = importlib.util.spec_from_file_location("unit_reference_data", "unit_reference_data.py")
unit_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unit_data)
unit_df = pd.DataFrame(unit_data.unit_reference_data)

# === Normalize unit numbers (remove NER- prefix) for matching ===
unit_df["Unit Number"] = unit_df["Unit Number"].str.replace("NER-", "", regex=False)
tlc_counts["Unit Number"] = tlc_counts["Unit Number"].str.replace("NER-", "", regex=False)

# === Filter only cadet, composite, and flight squadrons ===
unit_df = unit_df[unit_df["Unit Type"].isin(["cadet", "comp", "flight"])]

# === Merge and calculate compliance ===
report_df = unit_df.merge(tlc_counts, on="Unit Number", how="left").fillna({"Members_with_Valid_TLC": 0})
report_df["Members_with_Valid_TLC"] = report_df["Members_with_Valid_TLC"].astype(int)
report_df["TLC_Compliant"] = report_df["Members_with_Valid_TLC"] >= 2

# === Split non-compliant units ===
non_compliant_df = report_df[~report_df["TLC_Compliant"]]

# === Display report ===
st.subheader("Full Squadron Compliance Report")
st.dataframe(report_df, use_container_width=True)

st.subheader("Non-Compliant Units Only")
st.dataframe(non_compliant_df, use_container_width=True)

# === Download buttons ===
st.download_button(
    label="Download Full Report (CSV)",
    data=report_df.to_csv(index=False).encode(),
    file_name="tlc_unit_compliance_report.csv",
    mime="text/csv"
)

st.download_button(
    label="Download Non-Compliant Units Only (CSV)",
    data=non_compliant_df.to_csv(index=False).encode(),
    file_name="tlc_non_compliant_units.csv",
    mime="text/csv"
)