import chardet # Detect encoding 
import pandas as pd

with open(r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2023-07-17_18-12-24\combined_log.csv", 'rb') as f: 
    result = chardet.detect(f.read()) # Read the file with the detected encoding 

print(result)

df = pd.read_csv(r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2023-07-17_18-12-24\combined_log.csv", encoding=result['encoding']) 

print(df.head())