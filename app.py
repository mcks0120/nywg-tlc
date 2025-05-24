import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from xhtml2pdf import pisa

# === CONFIG ===
st.set_page_config(page_title="NYWG TLC Compliance Report", layout="wide")
st.title("NYWG Training Leader of Cadets")
st.subheader("Subordinate Unit Compliance Overview")
uploaded_file = st.file_uploader("Upload TLC_Progression CSV file", type="csv")

# === MAPPINGS ===
unit_to_group = {
    'NER-NY-035': 'Catskill Mountain Group',
    'NER-NY-030': 'Catskill Mountain Group',
    'NER-NY-072': 'Catskill Mountain Group',
    'NER-NY-159': 'Catskill Mountain Group',
    'NER-NY-387': 'Catskill Mountain Group',
    'NER-NY-395': 'Catskill Mountain Group',
    'NER-NY-413': 'Catskill Mountain Group',
    'NER-NY-421': 'Catskill Mountain Group',
    'NER-NY-134': 'Central New York Group',
    'NER-NY-135': 'Central New York Group',
    'NER-NY-156': 'Central New York Group',
    'NER-NY-162': 'Central New York Group',
    'NER-NY-189': 'Central New York Group',
    'NER-NY-292': 'Central New York Group',
    'NER-NY-406': 'Central New York Group',
    'NER-NY-408': 'Central New York Group',
    'NER-NY-109': 'Finger Lakes Group',
    'NER-NY-111': 'Finger Lakes Group',
    'NER-NY-212': 'Finger Lakes Group',
    'NER-NY-253': 'Finger Lakes Group',
    'NER-NY-273': 'Finger Lakes Group',
    'NER-NY-283': 'Finger Lakes Group',
    'NER-NY-354': 'Finger Lakes Group',
    'NER-NY-412': 'Finger Lakes Group',
    'NER-NY-117': 'Long Island Group',
    'NER-NY-153': 'Long Island Group',
    'NER-NY-311': 'Long Island Group',
    'NER-NY-328': 'Long Island Group',
    'NER-NY-332': 'Long Island Group',
    'NER-NY-420': 'Long Island Group',
    'NER-NY-614': 'Long Island Group',
    'NER-NY-048': 'South Eastern Group',
    'NER-NY-033': 'South Eastern Group',
    'NER-NY-384': 'South Eastern Group',
    'NER-NY-390': 'South Eastern Group',
    'NER-NY-422': 'South Eastern Group',
    'NER-NY-423': 'South Eastern Group',
    'NER-NY-373': 'South Eastern Group'
}

