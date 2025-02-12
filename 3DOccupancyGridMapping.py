import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import math

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

    # out_csv
    out_csv = os.path.join(base_path, "data\sonar_coordinates.csv")

    # add heading data to dead reckoning file
    data_column = combined[['timestamp', 'heading (°)']]

    deadReckoningCombined= pd.merge(deadReckoning, data_column, on='timestamp', how='left')
                        
    # merge dead reckoning file and oculus csv file based on time stamp
    columns_to_keep = ['timestamp', 'x (m)', 'y (m)', 'z (m)', 'roll (°)', 'pitch (°)', 'heading (°)']
    xyz = deadReckoningCombined[columns_to_keep]
    xyz = xyz.copy()
    xyz['timestamp'] = pd.to_datetime(xyz['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')
    oculus_csv['timestamp'] = pd.to_datetime(oculus_csv['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')

    merged = pd.merge_asof(oculus_csv, xyz, on='timestamp', tolerance=pd.Timedelta('50ms'), direction='nearest')

    merged = merged.dropna(subset=['x (m)'])

    # Apply the function to each row and assign the result to the DataFrame
    merged[['ping_x', 'ping_y', 'ping_z']] = merged.apply(compute_sonar_ping, axis=1)

    coords = pointProbability(merged)

    coords.to_csv(out_csv, mode = 'a', index=False)

    filtered_points = coords[coords['probability'] >= 1]

    # Extract x, y, and z coordinates
    x = filtered_points['ping_x']
    y = filtered_points['ping_y']
    z = filtered_points['ping_z']

    #rov position
    x_rov = coords['x (m)']
    y_rov = coords['y (m)']
    z_rov = coords['z (m)']

    # Plot points
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='b', marker='o')
    ax.scatter(x_rov, y_rov, z_rov, c='r', marker='o')

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
        
def round_to_nearest_half_meter(value):
    return round(value * 2) / 2

def compute_beam_pitch_and_heading(initial_pitch, roll, beam_bearing, initial_heading):
    # Convert degrees to radians
    pitch_rad = math.radians(initial_pitch)
    roll_rad = math.radians(roll)
    bearing_rad = math.radians(beam_bearing)
    
    # Compute new pitch angle
    new_pitch_rad = math.atan(math.tan(pitch_rad) * math.cos(roll_rad) + math.tan(roll_rad) * math.sin(bearing_rad))
    new_pitch = math.degrees(new_pitch_rad)
    
    # Compute new bearing angle
    if roll == 0:
        new_bearing = beam_bearing  # No change if roll is zero
    else:
        new_bearing_rad = math.atan(math.sin(bearing_rad) / math.cos(roll_rad))
        new_bearing = math.degrees(new_bearing_rad)
    
    # Compute new absolute heading
    new_heading = (initial_heading + new_bearing) % 360
    
    return new_pitch, new_heading


def rotation_matrix(heading, pitch, roll):
    """Compute the 3D rotation matrix from heading, pitch, and roll (in degrees)
    
    """
    # Convert degrees to radians
    heading = np.radians(heading)
    pitch = np.radians(pitch)  # Negate pitch to correct for coordinate system
    roll = np.radians(roll)

    # Rotation matrices
    R_y = np.array([
        [np.cos(heading), -np.sin(heading), 0],
        [np.sin(heading),  np.cos(heading), 0],
        [0, 0, 1]
    ])

    R_r = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    R_p = np.array([
        [np.cos(pitch), 0, -np.sin(pitch)],  # <-- Fixed negative sign
        [0, 1, 0],
        [np.sin(pitch), 0, np.cos(pitch)]  # <-- Fixed sign
    ])

    # Apply rotations in the order Z * X * Y
    return  R_y @ R_p @ R_r

def compute_sonar_ping(row):
    """Compute the Cartesian coordinates of the sonar ping for a row in the DataFrame
    
    """

    bearing, heading, pitch, roll = row['bearing'], row['heading (°)'], row['pitch (°)'], row['roll (°)']
    x, y, z = row['x (m)'], row['y (m)'], row['z (m)']
    ping_distance = row['distance']

    new_pitch, new_heading = compute_beam_pitch_and_heading(pitch, roll, bearing, heading)

    r = rotation_matrix(new_heading, new_pitch, roll)

    ping_local = np.array([ping_distance, 0, 0])

    # Transform ping to global frame
    ping_global = r @ ping_local

    # Add sonar's position to get global coordinates
    ping_global += np.array([-x, y, z])

    return pd.Series({'ping_x': -1*ping_global[0], 'ping_y': ping_global[1], 'ping_z': ping_global[2]})

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

    return df

if __name__ == "__main__":
    main()