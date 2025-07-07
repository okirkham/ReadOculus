import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import datetime

def main():
    '''
    
    
    '''
    # base path of 
    base_path = r"C:\Users\0w3nk\Documents\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-03-15_10-55-07"

    # dead reckoning file
    deadReckoningFolder = "data\peripheral\dvl_deadreckoning_log.csv"

    deadReckoningPath = os.path.join(base_path, deadReckoningFolder)

    deadReckoning = pd.read_csv(deadReckoningPath, encoding = "utf-8", sep=',')

    # combined log
    combined_folder = "data\combined_log.csv"

    combined_path = os.path.join(base_path, combined_folder)

    combined = pd.read_csv(combined_path, encoding = "utf-8", sep=',')

    # List of timestamps to be extracted
    timestamp_list = [
        ("2025.05.22 00:42:07:672", "2025.05.22 00:43:05:647"),
        ("2025.05.22 00:43:05:719", "2025.05.22 00:44:44:361")
    ]

    #########################################################################################################################################################################################
    # Names of output csv files
    # Naming convention:
    # survey type code: cross section = CS, range finding = RF, sweeping scan = SS
    # Survey description code: cross sections can be south to north (S2N) or north to south (N2S),
    # range finding can be north (N), south (S) or down (D), and sweeping scans can be north (N) or south (S)
    # The survey description code is followed by an ID number for the specific survey type. This is useful if a specific survey has be been performed multple times within a single log file.
    # All names end with SBT, meaning "Split by Timestamp", allowing for the SBT files to be  distinuged  from unfiltered csv log files.

    names = ["Oculus_20250521_194207_CS_S2N1_SBT", "Oculus_20250521_194207_N2S1_SBT"]

    #########################################################################################################################################################################################

    # Load CSV file
    sonar = os.path.join(base_path, "sonar")

    csvFile = find_csv(sonar)

    csvPath = os.path.join(base_path, "sonar", csvFile)

    oculus_csv = pd.read_csv(csvPath, encoding = "utf-8", sep=',')

    # Convert timestamp column to datetime
    oculus_csv["Timestamp"] = pd.to_datetime(oculus_csv["Timestamp"], format="%Y.%m.%d %H:%M:%S:%f")

    csvNames = []

    for name in names:
        name += ".csv"
        csvNames.append(name)

    # Save filtered segments as separate CSV files
    for (start_str, end_str), name in zip(timestamp_list, csvNames):
        start = datetime.strptime(start_str, "%Y.%m.%d %H:%M:%S:%f")
        end = datetime.strptime(end_str, "%Y.%m.%d %H:%M:%S:%f")
        filtered_df = oculus_csv[(oculus_csv["Timestamp"] >= start) & (oculus_csv["Timestamp"] <= end)]
        outPath = os.path.join(base_path, "sonar", name)
        filtered_df.to_csv(outPath, index=False)

    # add heading data to dead reckoning file
    data_column = combined[['timestamp', 'heading (°)', 'velocity_forward (m/s)', 'velocity_right (m/s)']]

    deadReckoningCombined= pd.merge(deadReckoning, data_column, on='timestamp', how='left')

    deadReckoningCombined_folder = "data\deadReckoningCombined.csv"

    deadReckoningCombined_path = os.path.join(base_path, deadReckoningCombined_folder)

    deadReckoningCombined.to_csv(deadReckoningCombined_path, mode = 'a', index=False)

    csvFiles = find_filtered_csv(sonar)

    #
    for file_name in csvFiles:
        csvPath = os.path.join(base_path, "sonar", file_name)
        filtered_csv = pd.read_csv(csvPath, encoding = "utf-8", sep=',')

        # merge dead reckoning file and oculus csv file based on time stamp
        columns_to_keep = ['timestamp', 'x (m)', 'y (m)', 'z (m)', 'roll (°)', 'pitch (°)', 'heading (°)', 'velocity_forward (m/s)', 'velocity_right (m/s)']
        xyz = deadReckoningCombined[columns_to_keep]
        xyz = xyz.copy()
        xyz['timestamp'] = pd.to_datetime(xyz['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')
        filtered_csv['timestamp'] = pd.to_datetime(filtered_csv['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')

        filtered_csv = filtered_csv.sort_values('timestamp')
        xyz = xyz.sort_values('timestamp')

        merged = pd.merge_asof(filtered_csv, xyz, on='timestamp', tolerance=pd.Timedelta('50ms'), direction='nearest')

        merged = merged.dropna(subset=['x (m)'])

        out_name = file_name.replace("SBT.csv", "SBT_merged.csv") 

        out_csv = os.path.join(base_path, "sonar", out_name)

        merged.to_csv(out_csv, mode = 'a', index=False)

# find oculus file
def find_csv(path):
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if file_name.endswith(".csv"):
            return file_name

# find filtered oculus files, make a lsit
def find_filtered_csv(path):
    files = []
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if file_name.endswith("SBT.csv"):
            files.append(file_name)
    return files
        
if __name__ == "__main__":
    main()