import pandas as pd
import numpy as np

# Load the CSV
data = r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-09-46\data\processed_combined_log_2025-05-21_19_09_46_V1.csv"
df = pd.read_csv(data)

# Convert pitch to radians for trig functions
df["pitch_rad"] = np.radians(df["camera_pitch"])

# Only process rows with valid ping_distance
mask = df["ping_distance"].notna()

df["ping_x"] = np.nan
df["ping_y"] = np.nan
df["ping_z"] = np.nan

# Compute components
# Horizontal component of ping
horizontal_ping = df.loc[mask, "ping_distance"] * np.cos(df.loc[mask, "pitch_rad"])
# Vertical component of ping
vertical_ping = df.loc[mask, "ping_distance"] * np.sin(df.loc[mask, "pitch_rad"])

# North-south (ping_x)
df.loc[mask, "ping_x"] = df.loc[mask, "total_forward"] + np.where(
    df.loc[mask, "heading"] == 0,
    horizontal_ping,
    -horizontal_ping
)

# West-east (ping_y)
df.loc[mask, "ping_y"] = df.loc[mask, "total_right"]

# Depth (ping_z)
df.loc[mask, "ping_z"] = df.loc[mask, "negative_depth"] + vertical_ping

# Drop helper column
df.drop(columns=["pitch_rad"], inplace=True)

# Save updated CSV
df.to_csv(data, index=False)

print("Ping position mapping complete. Updated data saved.")