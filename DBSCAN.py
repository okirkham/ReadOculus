from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score as ss
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools
import plotly.express as px

df =  pd.read_csv(r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06\sonar\scans\2025.05.21_19-48-16-031.csv")

# Calculate Cartesian coordinates

df["bearing_cartesian"] = np.radians(90 - df["bearing"])
df["x"] = df["distance"] * np.cos(df["bearing_cartesian"])
df["y"] = df["distance"] * np.sin(df["bearing_cartesian"])

df['intensity'] = df['intensity']*5

x_y_z = df[['x', 'y', 'intensity']]

x, y, z = df.x, df.y, df.intensity

X = x_y_z.to_numpy()

epsilons = np.linspace(0.01, 5, num=20)

min_samples = np.arange(1,10, step=1)

combinations = list(itertools.product(epsilons, min_samples))

N = len(combinations)

def get_scores_and_labels(combinations, X):
    scores = []
    all_labels_list = []
    
    for i, (eps, num_samples) in enumerate(combinations):
        dbscan_cluster_model = DBSCAN(eps=eps, min_samples=num_samples).fit(X)
        labels = dbscan_cluster_model.labels_
        labels_set = set(labels)
        num_clusters = len(labels_set)
        if -1 in labels_set:
            num_clusters -= 1

        if (num_clusters < 2) or (num_clusters > 50):
            scores.append(-10)
            all_labels_list.append('bad')
            c = (eps, num_samples)
            print(f"Combination {c} on iteration {i+1} of {N} has {num_clusters} clusters. Moving on")
            continue

        scores.append(ss(X, labels))
        all_labels_list.append(labels)
        print(f"Index: {i}, Score: {scores[-1]}, Labels: {all_labels_list[-1]}, NumClusters: {num_clusters}")

    best_index = np.argmax(scores)
    best_parameters = combinations[best_index]
    best_labels = all_labels_list[best_index]
    best_score = scores[best_index]

    return {'best_epsilon': best_parameters[0],
            'best_min_samples': best_parameters[1],
            'best_labels': best_labels,
            'best_score': best_score}

print(f'trying {N} possible combinations')

best_Score = get_scores_and_labels(combinations, X)

dbscan_cluster_model = DBSCAN(eps=best_Score['best_epsilon'], min_samples=best_Score['best_min_samples']).fit(X)

df['cluster'] = dbscan_cluster_model.labels_

labels = dbscan_cluster_model.labels_
labels_set = set(labels)
num_clusters = len(labels_set)
print(f'there are {num_clusters} clusters')

fig = px.scatter(x=x, y=y, color=df['cluster'])
fig.show()