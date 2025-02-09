import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# base path of 
base_path = r"C:\Users\0w3nk\Documents\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-02-07_14-19-17"

# dead reckoning file
deadReckoningFolder = "data\peripheral\dvl_deadreckoning_log.csv"

deadReckoningPath = os.path.join(base_path, deadReckoningFolder)

deadReckoning = pd.read_csv(deadReckoningPath, encoding = "utf-8", sep=',')

# oculus file
def find_csv(path):
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if file_name.endswith(".csv"):
            return file_name
        
sonar = os.path.join(base_path, "sonar")

csvFile = find_csv(sonar)

csvPath = os.path.join(base_path, "sonar", csvFile)

oculus_csv = pd.read_csv(csvPath, encoding = "utf-8", sep=',')

# combined log
combined_folder = "data\combined_log.csv"

combined_path = os.path.join(base_path, combined_folder)

combined = pd.read_csv(combined_path, encoding = "utf-8", sep=',')

# add heading data to dead reckoning file
data_column = combined[['timestamp', 'heading (°)']]

deadReckoningCombined= pd.merge(deadReckoning, data_column, on='timestamp', how='left')
                     
# merge dead reckoning file and oculus csv file based on time stamp
columns_to_keep = ['timestamp', 'x (m)', 'y (m)', 'z (m)', 'roll (°)', 'pitch (°)', 'heading (°)']
xyz = deadReckoningCombined[columns_to_keep]
xyz = xyz.copy()
xyz['timestamp'] = pd.to_datetime(xyz['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')
oculus_csv['timestamp'] = pd.to_datetime(oculus_csv['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')

merged = pd.merge_asof(oculus_csv, xyz, on='timestamp', tolerance=pd.Timedelta('250ms'), direction='nearest')

merged = merged.dropna(subset=['x (m)'])

def add_bearings(bearing1, bearing2): 
    result = (bearing1 + bearing2) % 360 
    if result < 0: 
        result += 360 
    
    return result

merged['combined_bearing'] = merged.apply(lambda row: add_bearings(row['bearing'], row['heading (°)']), axis=1)

def round_to_nearest_half_meter(value):
    return round(value * 2) / 2

def calculate_cartesian_coordinates(df):
    # Convert pitch, roll, and heading to radians
    df['pitch_rad'] = np.deg2rad(df['pitch (°)'])
    df['roll_rad'] = np.deg2rad(df["roll (°)"])
    df['heading_rad'] = np.deg2rad(df['combined_bearing'])

    # Calculate the Cartesian coordinates
    df['sonar_x'] = df["x (m)"] + df['distance'] * (
        np.cos(df['pitch_rad']) * np.cos(df['heading_rad'])
    )
    df['sonar_y'] = df['y (m)'] + df['distance'] * (
        np.cos(df['pitch_rad']) * np.sin(df['heading_rad'])
    )
    df['sonar_z'] = df['z (m)'] + df['distance'] * np.sin(df['pitch_rad'])

    # Round the coordinates
    df['sonar_x'] = df['sonar_x'].apply(round_to_nearest_half_meter)
    df['sonar_y'] = df['sonar_y'].apply(round_to_nearest_half_meter)
    df['sonar_z'] = df['sonar_z'].apply(round_to_nearest_half_meter)

    # Add the probability column with default value 0
    df['probability'] = 0

    # Check for duplicate coordinates and add 1 to probability for each duplicate
    duplicates = df.duplicated(subset=['sonar_x', 'sonar_y', 'sonar_z'], keep=False)
    df.loc[duplicates, 'probability'] += 1

    # Remove duplicates keeping the first occurrence
    df = df.drop_duplicates(subset=['sonar_x', 'sonar_y', 'sonar_z'])

    return df[['sonar_x', 'sonar_y', 'sonar_z', 'probability']]

coords = calculate_cartesian_coordinates(merged)

print(coords)

filtered_points = coords[coords['probability'] >= 1]

# Extract x, y, and z coordinates
x = filtered_points['sonar_x']
y = filtered_points['sonar_y']
z = filtered_points['sonar_z']

# Plot points
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z, c='b', marker='o')

# Set labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

ax.set_xlim([min(x) - 1, max(x) + 1])
ax.set_ylim([min(y) - 1, max(y) + 1])
ax.set_zlim([min(z) - 1, max(z) + 1])

# Show plot
plt.show()