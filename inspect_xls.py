import pandas as pd
import sys

try:
    f = "backend/test_dump.xlsx"
    xls = pd.ExcelFile(f)
    print(f"Sheets: {xls.sheet_names}")
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"Sheet '{sheet}': {len(df)} rows")
except Exception as e:
    print(e)
