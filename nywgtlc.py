import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# === PAGE CONFIG ===
st.set_page_config(page_title="NYWG TLC Compliance Report", layout="centered")

# === Upload CSV ===
st.title("TLC Compliance Report")
uploaded_file = st.file_uploader("Upload TLC_Progression CSV file", type="csv")

# === Mappings ===
squadron_map = {
    "NER-NY-030": "ORANGE COUNTY CADET SQDN",
    "NER-NY-072": "ROCKLAND CADET SQDN",
    "NER-NY-159": "DUTCHESS COUNTY CADET SQUADRON",
    "NER-NY-387": "SULLIVAN COUNTY CADET SQUADRON",
    "NER-NY-395": "ULSTER COUNTY FLIGHT",
    "NER-NY-413": "ORANGE COUNTY SENIOR SQDN",
    "NER-NY-421": "DUTCHESS COUNTY FLIGHT",
    "NER-NY-134": "CENTRAL NEW YORK GROUP",
    "NER-NY-135": "LT COL WILLIAM A. SHAFER CADET SQUADRON",
    "NER-NY-156": "MOHAWK GRIFFISS SENIOR SQDN",
    "NER-NY-162": "UTICA CADET SQUADRON",
    "NER-NY-189": "TRI-COUNTY FLIGHT",
    "NER-NY-292": "SOUTHERN TIER COMPOSITE SQUADRON",
    "NER-NY-406": "FORT DRUM COMPOSITE SQUADRON",
    "NER-NY-408": "F.R. SUSSEY COMPOSITE SQDN",
    "NER-NY-109": "FINGER LAKES GROUP",
    "NER-NY-111": "NEWARK COMPOSITE SQUADRON",
    "NER-NY-212": "CANANDAIGUA COMPOSITE SQDN",
    "NER-NY-253": "BATAVIA COMPOSITE SQUADRON",
    "NER-NY-273": "ROCHESTER COMPOSITE SQDN",
    "NER-NY-283": "TWIN TIERS CADET SQUADRON",
    "NER-NY-354": "CONDOR COMPOSITE SQDN",
    "NER-NY-412": "ROCHESTER SENIOR SQDN",
    "NER-NY-117": "COL FRANCIS S. GABRESKI CADET SQDN",
    "NER-NY-153": "LEROY R. GRUMMAN CADET SQUADRON",
    "NER-NY-311": "9TH SUFFOLK CADET SQUADRON",
    "NER-NY-328": "SUFFOLK CADET SQDN 10",
    "NER-NY-332": "THE SPIRIT OF TUSKEGEE CADET SQUADRON",
    "NER-NY-420": "LT VINCENT R. CAPODANNO COMPOSITE SQUADRON",
    "NER-NY-614": "BUFFALO CREEK CADET SQUADRON",
    "NER-NY-048": "WESTCHESTER CADET SQDN 1",
    "NER-NY-033": "PUTNAM COUNTY COMPOSITE SQUADRON",
    "NER-NY-384": "BROOKLYN TECH CADET SQDN. #1",
    "NER-NY-390": "VANGUARD COMPOSITE SQUADRON",
    "NER-NY-422": "LT ANTHONY L WILLSEA CADET SQUADRON",
    "NER-NY-423": "BRONX AEROSPACE CADET SQUADRON",
    "NER-NY-373": "FLOYD BENNETT COMPOSITE SQUADRON"
}

