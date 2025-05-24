unit_counts["Squadron_Name"] = unit_counts["Unit"].map(lambda x: squadron_map.get(x.strip(), "Unknown Unit"))
unit_counts["Compliant"] = unit_counts["Members_with_Valid_TLC"].apply(lambda x: "Yes" if x >= 2 else "No")
unit_counts = unit_counts[["Unit", "Squadron_Name", "Members_with_Valid_TLC", "Compliant"]]

# Exclude "Group", "Senior", and "HQ" units
unit_counts = unit_counts[~unit_counts["Squadron_Name"].str.contains("GROUP|SENIOR|HQ", case=False, na=False)]

# Compliance totals
total_compliant = (unit_counts["Compliant"] == "Yes").sum()
total_non_compliant = (unit_counts["Compliant"] == "No").sum()

# Display
st.subheader("TLC Compliance Summary")
st.markdown(f"**As of Date:** {latest_date.strftime('%B %d, %Y')}")
st.markdown(f"**Total Compliant Units:** {total_compliant}")
st.markdown(f"**Total Non-Compliant Units:** {total_non_compliant}")

st.subheader("Detailed Unit Report")
st.dataframe(unit_counts)

# Export
output = BytesIO()
unit_counts.to_excel(output, index=False)
st.download_button(
    label="Download Excel Report",
    data=output.getvalue(),
    file_name="tlc_compliance_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
