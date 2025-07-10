import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import datetime

def main():
    '''
    ProcesspculusCSV.py

    Takes the raw csv sonar output from readOculus.py and merges it with positioning data from the combined_log and the dvl_deadreckoning_log

    Before running the script, base_path, timestamp_list and names should be modified to the desired input

    change filter to true if the raw sonar csv was orciessed using the filter option
    '''

    # filter setting
    filter = True

    # base path of ROV mission package
    base_path = r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06"

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
        ("2025.05.21 19:43:57:000", "2025.05.21 19:44:07:000"),
        ("2025.05.21 19:44:34:000", "2025.05.21 19:44:44:000"),
        ("2025.05.21 19:47:42:000", "2025.05.21 19:49:32:000")
    ]

    #########################################################################################################################################################################################
    # Names of output csv files
    # Naming convention:
    # survey type code: cross section = CS, range finding = RF, sweeping scan = SS
    # Survey description code: cross sections can be south to north (S2N) or north to south (N2S),
    # range finding can be north (N), south (S) or down (D), and sweeping scans can be north (N) or south (S)
    # The survey description code is followed by an ID number for the specific survey type. This is useful if a specific survey has be been performed multple times within a single log file.
    # All names end with SBT, meaning "Split by Timestamp", allowing for the SBT files to be  distinuged  from unfiltered csv log files.

    names = ["Oculus_20250521_194207_RF_S1_SBT", "Oculus_20250521_194207_RF_N1_SBT", "Oculus_20250521_194207_CS_S2N1_SBT"]

    #########################################################################################################################################################################################

    # Load CSV file
    sonar = os.path.join(base_path, "sonar")

    csvFile = find_csv(sonar, filter)

    print(csvFile)

    csvPath = os.path.join(base_path, "sonar", csvFile)

    oculus_csv = pd.read_csv(csvPath, encoding = "utf-8", sep=',')

    # Convert timestamp column to datetime
    oculus_csv["timestamp"] = pd.to_datetime(oculus_csv["timestamp"], format="%Y.%m.%d %H:%M:%S:%f")

    csvNames = []

    for name in names:
        if filter == False:
            name += ".csv"
            csvNames.append(name)
        else:
            name += "_filtered.csv"
            csvNames.append(name)

    # Save filtered segments as separate CSV files
    for (start_str, end_str), name in zip(timestamp_list, csvNames):
        start = datetime.datetime.strptime(start_str, "%Y.%m.%d %H:%M:%S:%f")
        end = datetime.datetime.strptime(end_str, "%Y.%m.%d %H:%M:%S:%f")
        filtered_df = oculus_csv[(oculus_csv["timestamp"] >= start) & (oculus_csv["timestamp"] <= end)]
        outPath = os.path.join(base_path, "sonar", name)
        filtered_df["timestamp"] = filtered_df["timestamp"].dt.strftime("%Y.%m.%d %H:%M:%S:%f")
        filtered_df.to_csv(outPath, index=False)

    print(csvNames)

    # add heading data to dead reckoning file
    combined['depth'] = combined['depth'].str[:-1]
    combined['depth'] = combined['depth'].astype(float)
    combined['depth'] = combined['depth'] * -1

    data_column = combined[['timestamp', 'heading (°)', 'velocity_forward (m/s)', 'velocity_right (m/s)', 'depth']]

    deadReckoningCombined= pd.merge(deadReckoning, data_column, on='timestamp', how='left')

    deadReckoningCombined_folder = "data\deadReckoningCombined.csv"

    deadReckoningCombined_path = os.path.join(base_path, deadReckoningCombined_folder)

    deadReckoningCombined.to_csv(deadReckoningCombined_path, mode = 'a', index=False)

    csvFiles = find_filtered_csv(sonar, filter)

    #
    for file_name in csvFiles:
        csvPath = os.path.join(base_path, "sonar", file_name)
        filtered_csv = pd.read_csv(csvPath, encoding = "utf-8", sep=',')

        # merge dead reckoning file and oculus csv file based on time stamp
        columns_to_keep = ['timestamp', 'x (m)', 'y (m)', 'roll (°)', 'pitch (°)', 'heading (°)', 'velocity_forward (m/s)', 'velocity_right (m/s)', 'depth']
        xyz = deadReckoningCombined[columns_to_keep]
        xyz = xyz.copy()
        xyz['timestamp'] = pd.to_datetime(xyz['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')
        filtered_csv['timestamp'] = pd.to_datetime(filtered_csv['timestamp'], format='%Y.%m.%d %H:%M:%S:%f')

        filtered_csv = filtered_csv.sort_values('timestamp')
        xyz = xyz.sort_values('timestamp')

        merged = pd.merge_asof(filtered_csv, xyz, on='timestamp', tolerance=pd.Timedelta('50ms'), direction='nearest')

        merged = merged.dropna(subset=['x (m)'])

        if filter == False:
            out_name = file_name.replace("SBT.csv", "SBT_merged.csv")
        else:
            out_name = file_name.replace("SBT_filtered.csv", "SBT_filtered_merged.csv")

        out_csv = os.path.join(base_path, "sonar", out_name)

        merged["timestamp"] = merged["timestamp"].dt.strftime("%Y.%m.%d %H:%M:%S:%f")
        merged.to_csv(out_csv, mode = 'a', index=False)
    
    print("prcoessing complete")

# find oculus file
def find_csv(path, filter):
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if filter == False:
            if file_name.endswith(".csv"):
                return file_name
        else:
            if file_name.endswith("filtered.csv"):
                return file_name

# find filtered oculus files, make a lsit
def find_filtered_csv(path, filter):
    files = []
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if filter == False:
            if file_name.endswith("SBT.csv"):
                files.append(file_name)
        else:
            if file_name.endswith("SBT_filtered.csv"):
                files.append(file_name)
    return files
        
if __name__ == "__main__":
    main()