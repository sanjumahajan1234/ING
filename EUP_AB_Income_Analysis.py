import sqlite3
import pandas as pd

db_path     = r"C:\Users\GJ02DU\OneDrive - ING\Documents\ABCD\DatabaseABCDapr26.db"
output_path = r"C:\Users\GJ02DU\OneDrive - ING\Documents\EUP_AB_Income_Analysis.xlsx"

grids = [
    '36019632','37620268','36121674','50575376','48836581','50583585',
    '38552594','36391737','36481420','36046278','36079341'
]

# Full year = December row (YTD cumulative). 2026 = 202604 YTD.
full_year_periods = ['201912','202012','202112','202212','202312','202412','202512']
ytd_period        = '202604'
all_periods       = full_year_periods + [ytd_period]

grid_ph   = ','.join('?' * len(grids))
period_ph = ','.join('?' * len(all_periods))

q = f"""
SELECT
    [Client EC UP Grid ID]                 AS grid,
    [Client EC UP Legal Name]              AS name,
    [Client EC UP Sector Name]             AS sector,
    [Client EC UP Region Name]             AS region,
    [Client EC UP Country Name]            AS country,
    [ABCD]                                 AS abcd,
    [Year Month]                           AS ym,
    SUM([Total Income YTD (excl org rev)]) AS income
FROM VR_data
WHERE CAST([Client EC UP Grid ID] AS TEXT) IN ({grid_ph})
  AND [ABCD]       IN ('A','B1','B2')
  AND [Year Month] IN ({period_ph})
GROUP BY
    [Client EC UP Grid ID],
    [Client EC UP Legal Name],
    [Client EC UP Sector Name],
    [Client EC UP Region Name],
    [Client EC UP Country Name],
    [ABCD],
    [Year Month]
"""

con = sqlite3.connect(db_path)
df  = pd.read_sql_query(q, con, params=grids + all_periods)
con.close()

print(f"Rows returned: {len(df)}")

# label periods
label_map = {
    '201912':'FY2019','202012':'FY2020','202112':'FY2021',
    '202212':'FY2022','202312':'FY2023','202412':'FY2024',
    '202512':'FY2025','202604':'2026 YTD (Apr)'
}
df['period_label'] = df['ym'].astype(str).map(label_map)

col_order = ['FY2019','FY2020','FY2021','FY2022','FY2023','FY2024','FY2025','2026 YTD (Apr)']

# pivot income wide
income_wide = (
    df.pivot_table(
        index=['grid','name','sector','region','country','abcd'],
        columns='period_label',
        values='income',
        aggfunc='sum'
    )
    .reindex(columns=col_order)
    .reset_index()
)

# preserve original grid order
order = {g: i for i, g in enumerate(grids)}
income_wide = (
    income_wide
    .assign(_o=income_wide['grid'].astype(str).map(order))
    .sort_values('_o')
    .drop(columns='_o')
    .reset_index(drop=True)
)

income_wide.to_excel(output_path, index=False)
print(f"\nDone — {len(income_wide)} rows written to:")
print(output_path)
