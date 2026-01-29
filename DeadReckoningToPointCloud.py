import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import math
import pyproj

'''
DeadReckoningToPointCloud.py

Converts filtered and merged Oculus sonar csv files into point clouds with UTM and lat/lon coordinates

Use in conjunction with readOculusV2 and ProcessOculusCSV.py
    
'''

def main():

    # base path of mission package
    
    # coordinates of starting position [easting, northing]
    meltHole = [495407.35170000,9184737.66000000]

    stake50m = [495449.17970000, 9184709.29400000]

    stake100m = [495488.65587361,9184680.05162800]
 
    # path of root folder
    base_path = r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06"

    sonar = os.path.join(base_path, "sonar")

    mergedList = find_merged_csv(sonar)

    for merged in mergedList:
        output = False

        out_name = merged.replace("SBT_merged.csv", "SBT_coordinates.csv") 

        out_csv = os.path.join(base_path, "data", out_name)

        if os.path.exists(out_csv):
            print(f'{out_csv} already exists')
            pass
        else:
            if merged[23:25] == "CS":
                try: 
                    offset = float(merged[33:35])
                except ValueError:
                    print(f"survey offset for {merged} is incorrect")

                if merged[26:27] == "1":
                    df = crossSection(merged, base_path, offset, meltHole[0], meltHole[1])
                    output = True
                elif merged[26:27] == "2":
                    df = crossSection(merged, base_path, offset, stake50m[0], stake50m[1])
                    output = True
                elif merged[26:27] == "3":
                    df = crossSection(merged, base_path, offset, stake100m[0], stake100m[1])
                    output = True
            else:
                print(f"coordinates cannot be generated from {merged}")
            
            if output == True:              
                out_df = df[['timestamp', 'distance', 'intensity', 'bearing', 'heading (°)', 'adjusted_heading',
                            'camera pitch (°)', 'roll (°)', 'total_forward', 'total_right', 'x', 'y',
                            'depth', 'ping_x', 'ping_y', 'ping_z', 'longitude', 'latitude', 'rov_longitude', 'rov_latitude']]

                out_df.to_csv(out_csv, mode = 'a', index=False)

                print(f"point cloud {out_name} generated")

# find filtered and merged oculus files, make a list
def find_merged_csv(path):
    files = []
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if "SBT_merged.csv" in file_name:
            files.append(file_name)

    return files

def compute_beam_pitch_and_heading(initial_pitch, roll, beam_bearing, initial_heading):
    # Convert angles from degrees to radians.
    pitch_rad   = math.radians(initial_pitch)
    roll_rad    = math.radians(roll)
    bearing_rad = math.radians(beam_bearing)
    
    v = np.array([
        math.cos(pitch_rad) * math.cos(-bearing_rad),
        math.cos(pitch_rad) * math.sin(-bearing_rad),
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
    pitch = np.radians(pitch)
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
    bearing, heading, pitch, roll = row['bearing'], row['adjusted_heading'], row['camera pitch (°)'], row['roll (°)']
    x, y, z = row['x'], row['y'], row['depth']
    ping_distance = row['distance']

    new_pitch, new_heading, new_roll = compute_beam_pitch_and_heading(pitch, roll, bearing, heading)

    r = rotation_matrix(new_heading, new_pitch, new_roll)

    ping_local = np.array([ping_distance,0,0,])

        # Transform ping to global frame
    ping_global = r @ ping_local

    if pitch < 0 and ping_global[2] > 0:
        ping_global[2] *= -1

        # Add sonar's position to get global coordinates
    ping_global += np.array([x, y, z])

    return pd.Series({'ping_x': ping_global[0], 'ping_y': ping_global[1], 'ping_z': ping_global[2]})

def createPointCloud(df, easting, northing):
        # Apply the function to each row and assign the result to the DataFrame
        df[['ping_x', 'ping_y', 'ping_z']] = df.apply(compute_sonar_ping, axis=1)

        # Compute the new UTM coordinates by adding the displacements
        df['ping_easting'] = easting + df['ping_y']
        df['ping_northing'] = northing + df['ping_x']


        df['rov_easting'] = easting + df['y']
        df['rov_northing'] = northing + df['x']

        source_crs = "epsg:32617"
        target_crs = "epsg:4326"

        transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

        def utm_to_latlon(easting, northing):
            lon, lat = transformer.transform(easting, northing)
            return lon, lat

        # Apply the conversion to each row in the DataFrame
        df[['longitude', 'latitude']] = df.apply(
            lambda row: pd.Series(utm_to_latlon(row['ping_easting'], row['ping_northing'])),
            axis=1
        )

        df[['rov_longitude', 'rov_latitude']] = df.apply(
            lambda row: pd.Series(utm_to_latlon(row['rov_easting'], row['rov_northing'])),
            axis=1
        )

        return df

def crossSection(csvName, basepath, offset, easting, northing):
    """
    csv = input split and merged csv, basepath = path to root directory, offset = distance from reference waypoint, easting, northing

    """
    print(f"generating coordinates for {csvName}")

    csvPath = os.path.join(basepath, "sonar", csvName)

    csv_df = pd.read_csv(csvPath, encoding = "utf-8", sep=',')

    # extract survey code
    code = csvName[28:31]

    if code.startswith("S2N"):
        csv_df['x'] = csv_df['total_forward'] 
        csv_df['x'] = csv_df['x'] - offset
        csv_df['y'] = csv_df['total_right']
        csv_df['adjusted_heading'] = 0

        df = createPointCloud(csv_df, easting, northing)

        return df
    
    elif code.startswith("N2S"):
        csv_df['x'] = csv_df['total_forward'] * -1
        csv_df['x'] = csv_df['x'] + offset
        csv_df['y'] = csv_df['total_right'] * -1
        csv_df['adjusted_heading'] = 122.5

        df = createPointCloud(csv_df, easting, northing)

        return df
    else:
        print(f"survey code for {csvName} is invalid")
    
    
if __name__ == "__main__":
    main()