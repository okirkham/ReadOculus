import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def main():
    # base path of 
    base_path = r"C:\Users\0w3nk\Documents\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-02-07_14-19-17"

    # dead reckoning file
    deadReckoningFolder = "data\peripheral\dvl_deadreckoning_log.csv"

    deadReckoningPath = os.path.join(base_path, deadReckoningFolder)

    deadReckoning = pd.read_csv(deadReckoningPath, encoding = "utf-8", sep=',')

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

    merged['combined_bearing'] = merged.apply(lambda row: add_bearings(row['bearing'], row['heading (°)']), axis=1)

    # Apply the function to each row and assign the result to the DataFrame
    merged[['ping_x', 'ping_y', 'ping_z']] = merged.apply(calculate_cartesian_coordinates, axis=1)

    coords = pointProbability(merged)

    print(coords)

    filtered_points = coords[coords['probability'] >= 1]

    # Extract x, y, and z coordinates
    x = filtered_points['ping_x']
    y = filtered_points['ping_y']
    z = filtered_points['ping_z']

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

# oculus file
def find_csv(path):
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if file_name.endswith(".csv"):
            return file_name
        

def add_bearings(bearing1, bearing2): 
    result = (bearing1 + bearing2) % 360 
    if result < 0: 
        result += 360 
    
    return result

def round_to_nearest_half_meter(value):
    return round(value * 2) / 2

def calculate_cartesian_coordinates(row):
    # Extract values for a single row
    x, y, z = row['x (m)'], row['y (m)'], row['z (m)']
    heading, pitch, roll = row['heading (°)'], row['pitch (°)'], row['roll (°)']
    distance = row['distance']
        
    # Convert angles from degrees to radians
    heading_rad = np.radians(heading)
    pitch_rad = np.radians(pitch)
    roll_rad = np.radians(roll)
        
    # Rotation matrix for heading (yaw)
    R_heading = np.array([
        [np.cos(heading_rad), -np.sin(heading_rad), 0],
        [np.sin(heading_rad), np.cos(heading_rad), 0],
        [0, 0, 1]
    ])
        
    # Rotation matrix for pitch
    R_pitch = np.array([
        [np.cos(pitch_rad), 0, np.sin(pitch_rad)],
        [0, 1, 0],
        [-np.sin(pitch_rad), 0, np.cos(pitch_rad)]
    ])
        
    # Rotation matrix for roll
    R_roll = np.array([
        [1, 0, 0],
        [0, np.cos(roll_rad), -np.sin(roll_rad)],
        [0, np.sin(roll_rad), np.cos(roll_rad)]
    ])
        
    # Combined rotation matrix
    R_combined = R_heading @ R_pitch @ R_roll
        
    # Direction vector of the sonar ping in local coordinates (x = 0, y = 0, z = -distance along z-axis)
    direction_local = np.array([0, 0, -distance])  # Assume the ping starts directly along the z-axis
        
    # Rotate the direction vector by the combined rotation matrix
    direction_rotated = R_combined @ direction_local
        
    # Add the sonar's position to the rotated direction to get the final ping coordinates
    ping_coordinates = np.array([x, y, z]) + direction_rotated
        
    # Return the ping coordinates as a Series
    return pd.Series(ping_coordinates)

def pointProbability(df):
    # Round the coordinates
    df['ping_x'] = df['ping_x'].apply(round_to_nearest_half_meter)
    df['ping_y'] = df['ping_y'].apply(round_to_nearest_half_meter)
    df['ping_z'] = df['ping_z'].apply(round_to_nearest_half_meter)

    # Add the probability column with default value 0
    df['probability'] = 0

    # Check for duplicate coordinates and add 1 to probability for each duplicate
    duplicates = df.duplicated(subset=['ping_x', 'ping_y', 'ping_z'], keep=False)
    df.loc[duplicates, 'probability'] += 1

    # Remove duplicates keeping the first occurrence
    df = df.drop_duplicates(subset=['ping_x', 'ping_y', 'ping_z'])

    return df[['ping_x', 'ping_y', 'ping_z', 'probability']]

if __name__ == "__main__":
    main()