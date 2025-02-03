import matplotlib.pyplot as plt
import pandas as pd

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

deadReckoning = pd.read_csv(r"C:\Users\0w3nk\OneDrive - Carleton University\January 29th, ROV Pool Tests\DEEP_TREKKER_MISSION-PACKAGE_2025-01-29_17-01-17\data\peripheral\dvl_deadreckoning_log.csv", encoding = "utf-8", sep=',')
oculus = pd.read_csv(r"C:\Users\0w3nk\Documents\ROV\Oculus_20250129_170117.csv", encoding = "utf-8", sep=',')

XYZ = deadReckoning.iloc[:, 0:4]

XYZ['timestamp'] = pd.to_datetime(XYZ['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')
oculus['timestamp'] = pd.to_datetime(oculus['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')

merged = pd.merge_asof(oculus, XYZ, on='timestamp', tolerance=pd.Timedelta('50ms'), direction='nearest')

merged = merged.dropna(subset=['x (m)'])

merged.to_csv(r"C:\Users\0w3nk\Documents\ROV\merged", mode = 'a', index=False)

print("done")

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