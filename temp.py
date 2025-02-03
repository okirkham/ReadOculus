import pandas as pd
import math
from pyproj import Proj, transform
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# merge combined_log and dvl_deadreckoning_log
# combined = pd.read_csv(r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\combined_log.csv")
# deadreckoning = pd.read_csv(r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\peripheral\dvl_deadreckoning_log.csv")

# data_column = combined[['timestamp', 'heading (°)']]

# merged_csv = pd.merge(deadreckoning, data_column, on='timestamp', how='left')

# merged_csv.to_csv(r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\peripheral\merged.csv", index=False)

# #entire_metadf = pd.read_csv(merged_csv, encoding = "utf-8", sep=',')
# #metadf = merged_csv.loc[[0,1,2,3,5,6,7,13]]

# #metadf['timestamp'] = pd.to_datetime(metadf['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')
# #final_df['timestamp'] = pd.to_datetime(final_df['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')

 
# #metadf = metadf.sort_values('timestamp') 

# #merged = pd.merge_asof(final_df, metadf, on='timestamp', tolerance=pd.Timedelta('250ms'), direction='nearest')

# def add_bearings(bearing1, bearing2): 
#     result = (bearing1 + bearing2) % 360 
#     if result < 0: 
#         result += 360 
    
#     return result

# def find_adjacent(distance, bearing): 
#     bearingRadians = math.radians(bearing) 
#     adjacent = distance * math.cos(bearingRadians) 
#     return adjacent

# def find_opposite(distance, bearing): 
#     bearingRadians = math.radians(bearing) 
#     opposite = distance * math.sin(bearingRadians) 
#     return opposite

# def latlon_to_utm(lat, lon, zone): 
#     wgs84 = Proj(init='epsg:4326') # WGS84 latitude and longitude 
#     utm = Proj(proj='utm', zone=zone, ellps='WGS84')
#     easting, northing = transform(wgs84, utm, lon, lat) 
#     return easting, northing

# def get_utm_zone(lon): 
#     return int((lon + 180) // 6) + 1



# Sample data points
points = [
    (-1, 2, 3),
    (4, 5, 6),
    (7, 8, 9),
    (10, 11, 12),
    (13, 14, 15)
]

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Extract x, y, and z coordinates
x = [point[0] for point in points]
y = [point[1] for point in points]
z = [point[2] for point in points]

# Plot points
ax.scatter(x, y, z, c='b', marker='o')

# Set labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Show plot
plt.show()