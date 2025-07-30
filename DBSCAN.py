from sklearn.cluster import HDBSCAN
from sklearn.metrics import silhouette_score as ss
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

df =  pd.read_csv(r"c:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06\sonar\scans\2025.05.21_19-48-29-667.csv")

# Calculate Cartesian coordinates

df["bearing_cartesian"] = np.radians(90 - df["bearing"])
df["x"] = df["distance"] * np.cos(df["bearing_cartesian"])
df["y"] = df["distance"] * np.sin(df["bearing_cartesian"])

df['bin'] = None

# Loop over rows and apply binning logic
for index, row in df.iterrows():
    val = row['intensity']
    if val <= 3:
        df.at[index, 'bin'] = 1
    elif 4 <= val <= 15:
        df.at[index, 'bin'] = 2


x_y_z = df[['x', 'y', 'bin']]

x, y, z = df.x, df.y, df.intensity

X = x_y_z.to_numpy()

dbscan_cluster_model = HDBSCAN(min_samples=200).fit(X)

df['cluster'] = dbscan_cluster_model.labels_

labels = dbscan_cluster_model.labels_
labels_set = set(labels)
num_clusters = len(labels_set)

fig = px.scatter(x=x, y=y, color=df['cluster'])
fig.show()