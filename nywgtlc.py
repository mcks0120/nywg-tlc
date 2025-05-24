import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO

# === Embedded Unit-to-Squadron Mapping ===
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

# === Streamlit UI ===
st.title("TLC Validity Report Generator")

uploaded_file = st.file_uploader("Upload TLC_Progression CSV file", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Convert TLC completion dates
        df["BasicCompleted_Date"] = pd.to_datetime(df["BasicCompleted"], errors='coerce')
        df["IntCompleted_Date"] = pd.to_datetime(df["IntCompleted"], errors='coerce')
        cutoff_date = datetime.now() - timedelta(days=4 * 365)
        latest_date = pd.concat([df["BasicCompleted_Date"], df["IntCompleted_Date"]]).max()

        # Determine valid TLC
        df["Valid_TLC"] = (
            (df["BasicCompleted_Date"] >= cutoff_date) |
            (df["IntCompleted_Date"] >= cutoff_date)
        )

        # Filter valid members and count per unit
        valid_df = df[df["Valid_TLC"]].drop_duplicates(subset=["Organization", "CAPID"])
        unit_counts = valid_df.groupby("Organization")["CAPID"].nunique().reset_index()
        unit_counts.columns = ["Unit", "Members_with_Valid_TLC"]

        # Map squadron names
        unit_counts["Squadron_Name"] = unit_counts["Unit"].map(lambda x: squadron_map.get(x.strip(), "Unknown Unit"))

        # Add compliance flag
        unit_counts["Compliant"] = unit_counts["Members_with_Valid_TLC"].apply(lambda x: "Yes" if x >= 2 else "No")

        # Reorder columns
        unit_counts = unit_counts[["Unit", "Squadron_Name", "Members_with_Valid_TLC", "Compliant"]]

        # Exclude HQ, GROUP, SENIOR units
        unit_counts = unit_counts[~unit_counts["Squadron_Name"].str.contains("GROUP|SENIOR|HQ", case=False, na=False)]

        # Compliance stats
        total_compliant = (unit_counts["Compliant"] == "Yes").sum()
        total_non_compliant = (unit_counts["Compliant"] == "No").sum()

        # Display summary
        st.subheader("TLC Compliance Summary")
        st.markdown(f"**As of Date:** {latest_date.strftime('%B %d, %Y')}")
        st.markdown(f"**Total Compliant Units:** {total_compliant}")
        st.markdown(f"**Total Non-Compliant Units:** {total_non_compliant}")

        st.subheader("Detailed Unit Report")
        st.dataframe(unit_counts)

        # Download as Excel
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
