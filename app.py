
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from fpdf import FPDF
import io

st.set_page_config(page_title="NYWG TLC Compliance Checker", layout="wide")
st.title("Civil Air Patrol - NYWG TLC Compliance Checker")

uploaded_file = st.file_uploader("Upload TLC Progression CSV", type=["csv"])

if uploaded_file is not None:
    tlc = pd.read_csv(uploaded_file)
    st.success("CSV successfully uploaded and processed.")

    cutoff = datetime.now() - timedelta(days=4 * 365)

    # Convert date columns
    tlc["OnDemand_Date"] = pd.to_datetime(tlc["OnDemandCompleted"], errors='coerce')
    tlc["Basic_Date"] = pd.to_datetime(tlc["BasicCompleted"], errors='coerce')
    tlc["Intermediate_Date"] = pd.to_datetime(tlc["IntCompleted"], errors='coerce')
    tlc["Advanced_Date"] = pd.to_datetime(tlc["AdvCompleted"], errors='coerce')

    tlc["TLC_Valid"] = (
        (tlc["OnDemand_Date"] >= cutoff) |
        (tlc["Basic_Date"] >= cutoff) |
        (tlc["Intermediate_Date"] >= cutoff) |
        (tlc["Advanced_Date"] >= cutoff)
    )

    unit_reference_data = [
    {'Group': 'hq', 'Unit Name': 'NY Wing HQ Squadron, inactive', 'Unit Type': 'comp', 'Unit Number': 'NY-000'},
    ...
]
    units = pd.DataFrame(unit_reference_data)
    units["Unit Type"] = units["Unit Type"].str.lower().str.strip()

    eligible_units = units[units["Unit Type"].isin({"cadet", "composite", "flight"})]
    valid_counts = tlc[tlc["TLC_Valid"]].groupby("Organization")["CAPID"].nunique().reset_index()
    valid_counts.columns = ["Unit Number", "Valid TLC Count"]

    report = eligible_units.merge(valid_counts, on="Unit Number", how="left")
    report["Valid TLC Count"] = report["Valid TLC Count"].fillna(0).astype(int)
    report["Compliance"] = report["Valid TLC Count"].apply(lambda x: "Compliant" if x >= 2 else "Non-Compliant")

    st.dataframe(report)

    # CSV Export
    csv = report.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV Report",
        data=csv,
        file_name="NYWG_TLC_Compliance_Report.csv",
        mime="text/csv"
    )

    # PDF Export
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "CAP TLC Compliance Report", ln=True, align="C")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

        def create_table(self, dataframe):
            self.set_font("Arial", "", 10)
            col_widths = [30, 60, 30, 30, 30]
            for i, col in enumerate(dataframe.columns):
                width = 30 if i >= len(col_widths) else col_widths[i]
                self.cell(width, 8, str(col), border=1, align="C")
            self.ln()
            col_widths = [30, 60, 30, 30, 30]
            for _, row in dataframe.iterrows():
                self.cell(col_widths[0], 8, str(row["Group"]), border=1)
                self.cell(col_widths[1], 8, str(row["Unit Name"]), border=1)
                self.cell(col_widths[2], 8, str(row["Unit Number"]), border=1)
                self.cell(col_widths[3], 8, str(row["Valid TLC Count"]), border=1, align="C")
                self.cell(col_widths[4], 8, str(row["Compliance"]), border=1, align="C")
                self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.create_table(report)

    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name="NYWG_TLC_Compliance_Report.pdf",
        mime="application/pdf"
    )
