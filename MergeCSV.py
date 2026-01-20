import pandas as pd

# --- Load both CSVs ---
large_df = pd.read_csv(r"c:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06\data\DepthProfilePoints_2025-05-21_12_42-06.CSV")
small_df = pd.read_csv(r"c:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06\data\processed_combined_log_2025-05-21_19-42-06.csv")

# --- Identify shared columns ---
shared_cols = list(set(large_df.columns) & set(small_df.columns))

# --- Filter small_df to only rows with complete data in shared columns ---
filtered_small = small_df[shared_cols].dropna(how='any')

# --- Merge: append filtered rows to large_df (shared columns only) ---
merged_df = pd.concat([large_df[shared_cols], filtered_small], ignore_index=True)

# --- Save to new CSV ---
merged_df.to_csv(r"c:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06\data\DepthProfilePoints_mergedV1.CSV", index=False)
print("Merged CSV saved with only shared columns.")