import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import math
import pyvista as pv

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
    #out_csv = os.path.join(base_path, "data\sonar_coordinates.csv")

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

    #merged.to_csv(out_csv, mode = 'a', index=False)

    # Define the grid resolution
    resolution = 1
    x_min, x_max = merged['ping_x'].min(), merged['ping_x'].max()
    y_min, y_max = merged['ping_y'].min(), merged['ping_y'].max()
    z_min, z_max = merged['ping_z'].min(), merged['ping_z'].max()

    # Initialize the occupancy grid
    grid_width = int((x_max - x_min) / resolution) + 1
    grid_height = int((y_max - y_min) / resolution) + 1
    grid_depth = int((z_max - z_min) / resolution) + 1
    occupancy_grid = np.zeros((grid_depth, grid_height, grid_width))

    # Update the grid based on the points in the DataFrame
    for index, row in merged.iterrows():
        x_idx = int((row['ping_x'] - x_min) / resolution)
        y_idx = int((row['ping_y'] - y_min) / resolution)
        z_idx = int((row['ping_z'] - z_min) / resolution)
        occupancy_grid[z_idx, y_idx, x_idx] = min(1, occupancy_grid[z_idx, y_idx, x_idx] + 0.1)  # Increment and cap at 1

    # Create a structured grid for visualization
    structured_grid = pv.UniformGrid()
    structured_grid.dimensions = np.array(occupancy_grid.shape) + 1
    structured_grid.spacing = (resolution, resolution, resolution)
    structured_grid.cell_arrays["values"] = occupancy_grid.flatten(order="F")

    # Plot the 3D occupancy grid
    plotter = pv.Plotter()
    plotter.add_volume(structured_grid, cmap="gray", opacity="sigmoid", shade=True)
    plotter.show_axes()
    plotter.show()

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

if __name__ == "__main__":
    main()