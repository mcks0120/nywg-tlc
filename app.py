import streamlit as st
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# Embedded mapping: clean version using just the unit code as keys
squadron_map = {
    "NER-NY-001": "NEW YORK WING HQ",
    "NER-NY-015": "NEW YORK CITY GROUP",
    "NER-NY-020": "SOUTHTOWNS CADET SQDN",
    "NER-NY-022": "BUFFALO COMPOSITE SQUADRON #1",
    "NER-NY-024": "WESTERN NEW YORK GROUP",
    "NER-NY-030": "ORANGE COUNTY CADET SQDN",
    "NER-NY-033": "PUTNAM COUNTY COMPOSITE SQUADRON",
    "NER-NY-035": "CATSKILL MOUNTAIN GROUP",
    "NER-NY-043": "MID-EASTERN GROUP",
    "NER-NY-048": "WESTCHESTER CADET SQDN 1",
    "NER-NY-072": "ROCKLAND CADET SQDN",
    "NER-NY-073": "SCHENECTADY COMPOSITE SQDN",
    "NER-NY-089": "BRONX CADET SQUADRON",
    "NER-NY-109": "FINGER LAKES GROUP",
    "NER-NY-111": "NEWARK COMPOSITE SQUADRON",
    "NER-NY-116": "NIAGARA FALLS COMPOSITE SQUADRON",
    "NER-NY-117": "COL FRANCIS S. GABRESKI CADET SQDN",
    "NER-NY-118": "SOUTH EASTERN GROUP",
    "NER-NY-134": "CENTRAL NEW YORK GROUP",
    "NER-NY-135": "LT COL WILLIAM A. SHAFER CADET SQUADRON",
    "NER-NY-147": "ACADEMY CADET SQDN",
    "NER-NY-153": "LEROY R. GRUMMAN CADET SQUADRON",
    "NER-NY-156": "MOHAWK GRIFFISS SENIOR SQDN",
    "NER-NY-159": "DUTCHESS COUNTY CADET SQUADRON",
    "NER-NY-162": "UTICA CADET SQUADRON",
    "NER-NY-173": "TAK COMPOSITE SQDN",
    "NER-NY-189": "TRI-COUNTY FLIGHT",
    "NER-NY-207": "LONG ISLAND SENIOR SQDN",
    "NER-NY-212": "CANANDAIGUA COMPOSITE SQDN",
    "NER-NY-219": "WESTCHESTER HUDSON SENIOR SQUADRON",
    "NER-NY-238": "COL JOHNNIE PANTANELLI COMPOSITE SQUADRON",
    "NER-NY-247": "BRIAN M. MOONEY CADET SQDN",
    "NER-NY-251": "LONG ISLAND GROUP",
    "NER-NY-253": "BATAVIA COMPOSITE SQUADRON",
    "NER-NY-273": "ROCHESTER COMPOSITE SQDN",
    "NER-NY-283": "TWIN TIERS CADET SQUADRON",
    "NER-NY-288": "LT. QUENTIN ROOSEVELT CADET SQUADRON",
    "NER-NY-292": "SOUTHERN TIER COMPOSITE SQUADRON",
    "NER-NY-301": "PHOENIX COMPOSITE SQDN",
    "NER-NY-311": "9TH SUFFOLK CADET SQUADRON",
    "NER-NY-328": "SUFFOLK CADET SQDN 10",
    "NER-NY-332": "THE SPIRIT OF TUSKEGEE CADET SQUADRON",
    "NER-NY-343": "NIAGARA FRONTIER SENIOR FLIGHT",
    "NER-NY-351": "DUNKIRK COMPOSITE SQUADRON",
    "NER-NY-354": "CONDOR COMPOSITE SQDN",
    "NER-NY-361": "ALBANY SENIOR SQDN",
    "NER-NY-373": "FLOYD BENNETT COMPOSITE SQUADRON",
    "NER-NY-379": "FALCON SENIOR SQDN",
    "NER-NY-384": "BROOKLYN TECH CADET SQDN. #1",
    "NER-NY-387": "SULLIVAN COUNTY CADET SQUADRON",
    "NER-NY-388": "JAMES P. OCONNOR COMPOSITE SQDN",
    "NER-NY-390": "VANGUARD COMPOSITE SQUADRON",
    "NER-NY-392": "VEDDER COMPOSITE  SQDN",
    "NER-NY-395": "ULSTER COUNTY FLIGHT",
    "NER-NY-402": "JAMESTOWN COMPOSITE SQDN",
    "NER-NY-406": "FORT DRUM COMPOSITE SQUADRON",
    "NER-NY-408": "F.R. SUSSEY COMPOSITE SQDN",
    "NER-NY-412": "ROCHESTER SENIOR SQDN",
    "NER-NY-413": "ORANGE COUNTY SENIOR SQDN",
    "NER-NY-415": "CAPT LUKE C. WULLENWABER COMPOSITE SQUADRON",
    "NER-NY-420": "LT VINCENT R. CAPODANNO COMPOSITE SQUADRON",
    "NER-NY-421": "DUTCHESS COUNTY FLIGHT",
    "NER-NY-422": "LT ANTHONY L WILLSEA CADET SQUADRON",
    "NER-NY-423": "BRONX AEROSPACE CADET SQUADRON",
    "NER-NY-613": "BROOKLYN SENIOR SQUADRON",
    "NER-NY-614": "BUFFALO CREEK CADET SQUADRON"
}

