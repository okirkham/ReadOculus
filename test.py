import numpy as np
import pandas as pd
import math

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
    """Compute the 3D rotation matrix from heading, pitch, and roll (in degrees)."""
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
    """Compute the Cartesian coordinates of the sonar ping for a row in the DataFrame (with debug prints)."""
    bearing, heading, pitch, roll = row['bearing'], row['heading'], row['pitch'], row['roll']
    x, y, z = row['x'], row['y'], row['z']
    ping_distance = row['ping_distance']

    new_pitch, new_heading = compute_beam_pitch_and_heading(pitch, roll, bearing, heading)

    print(new_heading)

    r = rotation_matrix(new_heading, new_pitch, roll)

    ping_local = np.array([ping_distance, 0, 0])

    # Transform ping to global frame
    ping_global = r @ ping_local

    # Add sonar's position to get global coordinates
    ping_global += np.array([-x, y, z])

    print(ping_global)

    return pd.Series({'ping_x': -1*ping_global[0], 'ping_y': ping_global[1], 'ping_z': ping_global[2]})

# Example DataFrame
data = {
    'bearing': [0],
    'heading': [100],
    'pitch': [0],  # Negative pitch should push ping deeper
    'roll': [0],
    'x': [0],
    'y': [0],
    'z': [0],
    'ping_distance': [10]
}

df = pd.DataFrame(data)

df[['ping_x', 'ping_y', 'ping_z']] = df.apply(compute_sonar_ping, axis=1)

print(df)