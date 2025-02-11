import numpy as np
import pandas as pd

def rotation_matrix(heading, pitch, roll):
    """Compute the 3D rotation matrix from heading, pitch, and roll (in degrees)."""
    # Convert degrees to radians
    heading = np.radians(heading)
    pitch = np.radians(-pitch)  # Negate pitch to correct for coordinate system
    roll = np.radians(roll)

    # Rotation matrices
    R_z = np.array([
        [np.cos(heading), -np.sin(heading), 0],
        [np.sin(heading),  np.cos(heading), 0],
        [0, 0, 1]
    ])

    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])

    R_y = np.array([
        [np.cos(pitch), 0, -np.sin(pitch)],  # <-- Fixed negative sign
        [0, 1, 0],
        [np.sin(pitch), 0, np.cos(pitch)]  # <-- Fixed sign
    ])

    # Apply rotations in the order Z * X * Y
    return R_z @ R_x @ R_y

# def compute_sonar_ping(row):
#     """Compute the Cartesian coordinates of the sonar ping for a row in the DataFrame."""
#     heading, pitch, roll = row['heading'], row['pitch'], row['roll']
#     x, y, z = row['x'], row['y'], row['z']
#     ping_distance = row['ping_distance']

#     # Adjust the local ping vector to account for pitch before rotation
#     ping_local = np.array([
#     ping_distance * np.cos(np.radians(pitch)),  # Forward (X)
#     0,  # No lateral movement (Y)
#     -ping_distance * np.sin(np.radians(pitch))  # Depth (negative pitch should make this more negative)
# ])

#     # Compute rotation matrix
#     R = rotation_matrix(heading, pitch, roll)

#     # Transform ping to global frame
#     ping_global = R @ ping_local

#     # Add sonar's position to get global coordinates
#     ping_global += np.array([x, y, z])

#     return pd.Series({'ping_x': ping_global[0], 'ping_y': ping_global[1], 'ping_z': ping_global[2]})

def compute_sonar_ping_debug(row):
    """Compute the Cartesian coordinates of the sonar ping for a row in the DataFrame (with debug prints)."""
    heading, pitch, roll = row['heading'], row['pitch'], row['roll']
    x, y, z = row['x'], row['y'], row['z']
    ping_distance = row['ping_distance']

    # Adjust the local ping vector to account for pitch before rotation
    ping_local = np.array([
        ping_distance * np.cos(np.radians(pitch)),  # Forward movement
        0,  # No sideways movement
        -ping_distance * np.sin(np.radians(pitch))  # Depth movement (negative pitch should move it downward)
    ])

    # Compute rotation matrix
    R = rotation_matrix(heading, pitch, roll)

    # Transform ping to global frame
    ping_global = R @ ping_local

    # Add sonar's position to get global coordinates
    ping_global += np.array([x, y, z])

    # Debugging: Print key values
    print(f"\nRow: {row.name}")
    print(f"  Heading: {heading}, Pitch: {pitch}, Roll: {roll}")
    print(f"  Sonar Position (x, y, z): ({x}, {y}, {z})")
    print(f"  Ping Local: {ping_local}")
    print(f"  Transformed Ping Global: {ping_global}")

    return pd.Series({'ping_x': ping_global[0], 'ping_y': ping_global[1], 'ping_z': ping_global[2]})

# Example DataFrame
data = {
    'heading': [45, 90, 180],
    'pitch': [10, -5, -30],  # Negative pitch should push ping deeper
    'roll': [5, -2, 0],
    'x': [10, 20, -5],
    'y': [-5, 15, 30],
    'z': [-20, -25, -10],
    'ping_distance': [15, 20, 10]
}

df = pd.DataFrame(data)

# Apply function to each row
#df[['ping_x', 'ping_y', 'ping_z']] = df.apply(compute_sonar_ping, axis=1)

df[['ping_x', 'ping_y', 'ping_z']] = df.apply(compute_sonar_ping_debug, axis=1)

print(df)