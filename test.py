import pandas as pd
import numpy as np
import os

d = {'x (m)': [-0.5, -1], 'y (m)': [3, 4], 'z (m)': [-1,-2], 'heading (°)': [200,250], 'pitch (°)': [-45,-32], 'roll (°)': [1,2], 'distance': [10,15]}

df = pd.DataFrame(data=d)

x, y, z = df['x (m)'], df['y (m)'], df['z (m)']
heading, pitch, roll = df['heading (°)'], df['pitch (°)'], df['roll (°)']
distance = df['distance']
    
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
    
print(ping_coordinates)