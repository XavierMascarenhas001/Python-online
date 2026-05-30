import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# Hide root Tkinter window
root = tk.Tk()
root.withdraw()

# Select input Excel file
file_path = filedialog.askopenfilename(
    title="Select Excel File",
    filetypes=[("Excel files", "*.xlsx")]
)

if not file_path:
    raise Exception("No file selected.")

# Sheets to process
sheets = ["Ayrshire", "Lanark", "Glasgow"]

# Columns we want (by name)
columns_needed = {
    "Scope": "Scope",
    "Job Name": "job name",
    "Circuit": "Circuit",
    "Control File": "Control file",
    "PID": "PID",
    "PO": "PO"
}

all_data = []

for sheet in sheets:
    try:
        df = pd.read_excel(file_path, sheet_name=sheet, header=1)

        df.columns = df.columns.str.strip()

        selected_cols = {}
        for col in df.columns:
            col_lower = col.lower()
            for key, val in columns_needed.items():
                if val.lower() == col_lower:
                    selected_cols[col] = key

        df = df[list(selected_cols.keys())]
        df.rename(columns=selected_cols, inplace=True)

        # Rename columns as requested
        df.rename(columns={
            "Scope": "Project",
            "Circuit": "SegmentCode"
        }, inplace=True)

        # Add shire column (lowercase)
        df["shire"] = sheet

        all_data.append(df)

    except Exception as e:
        print(f"Skipping sheet {sheet}: {e}")

final_df = pd.concat(all_data, ignore_index=True)

# Fix Parquet type issues
# Fix Parquet type issues
for col in final_df.columns:
    if final_df[col].dtype == "object":
        final_df[col] = final_df[col].astype("string")

# 👉 Move "shire" to first column
cols = list(final_df.columns)
cols.insert(0, cols.pop(cols.index("shire")))
final_df = final_df[cols]

# Select output folder
output_folder = filedialog.askdirectory(title="Select Output Folder")

if not output_folder:
    raise Exception("No output folder selected.")

# Output paths (renamed to workbank)
excel_output = os.path.join(output_folder, "workbank.xlsx")
parquet_output = os.path.join(output_folder, "workbank.parquet")

# Save files
final_df.to_excel(excel_output, index=False)
final_df.to_parquet(parquet_output, index=False)

print("Files saved successfully!")
print(f"Excel: {excel_output}")
print(f"Parquet: {parquet_output}")
