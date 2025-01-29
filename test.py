import pandas as pd

# Read CSV files
csv_a = pd.read_csv(r"C:\Users\0w3nk\OneDrive - Carleton University\January 29th, ROV Pool Tests\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\combined_log.csv")
csv_b = pd.read_csv(r"C:\Users\0w3nk\OneDrive - Carleton University\January 29th, ROV Pool Tests\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\peripheral\dvl_deadreckoning_log.csv")

# Select the column from CSV "A" that you want to join
# Assuming the column to join is named 'data_column'
#print(list(csv_a.columns))

data_column = csv_a[['timestamp', 'heading (°)']]

# Merge CSV "A" column with CSV "B" based on timestamps (treated as strings)
merged_csv = pd.merge(csv_b, data_column, on='timestamp', how='left')

# Save the merged result to a new CSV
merged_csv.to_csv(r"C:\Users\0w3nk\OneDrive - Carleton University\January 29th, ROV Pool Tests\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\merged_output.csv", index=False)