squadron_map = {
    "NER-NY-030": "Orange County Cadet Squadron",
    "NER-NY-035": "Catskill Mountain Cadet Squadron",
    "NER-NY-072": "Rockland Cadet Squadron",
    "NER-NY-159": "Dutchess County Cadet Squadron",
    "NER-NY-387": "Sullivan County Cadet Squadron",
    "NER-NY-395": "Ulster County Flight",
    "NER-NY-413": "Orange County Senior Squadron",
    "NER-NY-421": "Dutchess County Flight",
    "NER-NY-134": "Central New York Group",
    "NER-NY-135": "Lt Col William A. Shafer Cadet Squadron",
    "NER-NY-156": "Mohawk Griffiss Senior Squadron",
    "NER-NY-162": "Utica Cadet Squadron",
    "NER-NY-189": "Tri-County Flight",
    "NER-NY-292": "Southern Tier Composite Squadron",
    "NER-NY-406": "Fort Drum Composite Squadron",
    "NER-NY-408": "F.R. Sussey Composite Squadron",
    "NER-NY-109": "Finger Lakes Group",
    "NER-NY-111": "Newark Composite Squadron",
    "NER-NY-212": "Canandaigua Composite Squadron",
    "NER-NY-253": "Batavia Composite Squadron",
    "NER-NY-273": "Rochester Composite Squadron",
    "NER-NY-283": "Twin Tiers Cadet Squadron",
    "NER-NY-354": "Condor Composite Squadron",
    "NER-NY-412": "Rochester Senior Squadron",
    "NER-NY-117": "Col Francis S. Gabreski Cadet Squadron",
    "NER-NY-153": "Leroy R. Grumman Cadet Squadron",
    "NER-NY-311": "9th Suffolk Cadet Squadron",
    "NER-NY-328": "Suffolk Cadet Squadron 10",
    "NER-NY-332": "The Spirit of Tuskegee Cadet Squadron",
    "NER-NY-420": "Lt Vincent R. Capodanno Composite Squadron",
    "NER-NY-614": "Buffalo Creek Cadet Squadron",
    "NER-NY-048": "Westchester Cadet Squadron 1",
    "NER-NY-033": "Putnam County Composite Squadron",
    "NER-NY-384": "Brooklyn Tech Cadet Squadron #1",
    "NER-NY-390": "Vanguard Composite Squadron",
    "NER-NY-422": "Lt Anthony L Willsea Cadet Squadron",
    "NER-NY-423": "Bronx Aerospace Cadet Squadron",
    "NER-NY-373": "Floyd Bennett Composite Squadron"
}

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    df["BasicCompleted_Date"] = pd.to_datetime(df["BasicCompleted"], errors='coerce')
    df["IntCompleted_Date"] = pd.to_datetime(df["IntCompleted"], errors='coerce')
    cutoff = datetime.now() - timedelta(days=4*365)

    df["Valid_TLC"] = (df["BasicCompleted_Date"] >= cutoff) | (df["IntCompleted_Date"] >= cutoff)

    unit_total = df.groupby("Organization")["CAPID"].nunique().reset_index().rename(columns={"Organization": "Unit", "CAPID": "Total_Members"})
    valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
    unit_valid = valid_df.groupby("Organization")["CAPID"].nunique().reset_index().rename(columns={"Organization": "Unit", "CAPID": "Members_with_Valid_TLC"})

    unit_counts = pd.merge(unit_total, unit_valid, on="Unit", how="left").fillna(0)
    unit_counts["Members_with_Valid_TLC"] = unit_counts["Members_with_Valid_TLC"].astype(int)
    unit_counts["Compliant"] = unit_counts["Members_with_Valid_TLC"].apply(lambda x: "Yes" if x >= 2 else "No")
    unit_counts["Group"] = unit_counts["Unit"].map(unit_to_group).fillna("Unknown Group")
    unit_counts["Squadron"] = unit_counts["Unit"].map(squadron_map).fillna(unit_counts["Unit"])

    group_summary = unit_counts.groupby("Group").agg({
        "Members_with_Valid_TLC": "sum",
        "Total_Members": "sum"
    }).reset_index()
    group_summary["Percent_Compliant"] = (group_summary["Members_with_Valid_TLC"] / group_summary["Total_Members"] * 100).round(1)

    unit_counts = unit_counts.merge(group_summary[["Group", "Percent_Compliant"]], on="Group", how="left")
    unit_counts = unit_counts.sort_values(by=["Group", "Squadron"])

    # === HTML Preview ===
    st.subheader("Compliance Report")
    html = """
    <style>
        table, th, td {
            border: 1px solid black;
            border-collapse: collapse;
            padding: 6px;
            font-size: 12px;
        }
        .group-row {
            background-color: #d9d9d9;
            font-weight: bold;
        }
        .compliant {
            background-color: #d4edda;
        }
        .noncompliant {
            background-color: #f8d7da;
        }
    </style>
    <table>
        <tr><th>Group</th><th>Squadron</th><th>Compliant</th><th>Valid TLC</th><th>Total</th><th>% Group</th></tr>
    """

    for group in unit_counts["Group"].unique():
        group_df = unit_counts[unit_counts["Group"] == group]
        percent = group_df["Percent_Compliant"].iloc[0]
        html += f"<tr class='group-row'><td>{group}</td><td colspan='4'></td><td>{percent:.1f}%</td></tr>"

        for _, row in group_df.iterrows():
            css = "compliant" if row["Compliant"] == "Yes" else "noncompliant"
            html += f"<tr class='{css}'><td></td><td>{row['Squadron']}</td><td>{row['Compliant']}</td><td>{row['Members_with_Valid_TLC']}</td><td>{row['Total_Members']}</td><td></td></tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    # === PDF Export ===
    def convert_html_to_pdf(source_html):
        output = BytesIO()
        pisa_status = pisa.CreatePDF(source_html, dest=output)
        return output if not pisa_status.err else None

    pdf = convert_html_to_pdf(html)
    if pdf:
        st.download_button("Download PDF", data=pdf.getvalue(), file_name="TLC_Report.pdf", mime="application/pdf")
