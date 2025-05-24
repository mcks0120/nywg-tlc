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
        border: 1px solid black;
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
