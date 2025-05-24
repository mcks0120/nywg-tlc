import sys
import pandas as pd
from datetime import datetime, timedelta
import importlib.util

# === Load TLC CSV file ===
file_path = "TLC_Progression.csv"  # Update this if needed
df = pd.read_csv(file_path)

# === Treat "Incomplete" as missing and convert columns to datetime ===
date_columns = ["OnDemandCompleted", "BasicCompleted", "IntCompleted", "AdvCompleted"]
for col in date_columns:
    df[col] = df[col].replace("Incomplete", pd.NA)
    df[col + "_Date"] = pd.to_datetime(df[col], errors='coerce')

# === Define cutoff date (4 years ago) ===
cutoff_date = datetime.now() - timedelta(days=4*365)

# === Determine if member has valid TLC (any of the four levels) ===
df["Valid_TLC"] = df[[col + "_Date" for col in date_columns]].apply(
    lambda row: any(pd.notnull(date) and date >= cutoff_date for date in row), axis=1
)

# === Filter valid members and remove duplicate CAPIDs per unit ===
valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
tlc_counts = valid_df.groupby("Organization")["CAPID"].nunique().reset_index()
tlc_counts.columns = ["Unit Number", "Members_with_Valid_TLC"]

# === Load unit reference data from Python module ===
spec = importlib.util.spec_from_file_location("unit_reference_data", "unit_reference_data.py")
unit_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unit_data)
unit_df = pd.DataFrame(unit_data.unit_reference_data)

# === Normalize unit numbers for matching (remove "NER-" from both sides) ===
unit_df["Unit Number"] = unit_df["Unit Number"].str.replace("NER-", "", regex=False)
tlc_counts["Unit Number"] = tlc_counts["Unit Number"].str.replace("NER-", "", regex=False)

# === Filter to cadet, composite, and flight squadrons only ===
unit_df = unit_df[unit_df["Unit Type"].isin(["cadet", "comp", "flight"])]

# === Merge TLC counts with unit reference data ===
report_df = unit_df.merge(tlc_counts, on="Unit Number", how="left").fillna({"Members_with_Valid_TLC": 0})
report_df["Members_with_Valid_TLC"] = report_df["Members_with_Valid_TLC"].astype(int)
report_df["TLC_Compliant"] = report_df["Members_with_Valid_TLC"] >= 2

# === Export results ===
excel_output = "tlc_unit_compliance_report.xlsx"
csv_output = "tlc_unit_compliance_report.csv"
report_df.to_excel(excel_output, index=False)
report_df.to_csv(csv_output, index=False)

print(f"Reports saved as:\n- {excel_output}\n- {csv_output}")