st.title("TLC Validity Report Generator")

uploaded_file = st.file_uploader("Upload TLC_Progression CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        df["BasicCompleted_Date"] = pd.to_datetime(df["BasicCompleted"], errors='coerce')
        df["IntCompleted_Date"] = pd.to_datetime(df["IntCompleted"], errors='coerce')

        cutoff_date = datetime.now() - timedelta(days=4*365)
        latest_date = pd.concat([df["BasicCompleted_Date"], df["IntCompleted_Date"]]).max()
        st.markdown(f"**As of Date:** {latest_date.strftime('%B %d, %Y')}")

        df["Valid_TLC"] = (
            (df["BasicCompleted_Date"] >= cutoff_date) |
            (df["IntCompleted_Date"] >= cutoff_date)
        )

        valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
        unit_counts = valid_df.groupby("Organization")["CAPID"].nunique().reset_index()
        unit_counts.columns = ["Unit", "Members_with_Valid_TLC"]

        unit_counts["Squadron_Name"] = unit_counts["Unit"].map(lambda x: squadron_map.get(x.strip(), "Unknown Unit"))
        unit_counts["Compliant"] = unit_counts["Members_with_Valid_TLC"].apply(lambda x: "Yes" if x >= 2 else "No")

        unit_counts = unit_counts[["Unit", "Squadron_Name", "Members_with_Valid_TLC", "Compliant"]]

        st.subheader("TLC Compliance Report")
        st.dataframe(unit_counts)

        output = BytesIO()
        unit_counts.to_excel(output, index=False)
        st.download_button(
            label="Download Excel Report",
            data=output.getvalue(),
            file_name="tlc_compliance_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error: {e}")
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

        
        

    except Exception as e:
        st.error(f"Error processing file: {e}")

html_content = """
<style>
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 6px;
        font-size: 13px;
    }
    th { background-color: #f2f2f2; }
    .group-row {
        background-color: #d9d9d9;
        font-weight: bold;
    }
</style>

<div style='text-align: center;'>
    <img src='https://raw.githubusercontent.com/mcks0120/nywg-tlc/main/298903439_5485841021479213_274053999167640142_n.png' width='120'/>
    <h2 style='margin-bottom: 0;'>NYWG Training Leader of Cadets</h2>
    <h4 style='margin-top: 4px;'>Subordinate Unit Compliance</h4>
</div>
<br>
<table>
    <tr>
        <th>Group</th>
        <th>Squadron</th>
        <th>Compliant?</th>
        <th>Valid TLC</th>
        <th>Total Members</th>
        <th>% Group</th>
    </tr>
"""

for group in unit_counts["Group"].unique():
    group_df = unit_counts[unit_counts["Group"] == group]
    group_percent = group_summary.loc[group_summary["Group"] == group, "Group_Percent_Compliant"].values[0]

    html_content += f"""
    <tr class='group-row'>
        <td>{group}</td>
        <td colspan='4'></td>
        <td>{group_percent:.1f}%</td>
    </tr>
    """

    for _, row in group_df.iterrows():
        html_content += f"""
        <tr>
            <td></td>
            <td>{row['Squadron_Name']}</td>
            <td>{row['Compliant']}</td>
            <td>{row['Members_with_Valid_TLC']}</td>
            <td>{row['Total_Members']}</td>
            <td></td>

# Final app.py file content with all features
# You will need to paste your existing logic above this (loading and preparing unit_counts and group_summary)

# Imports
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from xhtml2pdf import pisa

# Use existing `unit_counts` and `group_summary` built from uploaded CSV

# === Compute group-level bar chart ===
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(group_summary["Group"], group_summary["Members_with_Valid_TLC"], color="skyblue")
ax.set_xlabel("Group")
ax.set_ylabel("Valid TLC Completions")
ax.set_title("TLC Completions by Group")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

chart_buf = BytesIO()
fig.savefig(chart_buf, format="png")
chart_data = base64.b64encode(chart_buf.getvalue()).decode("utf-8")
plt.close(fig)

timestamp = datetime.now().strftime("%B %d, %Y %I:%M %p")

html_string = f"""
<style>
    table, th, td {{
        border: 3px solid black;
        border-collapse: collapse;
        padding: 6px;
        font-size: 13px;
    }}
    th {{
        background-color: #f2f2f2;
    }}
    .group-row {{
        background-color: #e0e0e0;
        font-weight: bold;
    }}
</style>
"""
    th {{
        background-color: #f2f2f2;
    }}
    .group-row {{
        background-color: #e0e0e0;
        font-weight: bold;
    }}
    .compliant {{
        background-color: #d4edda;
    }}
    .non-compliant {{
        background-color: #f8d7da;
    }}
</style>
<div style='text-align: center;'>
    <img src='https://raw.githubusercontent.com/mcks0120/nywg-tlc/main/298903439_5485841021479213_274053999167640142_n.png' width='120'/>
    <h2 style='margin-bottom: 0;'>NYWG Training Leader of Cadets</h2>
    <h4 style='margin-top: 4px;'>Subordinate Unit Compliance</h4>
</div><br>
<div style='text-align: center; margin-top: 20px;'>
    <img src='data:image/png;base64,{chart_data}' width='600'/>
</div>
<br>
<table>
    <tr>
        <th>Group</th>
        <th>Squadron</th>
        <th>Compliant?</th>
        <th>Valid TLC</th>
        <th>Total Members</th>
        <th>% Group</th>
    </tr>
"""

for group in unit_counts["Group"].unique():
    group_df = unit_counts[unit_counts["Group"] == group]
    group_row = group_summary[group_summary["Group"] == group].iloc[0]
    group_percent = group_row["Group_Percent_Compliant"]

    html_string += f"""
    <tr class='group-row'>
        <td>{group}</td><td colspan='4'></td><td>{group_percent:.1f}%</td>
    </tr>
    """

    for _, row in group_df.iterrows():
        css_class = "compliant" if row["Compliant"] == "Yes" else "non-compliant"
        html_string += f"""
        <tr class='{css_class}'>
            <td></td>
            <td>{row['Squadron_Name']}</td>
            <td>{row['Compliant']}</td>
            <td>{row['Members_with_Valid_TLC']}</td>
            <td>{row['Total_Members']}</td>
            <td></td>
        </tr>
        """

html_string += f"""
</table>
<p style='text-align: right; font-size: 12px; color: gray;'>Generated: {timestamp}</p>
"""

# Display in app
st.subheader("Printable Report Preview")
st.markdown(html_string, unsafe_allow_html=True)
st.info("To print or save this view as a PDF, use your browser’s Print feature (Ctrl+P or Cmd+P).")

def convert_html_to_pdf(source_html):
    output = BytesIO()
    pisa.CreatePDF(BytesIO(source_html.encode("utf-8")), dest=output)
    return output.getvalue()

pdf_bytes = convert_html_to_pdf(html_string)

st.download_button(
    label="Download Report as PDF",
    data=pdf_bytes,
    file_name="NYWG_TLC_Report.pdf",
    mime="application/pdf"
)
from io import BytesIO
from xhtml2pdf import pisa

st.subheader("Downloadable PDF Report")

# Build same HTML with color-coded compliance
styled_html = """
<style>
    table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 6px;
        font-size: 12px;
    }
    th { background-color: #f2f2f2; }
    .group-row {
        background-color: #e0e0e0;
        font-weight: bold;
    }
    .compliant { background-color: #d4edda; }  /* green */
    .noncompliant { background-color: #f8d7da; }  /* red */
</style>

<div style='text-align: center;'>
    <img src='https://raw.githubusercontent.com/mcks0120/nywg-tlc/main/298903439_5485841021479213_274053999167640142_n.png' width='120'/>
    <h2 style='margin-bottom: 0;'>NYWG Training Leader of Cadets</h2>
    <h4 style='margin-top: 4px;'>Subordinate Unit Compliance</h4>
</div>
<br>
<table>
    <tr>
        <th>Group</th>
        <th>Squadron</th>
        <th>Compliant?</th>
        <th>Valid TLC</th>
        <th>Total Members</th>
        <th>% Group</th>
    </tr>
"""

for group in unit_counts["Group"].unique():
    group_df = unit_counts[unit_counts["Group"] == group]
    group_row = group_summary[group_summary["Group"] == group].iloc[0]
    group_percent = group_row["Group_Percent_Compliant"]

    styled_html += f"""
    <tr class='group-row'>
        <td>{group}</td>
        <td colspan='4'></td>
        <td>{group_percent:.1f}%</td>
    </tr>
    """

    for _, row in group_df.iterrows():
        css_class = "compliant" if row["Compliant"] == "Yes" else "noncompliant"
        styled_html += f"""
        <tr class='{css_class}'>
            <td></td>
            <td>{row['Squadron_Name']}</td>
            <td>{row['Compliant']}</td>
            <td>{row['Members_with_Valid_TLC']}</td>
            <td>{row['Total_Members']}</td>
            <td></td>
        </tr>
        """

styled_html += "</table>"

# Convert HTML to PDF
def convert_html_to_pdf(source_html):
    output = BytesIO()
    pisa_status = pisa.CreatePDF(source_html, dest=output)
    return output if not pisa_status.err else None

pdf_output = convert_html_to_pdf(styled_html)

if pdf_output:
    st.download_button(
        label="Download PDF Report",
        data=pdf_output.getvalue(),
        file_name="TLC_Compliance_Report.pdf",
        mime="application/pdf"
    )
else:
    st.error("There was an error generating the PDF.")
