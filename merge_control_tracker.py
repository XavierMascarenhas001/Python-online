import pandas as pd
from tkinter import Tk, filedialog

# -----------------------------
# FILE SELECTION
# -----------------------------
root = Tk()
root.withdraw()

aggregated_file = filedialog.askopenfilename(title="Select CF_aggregated.parquet")
tracker_file = filedialog.askopenfilename(title="Select Project Tracker.parquet")
misc_file = filedialog.askopenfilename(title="Select miscelaneous.parquet")

output_parquet_file = filedialog.asksaveasfilename(
    title="Save Master Parquet",
    defaultextension=".parquet"
)

# -----------------------------
# LOAD DATA
# -----------------------------
agg_df = pd.read_parquet(aggregated_file)
tracker_df = pd.read_parquet(tracker_file)
misc_df = pd.read_parquet(misc_file)

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------
for df in [agg_df, tracker_df, misc_df]:
    df.columns = df.columns.str.strip().str.lower()

# -----------------------------
# NORMALIZE KEYS
# -----------------------------
key_cols = ['shire', 'project', 'segmentcode']

for col in key_cols:
    if col in agg_df.columns:
        agg_df[col] = agg_df[col].astype(str).str.strip().str.lower()
    if col in tracker_df.columns:
        tracker_df[col] = tracker_df[col].astype(str).str.strip().str.lower()

# text normalization
if 'segment' in agg_df.columns:
    agg_df['segment'] = agg_df['segment'].astype(str).str.lower()

if 'job name' in tracker_df.columns:
    tracker_df['job name'] = tracker_df['job name'].astype(str).str.lower()

# ensure output columns exist
agg_df['pid'] = None
agg_df['po'] = None
agg_df['material_code'] = None

# -----------------------------
# GROUP TRACKER FOR FAST LOOKUP
# -----------------------------
tracker_groups = tracker_df.groupby(['shire', 'project', 'segmentcode'])

# -----------------------------
# MATCH PID + PO LOGIC
# -----------------------------
for i, row in agg_df.iterrows():

    key = (row.get('shire'), row.get('project'), row.get('segmentcode'))

    if key not in tracker_groups.groups:
        continue

    subset = tracker_groups.get_group(key)
    segment_text = str(row.get('segment', ''))

    for _, trow in subset.iterrows():

        job_name = str(trow.get('job name', '')).strip()

        if job_name and job_name in segment_text:
            agg_df.at[i, 'pid'] = trow.get('pid')
            agg_df.at[i, 'po'] = trow.get('po')
            break

# -----------------------------
# MATERIAL CODE FROM MISC FILE
# -----------------------------
if 'item' in agg_df.columns and 'column_1' in misc_df.columns and 'column_3' in misc_df.columns:

    agg_df['item'] = agg_df['item'].astype(str).str.strip().str.lower()
    misc_df['column_1'] = misc_df['column_1'].astype(str).str.strip().str.lower()

    item_to_column_k = misc_df.set_index('column_1')['column_3'].to_dict()
    item_to_column_2 = misc_df.set_index('column_1')['column_2'].to_dict()

    agg_df['material_code'] = agg_df['item'].map(item_to_column_k)
    agg_df['MD Poling'] = agg_df['item'].map(item_to_column_2)

# -----------------------------
# FINAL COLUMN ORDER FIX
# -----------------------------
def move_before(df, target, before):
    cols = list(df.columns)
    if target in cols and before in cols:
        cols.remove(target)
        idx = cols.index(before)
        cols.insert(idx, target)
        return df[cols]
    return df

# ensure correct order: material_code before PID and PO
agg_df = move_before(agg_df, 'material_code', 'pid')
agg_df = move_before(agg_df, 'po', 'pid')
cols = [c for c in agg_df.columns if c != 'MD Poling'] + ['MD Poling']
agg_df = agg_df[cols]

# -----------------------------
# SAVE OUTPUTS
# -----------------------------
agg_df.to_parquet(output_parquet_file, index=False)
agg_df.to_excel(output_parquet_file.replace(".parquet", ".xlsx"), index=False)

print("Done!")
