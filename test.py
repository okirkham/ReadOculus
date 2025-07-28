import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


df =  pd.read_csv(r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06\sonar\scans\2025.05.21_19-48-16-031.csv")

x, y, z = df.bearing, df.rangeLine, df.intensity

fig = px.scatter(x=x, y=y, color=df['intensity'])

fig.show()
