import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# base path of 
base_path = r"C:\Users\0w3nk\Documents\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-02-07_14-01-04"

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

merged = pd.merge_asof(oculus_csv, xyz, on='timestamp', tolerance=pd.Timedelta('50ms'), direction='nearest')

merged = merged.dropna(subset=['x (m)'])

def add_bearings(bearing1, bearing2): 
    result = (bearing1 + bearing2) % 360 
    if result < 0: 
        result += 360 
    
    return result

def Rypr(y, p, r):
    '''
    Rotation matrix y=heading, p=pitch, r=roll in degrees
    '''
    # from Degree to Radians
    y = y*np.pi/180.0
    p = p*np.pi/180.0
    r = r*np.pi/180.0
    
    Rr = np.matrix([[1.0, 0.0, 0.0],[0.0, np.cos(r), -np.sin(r)],[0.0, np.sin(r), np.cos(r)]])
    Rp = np.matrix([[np.cos(p), 0.0, np.sin(p)],[0.0, 1.0, 0.0],[-np.sin(p), 0.0, np.cos(p)]])
    Ry = np.matrix([[np.cos(y), -np.sin(y), 0.0],[np.sin(y), np.cos(y), 0.0],[0.0, 0.0, 1.0]])
    
    return Ry*Rp*Rr

# # Extract x, y, and z coordinates
# x = [point[0] for point in points]
# y = [point[1] for point in points]
# z = [point[2] for point in points]

# # Plot points
# ax.scatter(x, y, z, c='b', marker='o')

# # Set labels
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')

# # Show plot
# plt.show()