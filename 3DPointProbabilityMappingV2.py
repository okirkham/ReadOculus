import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import math
import pyproj


def main():
    
    # out_csv
    out_csv = os.path.join(base_path, "data\sonar_coordinates.csv")

  # Apply the function to each row and assign the result to the DataFrame
    merged[['ping_x', 'ping_y', 'ping_z']] = merged.apply(compute_sonar_ping, axis=1)

    coords = pointProbability(merged)

    coords.to_csv(out_csv, mode = 'a', index=False)

    filtered_points = coords[coords['probability'] >= 1]

    # Define the starting UTM coordinate (example values)
    start_easting = 394716.30    # meters
    start_northing = 5059887.02  # meters

    # Compute the new UTM coordinates by simply adding the displacements
    merged['utm_easting'] = start_easting + merged['ping_x']
    merged['utm_northing'] = start_northing + merged['ping_y']

    source_crs = "epsg:32618"
    target_crs = "epsg:4326"

    transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

    def utm_to_latlon(easting, northing):
        lon, lat = transformer.transform(easting, northing)
        return lon, lat

    # Apply the conversion to each row in the DataFrame
    merged[['longitude', 'latitude']] = merged.apply(
        lambda row: pd.Series(utm_to_latlon(row['utm_easting'], row['utm_northing'])),
        axis=1
    )

    points_path = os.path.join(base_path, "data\sonarPoints.csv")

    merged.to_csv(points_path, mode = 'a', index=False)

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
    # Convert angles from degrees to radians.
    pitch_rad   = math.radians(initial_pitch)
    roll_rad    = math.radians(roll)
    bearing_rad = math.radians(beam_bearing)
    
    v = np.array([
        math.cos(pitch_rad) * math.cos(bearing_rad),
        math.cos(pitch_rad) * math.sin(bearing_rad),
        math.sin(pitch_rad)
    ])
    
    R_x = np.array([
        [1, 0, 0],
        [0, math.cos(roll_rad), -math.sin(roll_rad)],
        [0, math.sin(roll_rad),  math.cos(roll_rad)]
    ])
    v_new = R_x @ v

    horizontal_magnitude = math.hypot(v_new[0], v_new[1])
    new_pitch = math.degrees(math.atan2(v_new[2], horizontal_magnitude))
    
    # The new bearing (relative horizontal angle) is given by:
    new_bearing = math.degrees(math.atan2(v_new[1], v_new[0]))
    
    # Combine with the initial heading to get the new global heading.
    new_heading = (initial_heading + new_bearing) % 360
    
    # Roll has been applied via the rotation, so we set it to 0.
    new_roll = 0

    return new_pitch, new_heading, new_roll


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
    return  R_r @ R_p @ R_y

def compute_sonar_ping(row):
    """Compute the Cartesian coordinates of the sonar ping for a row in the DataFrame
    
    """
    bearing, heading, pitch, roll = row['bearing'], row['heading (°)'], row['pitch (°)'], row['roll (°)']
    x, y, z = row['x (m)'], row['y (m)'], row['z (m)']
    ping_distance = row['distance']

    new_pitch, new_heading, new_roll = compute_beam_pitch_and_heading(pitch, roll, bearing, heading)

    r = rotation_matrix(new_heading, new_pitch, new_roll)

    ping_local = np.array([-1*ping_distance,0,0,])

        # Transform ping to global frame
    ping_global = r @ ping_local

    if pitch < 0 and ping_global[2] > 0:
        ping_global[2] *= -1

        # Add sonar's position to get global coordinates
    ping_global += np.array([x, y, z])

    return pd.Series({'ping_x': ping_global[0], 'ping_y': ping_global[1], 'ping_z': ping_global[2]})

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