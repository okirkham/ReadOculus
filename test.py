import pandas as pd 
# Sample DataFrames with datetime stamps 
df1 = pd.DataFrame({ 'timestamp': ['2024-11-08 20:30:00.000', '2024-11-08 20:35:00.250', '2024-11-08 20:40:00.500'], 
                        'value1': [10, 20, 30] }) 
df2 = pd.DataFrame({ 'timestamp': ['2024-11-08 20:30:00.100', '2024-11-08 20:35:00.400', '2024-11-08 20:42:00.750'], 
                        'value2': [100, 200, 300] }) 
# # Convert timestamps to datetime 

df1['timestamp'] = pd.to_datetime(df1['timestamp']) 
df2['timestamp'] = pd.to_datetime(df2['timestamp']) 
# Function to find rows in df2 within 0.25 seconds of rows in df1 

def find_closest_timestamp(row, df2, tolerance=pd.Timedelta(seconds=0.25)): 
    closest_row = df2[(df2['timestamp'] >= row['timestamp'] - tolerance) & (df2['timestamp'] <= row['timestamp'] + tolerance)] 
    if not closest_row.empty: 
        closest_row = closest_row.iloc[0] 
        return closest_row 
    else: return pd.Series([None, None], index=['timestamp', 'value2']) 
    
# Apply function and create a new DataFrame 

merged_data = [] 
for idx, row in df1.iterrows(): 
    closest_row = find_closest_timestamp(row, df2) 
    merged_data.append(pd.concat([row, closest_row])) 
    
merged_df = pd.DataFrame(merged_data) # Drop rows where there was no match 
merged_df.dropna(subset=['value2'], inplace=True)