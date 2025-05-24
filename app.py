
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
    {'Group': None, 'Unit Name': 'NY Wing HQ Squadron, inactive', 'Unit Type': 'comp', 'Unit Number': 'NY-000'},
    {'Group': None, 'Unit Name': 'New York State Legislative Squadron', 'Unit Type': 'senior', 'Unit Number': 'NY-999'},
    {'Group': 'CMG', 'Unit Name': 'Catskill Mountain Group', 'Unit Type': 'group', 'Unit Number': 'NY-035'},
    {'Group': 'CMG', 'Unit Name': 'Orange County Cadet', 'Unit Type': 'cadet', 'Unit Number': 'NY-030'},
    {'Group': 'CMG', 'Unit Name': 'Rockland Cadet', 'Unit Type': 'cadet', 'Unit Number': 'NY-072'},
    {'Group': 'CMG', 'Unit Name': 'Dutchess County Cadet', 'Unit Type': 'cadet', 'Unit Number': 'NY-159'},
    {'Group': 'CMG', 'Unit Name': 'Sullivan County ', 'Unit Type': 'cadet', 'Unit Number': 'NY-387'},
    {'Group': 'CMG', 'Unit Name': 'Ulster County Flight (to NY-030)', 'Unit Type': 'flight', 'Unit Number': 'NY-395'},
    {'Group': 'CMG', 'Unit Name': 'Orange County Senior*', 'Unit Type': 'senior', 'Unit Number': 'NY-413'},
    {'Group': 'CMG', 'Unit Name': 'Dutchess County Senior (to NY-413)', 'Unit Type': 'flight*', 'Unit Number': 'NY-421'},
    {'Group': 'CMG', 'Unit Name': 'Central New York Group', 'Unit Type': 'group', 'Unit Number': 'NY-134'},
    {'Group': 'CMG', 'Unit Name': 'Lt Col William J. Shafer Cadet', 'Unit Type': 'cadet', 'Unit Number': 'NY-135'},
    {'Group': 'CMG', 'Unit Name': 'Mohawk Griffiss Senior Squadron', 'Unit Type': 'senior', 'Unit Number': 'NY-156'},
    {'Group': 'CMG', 'Unit Name': 'Utica Cadet Squadron        (Rome)', 'Unit Type': 'cadet', 'Unit Number': 'NY-162'},
    {'Group': 'CMG', 'Unit Name': 'Tri-County Flight **', 'Unit Type': 'flight', 'Unit Number': 'NY-189'},
    {'Group': 'CMG', 'Unit Name': 'Southern Tier Cadet Squadron', 'Unit Type': 'cadet', 'Unit Number': 'NY-292'},
    {'Group': 'CMG', 'Unit Name': 'Fort Drum Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-406'},
    {'Group': 'CMG', 'Unit Name': 'F.R. Sussey Composite Squadron, Fulton', 'Unit Type': 'comp', 'Unit Number': 'NY-408'},
    {'Group': 'CMG', 'Unit Name': 'Finger Lakes Group', 'Unit Type': 'group', 'Unit Number': 'NY-109'},
    {'Group': 'CMG', 'Unit Name': 'Newark Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-111'},
    {'Group': 'CMG', 'Unit Name': 'Canandaigua Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-212'},
    {'Group': 'CMG', 'Unit Name': 'Batavia Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-253'},
    {'Group': 'CMG', 'Unit Name': 'Rochester Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-273'},
    {'Group': 'CMG', 'Unit Name': 'Twin Tiers Cadet (Chemung/Schuyler)', 'Unit Type': 'cadet', 'Unit Number': 'NY-283'},
    {'Group': 'CMG', 'Unit Name': 'Condor', 'Unit Type': 'comp', 'Unit Number': 'NY-354'},
    {'Group': 'CMG', 'Unit Name': 'Rochester Senior', 'Unit Type': 'senior', 'Unit Number': 'NY-412'},
    {'Group': 'CMG', 'Unit Name': 'Long Island Group', 'Unit Type': 'group', 'Unit Number': 'NY-251'},
    {'Group': 'CMG', 'Unit Name': 'Col Francis S. Gabreski', 'Unit Type': 'cadet', 'Unit Number': 'NY-117'},
    {'Group': 'CMG', 'Unit Name': 'Leroy R. Grumman Cadet Squadron ', 'Unit Type': 'cadet', 'Unit Number': 'NY-153'},
    {'Group': 'CMG', 'Unit Name': 'Long Island Senior', 'Unit Type': 'senior', 'Unit Number': 'NY-207'},
    {'Group': 'CMG', 'Unit Name': 'Brian M. Mooney', 'Unit Type': 'cadet', 'Unit Number': 'NY-247'},
    {'Group': 'CMG', 'Unit Name': 'Lt Quentin Roosevelt Cadet', 'Unit Type': 'cadet', 'Unit Number': 'NY-288'},
    {'Group': 'CMG', 'Unit Name': '9th Suffolk Cadet Squadron', 'Unit Type': 'cadet', 'Unit Number': 'NY-311'},
    {'Group': 'CMG', 'Unit Name': 'Suffolk Cadet Squadron 10 ', 'Unit Type': 'cadet', 'Unit Number': 'NY-328'},
    {'Group': 'CMG', 'Unit Name': 'The Spirit of Tuskegee', 'Unit Type': 'cadet', 'Unit Number': 'NY-332'},
    {'Group': 'MEG', 'Unit Name': 'Mid-Eastern Group', 'Unit Type': 'group', 'Unit Number': 'NY-043'},
    {'Group': 'MEG', 'Unit Name': 'Schenectady Composite Squadron', 'Unit Type': 'comp', 'Unit Number': 'NY-073'},
    {'Group': 'MEG', 'Unit Name': 'Albany Senior Squadron', 'Unit Type': 'senior', 'Unit Number': 'NY-361'},
    {'Group': 'MEG', 'Unit Name': "James P. O'Conner Composite", 'Unit Type': 'comp', 'Unit Number': 'NY-388'},
    {'Group': 'MEG', 'Unit Name': 'Vanguard Composite Squadron', 'Unit Type': 'comp', 'Unit Number': 'NY-390'},
    {'Group': 'MEG', 'Unit Name': 'Vedder Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-392'},
    {'Group': 'MEG', 'Unit Name': 'Capt Luke C. Wullenwaber Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-415'},
    {'Group': 'MEG', 'Unit Name': 'New York City Group', 'Unit Type': 'group', 'Unit Number': 'NY-015'},
    {'Group': 'MEG', 'Unit Name': 'Bronx Cadet Squadron', 'Unit Type': 'cadet', 'Unit Number': 'NY-089'},
    {'Group': 'MEG', 'Unit Name': 'Academy', 'Unit Type': 'cadet', 'Unit Number': 'NY-147'},
    {'Group': 'MEG', 'Unit Name': 'Phoenix', 'Unit Type': 'comp', 'Unit Number': 'NY-301'},
    {'Group': 'MEG', 'Unit Name': 'Southern Tier Flight  (deactivated 22Jun)', 'Unit Type': 'flight', 'Unit Number': 'NY-414'},
    {'Group': 'MEG', 'Unit Name': 'Floyd Bennett', 'Unit Type': 'comp', 'Unit Number': 'NY-373'},
    {'Group': 'MEG', 'Unit Name': 'Falcon Senior', 'Unit Type': 'senior', 'Unit Number': 'NY-379'},
    {'Group': 'MEG', 'Unit Name': 'Brooklyn Tech Cadet Squadron #1', 'Unit Type': 'cadet', 'Unit Number': 'NY-384'},
    {'Group': 'MEG', 'Unit Name': 'Lt Vincent R. Capodanno Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-420'},
    {'Group': 'MEG', 'Unit Name': 'Bronx Aerospace Cadet Flight', 'Unit Type': 'flight', 'Unit Number': 'NY-423'},
    {'Group': 'MEG', 'Unit Name': 'Brooklyn Senior Squadron', 'Unit Type': 'senior', 'Unit Number': 'NY-613'},
    {'Group': 'MEG', 'Unit Name': 'Western New York', 'Unit Type': 'group', 'Unit Number': 'NY-024'},
    {'Group': 'MEG', 'Unit Name': 'Southtowns Cadet Squadron', 'Unit Type': 'cadet', 'Unit Number': 'NY-020'},
    {'Group': 'MEG', 'Unit Name': 'Buffalo Composite Squadron #1', 'Unit Type': 'comp', 'Unit Number': 'NY-022'},
    {'Group': 'MEG', 'Unit Name': 'Niagara Falls Composite Squadron', 'Unit Type': 'comp', 'Unit Number': 'NY-116'},
    {'Group': 'MEG', 'Unit Name': 'TAK Composite Squadron', 'Unit Type': 'comp', 'Unit Number': 'NY-173'},
    {'Group': 'MEG', 'Unit Name': 'Niagara Frontier Senior Squadron', 'Unit Type': 'flight', 'Unit Number': 'NY-343'},
    {'Group': 'MEG', 'Unit Name': 'Dunkirk Composite Squadron', 'Unit Type': 'comp', 'Unit Number': 'NY-351'},
    {'Group': 'MEG', 'Unit Name': 'Jamestown Composite Squadron', 'Unit Type': 'comp', 'Unit Number': 'NY-402'},
    {'Group': 'MEG', 'Unit Name': 'Buffalo Creek Academy Cadet Sq', 'Unit Type': 'cadet', 'Unit Number': 'NY-824'},
    {'Group': 'MEG', 'Unit Name': 'South Eastern Group', 'Unit Type': 'group', 'Unit Number': 'NY-118'},
    {'Group': 'MEG', 'Unit Name': 'Putnam County Composite', 'Unit Type': 'comp', 'Unit Number': 'NY-033'},
    {'Group': 'MEG', 'Unit Name': 'Westchester Cadet Squadron 1', 'Unit Type': 'cadet', 'Unit Number': 'NY-048'},
    {'Group': 'MEG', 'Unit Name': 'Westchester Hudson Senior', 'Unit Type': 'senior', 'Unit Number': 'NY-219'},
    {'Group': 'MEG', 'Unit Name': 'Col Johnnie Pantanelli Composite ', 'Unit Type': 'comp', 'Unit Number': 'NY-238'},
    {'Group': 'MEG', 'Unit Name': 'Lt Anthony L. Willsea Cadet ', 'Unit Type': 'cadet', 'Unit Number': 'NY-422'},
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
