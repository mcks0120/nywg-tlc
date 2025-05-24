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
        </tr>
        """

html_content += "</table>"

st.markdown(html_content, unsafe_allow_html=True)
