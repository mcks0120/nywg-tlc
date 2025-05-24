import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
from xhtml2pdf import pisa

st.set_page_config(page_title="NYWG TLC Compliance Report", layout="wide")

st.title("NYWG Training Leader of Cadets")
st.subheader("Subordinate Unit Compliance Overview")
uploaded_file = st.file_uploader("Upload TLC_Progression CSV file", type="csv")

unit_to_group = {
    'NER-NY-030': 'Catskill Mountain Group',
    'NER-NY-072': 'Catskill Mountain Group',
    'NER-NY-159': 'Catskill Mountain Group',
    'NER-NY-134': 'Central New York Group',
    'NER-NY-135': 'Central New York Group'
    # Add remaining mappings
}

squadron_map = {
    "NER-NY-030": "Orange County Cadet Squadron",
    "NER-NY-072": "Rockland Cadet Squadron",
    "NER-NY-159": "Dutchess County Cadet Squadron",
    "NER-NY-134": "Central New York Group",
    "NER-NY-135": "Lt Col William A. Shafer Cadet Squadron"
    # Add remaining mappings
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

    html = """
    <style>
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 6px; font-size: 12px; }
        .group-row { background-color: #d9d9d9; font-weight: bold; }
        .compliant { background-color: #d4edda; }
        .noncompliant { background-color: #f8d7da; }
    </style>
    <table>
        <tr><th>Group</th><th>Squadron</th><th>Compliant</th><th>Valid TLC</th><th>Total</th></tr>
    """

    for group in unit_counts["Group"].unique():
        html += f"<tr class='group-row'><td>{group}</td><td colspan='4'></td></tr>"
        group_df = unit_counts[unit_counts["Group"] == group]
        for _, row in group_df.iterrows():
            css_class = "compliant" if row["Compliant"] == "Yes" else "noncompliant"
            html += f"<tr class='{css_class}'><td></td><td>{row['Squadron']}</td><td>{row['Compliant']}</td><td>{row['Members_with_Valid_TLC']}</td><td>{row['Total_Members']}</td></tr>"

    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

    def html_to_pdf(source_html):
        output = BytesIO()
        pisa.CreatePDF(source_html, dest=output)
        return output.getvalue()

    pdf = html_to_pdf(html)
    st.download_button("Download PDF Report", data=pdf, file_name="TLC_Report.pdf", mime="application/pdf")