unit_to_group = {
    "NER-NY-030": "Catskill Mountain Group",
    "NER-NY-072": "Catskill Mountain Group",
    "NER-NY-159": "Catskill Mountain Group",
    "NER-NY-387": "Catskill Mountain Group",
    "NER-NY-395": "Catskill Mountain Group",
    "NER-NY-413": "Catskill Mountain Group",
    "NER-NY-421": "Catskill Mountain Group",
    "NER-NY-134": "Central New York Group",
    "NER-NY-135": "Central New York Group",
    "NER-NY-156": "Central New York Group",
    "NER-NY-162": "Central New York Group",
    "NER-NY-189": "Central New York Group",
    "NER-NY-292": "Central New York Group",
    "NER-NY-406": "Central New York Group",
    "NER-NY-408": "Central New York Group",
    "NER-NY-109": "Finger Lakes Group",
    "NER-NY-111": "Finger Lakes Group",
    "NER-NY-212": "Finger Lakes Group",
    "NER-NY-253": "Finger Lakes Group",
    "NER-NY-273": "Finger Lakes Group",
    "NER-NY-283": "Finger Lakes Group",
    "NER-NY-354": "Finger Lakes Group",
    "NER-NY-412": "Finger Lakes Group",
    "NER-NY-117": "Long Island Group",
    "NER-NY-153": "Long Island Group",
    "NER-NY-311": "Long Island Group",
    "NER-NY-328": "Long Island Group",
    "NER-NY-332": "Long Island Group",
    "NER-NY-420": "Long Island Group",
    "NER-NY-614": "Long Island Group",
    "NER-NY-048": "South Eastern Group",
    "NER-NY-033": "South Eastern Group",
    "NER-NY-384": "South Eastern Group",
    "NER-NY-390": "South Eastern Group",
    "NER-NY-422": "South Eastern Group",
    "NER-NY-423": "South Eastern Group",
    "NER-NY-373": "South Eastern Group"
}

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Date parsing
    df["BasicCompleted_Date"] = pd.to_datetime(df["BasicCompleted"], errors='coerce')
    df["IntCompleted_Date"] = pd.to_datetime(df["IntCompleted"], errors='coerce')
    cutoff_date = datetime.now() - timedelta(days=4 * 365)

    df["Valid_TLC"] = (
        (df["BasicCompleted_Date"] >= cutoff_date) |
        (df["IntCompleted_Date"] >= cutoff_date)
    )

    valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
    unit_counts = valid_df.groupby("Organization")["CAPID"].nunique().reset_index()
    unit_counts.columns = ["Unit", "Members_with_Valid_TLC"]

    unit_total_counts = df.groupby("Organization")["CAPID"].nunique().reset_index()
    unit_total_counts.columns = ["Unit", "Total_Members"]

    unit_counts = unit_counts.merge(unit_total_counts, on="Unit", how="left")
    unit_counts["Squadron_Name"] = unit_counts["Unit"].map(lambda x: squadron_map.get(x.strip(), "Unknown Unit"))
    unit_counts["Group"] = unit_counts["Unit"].map(lambda x: unit_to_group.get(x.strip(), "Unknown Group"))

    unit_counts = unit_counts[~unit_counts["Squadron_Name"].str.contains("GROUP|SENIOR|HQ", case=False, na=False)]
    unit_counts = unit_counts[unit_counts["Squadron_Name"] != "Unknown Unit"]

    unit_counts["Compliant"] = unit_counts["Members_with_Valid_TLC"].apply(lambda x: "Yes" if x >= 2 else "No")
    unit_counts["Percent_Compliant"] = (unit_counts["Members_with_Valid_TLC"] / unit_counts["Total_Members"] * 100).round(1)

    group_summary = unit_counts.groupby("Group").agg({
        "Members_with_Valid_TLC": "sum",
        "Total_Members": "sum"
    }).reset_index()
    group_summary["Group_Percent_Compliant"] = (group_summary["Members_with_Valid_TLC"] / group_summary["Total_Members"] * 100).round(1)

    unit_counts = unit_counts.merge(group_summary[["Group", "Group_Percent_Compliant"]], on="Group", how="left")
    unit_counts = unit_counts.sort_values(by=["Group", "Squadron_Name"])

    total_compliant = (unit_counts["Compliant"] == "Yes").sum()
    total_non_compliant = (unit_counts["Compliant"] == "No").sum()

    st.subheader("TLC Compliance Summary")
    st.markdown(f"**Total Compliant Units:** {total_compliant}")
    st.markdown(f"**Total Non-Compliant Units:** {total_non_compliant}")
    st.subheader("Full Report")
    st.dataframe(unit_counts)

    # === Printable HTML Preview ===
    st.subheader("Printable Report Preview")

    html_content = """
    <style>
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 6px; font-size: 13px; }
        th { background-color: #f2f2f2; }
    </style>
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/mcks0120/nywg-tlc/main/298903439_5485841021479213_274053999167640142_n.png' width='120'/>
        <h2 style='margin-bottom: 0;'>NYWG Training Leader of Cadets</h2>
        <h4 style='margin-top: 4px;'>Subordinate Unit Compliance Report</h4>
    </div>
    """

    for group in unit_counts["Group"].unique():
        html_content += f"<h4>{group}</h4><table>"
        html_content += "<tr><th>Squadron</th><th>Compliant?</th><th>Valid TLC</th><th>Total</th><th>% Unit</th><th>% Group</th></tr>"
        for _, row in unit_counts[unit_counts["Group"] == group].iterrows():
            html_content += f"<tr><td>{row['Squadron_Name']}</td><td>{row['Compliant']}</td><td>{row['Members_with_Valid_TLC']}</td>"
            html_content += f"<td>{row['Total_Members']}</td><td>{row['Percent_Compliant']}%</td><td>{row['Group_Percent_Compliant']}%</td></tr>"
        html_content += "</table><br>"

    st.markdown(html_content, unsafe_allow_html=True)
    st.info("To print or save this report as a PDF, use your browser's Print feature (Ctrl+P or Cmd+P).")
