import struct
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import numpy as np
from sklearn.cluster import HDBSCAN

def main():
    # input misson package path
    base_path = r"C:\Users\0w3nk\Documents\Masters\MIS2025\Data\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-05-21_19-42-06"

    # define path to sonar folder
    sonar = os.path.join(base_path, "sonar")

    # locate the oculus file within the sonar folder
    binaryfile = find_oculus(sonar)

    # define path to oculus file
    oculus = os.path.join(base_path, "sonar", binaryfile)

    # define path to scans folder which must be added prior to running the code in the sonar folder
    scans = os.path.join(base_path, "sonar", "scans")

    # open the binary oculus file
    oculusBinary = open(oculus, mode='rb')
    sonarData = oculusBinary.read()
    fileSize = len(sonarData)

    # define constant value sizes 
    position = 48
    logSize = 242
    bearingStart = position + logSize

    # get metadata for the first log item
    dfSonarMeta = sonarLogHeader(sonarData, position, logSize)

    # find beam bearings, this is done only once as beam bearings do not change over the course of a mission
    numBearings = dfSonarMeta['bearingCount'].values[0]
    bearingList = bearings(sonarData, bearingStart, numBearings)

    # calculate estimate message size
    size = dfSonarMeta['messageSize'].values[0]
    true_size = size + 40

    # calculate the number of log items
    numItems = int((fileSize-48)/true_size)

    # create a list of timestamps that will be extracted from the oculus file
    timestamp_list = [
        ("2025.05.21 19:43:57:000", "2025.05.21 19:44:07:000"),
        ("2025.05.21 19:44:34:000", "2025.05.21 19:44:44:000"),
        ("2025.05.21 19:47:46:000", "2025.05.21 19:49:32:000"),
        ("2025.05.21 19:50:24:000", "2025.05.21 19:51:09:000")
    ]

    timestamp_ranges = [
        (datetime.strptime(start, "%Y.%m.%d %H:%M:%S:%f"),
        datetime.strptime(end, "%Y.%m.%d %H:%M:%S:%f"))
        for start, end in timestamp_list
    ]

    # define an empty list that will contain the names of log items that have already been converted to csv format
    scannedList = []

    # start iterating through the number of log items
    for item in range(0,numItems):
        # if the current position + the size of the next item > total log size, break to avoid throwing an error
        if position + logSize > fileSize: 
            break
        
        # read the metadata from the log item header
        sonarMeta = sonarLogHeader(sonarData, position, logSize)

        # extract key values
        rangeCount = sonarMeta['rangeCount'].values[0]
        rangeResolution = sonarMeta['rangeResolution'].values[0]
        time = sonarMeta['time'].values[0]
        messageSize = sonarMeta['messageSize'].values[0]

        utc_time = datetime.strptime(time, "%Y.%m.%d %H:%M:%S:%f").replace(tzinfo=timezone.utc)

        # Convert to timestamps Eastern Daylight Time (UTC-4) from UTC-0
        eastern_offset = timedelta(hours=-5)
        eastern_time = (utc_time + eastern_offset).replace(tzinfo=None)

        # if the timestamp of the log item falls within a timestamp in the timestamp list, begin converting the data
        if any(start <= eastern_time <= end for start, end in timestamp_ranges):
            print("Scan time:", eastern_time)
            # create a clean time stamp that will be used as the csv name
            clean_time = eastern_time.strftime("%Y.%m.%d_%H-%M-%S-%f")[:-3]
            name = f"{clean_time}.csv"
            out_csv = os.path.join(base_path, "sonar", "scans", f"{clean_time}.csv")

            # check if the csv has already been created
            if not os.path.exists(out_csv):
                # run the payload function to extract data for the item
                dataList = payload(sonarData, rangeCount, rangeResolution, eastern_time, position, bearingList)
                # convert data to a dataframe
                final_df = pd.DataFrame(dataList, columns=['bearing', 'rangeLine', 'rangeResolution', 'intensity', 
                                        'distance', 'timestamp'])
                # export data frame to csv  in the scans folder
                final_df.to_csv(out_csv, mode='a', index=False)
            else:
                # if csv already exists, add it to the scannedList
                scannedList.append(name)
                print('scan already exists')
        # update the position variable to move to the next log itme. 40 is added to reflect the additional log header that is found before the main log header
        position = position + messageSize + 40
    
    # convert the scannedList to a set for easier searching
    scannedSet = set(scannedList)

    # delete the scanned list and close the oculus file to free up memory
    del scannedList
    oculusBinary.close()

    # create the master csv where scans will be merged after preprocessing
    headers = ['bearing', 'rangeLine', 'rangeResolution', 'intensity', 'distance', 'timestamp']
    master_df = pd.DataFrame(columns=headers)
    out_master_name = binaryfile.replace(".oculus", ".csv")
    out_master = os.path.join(base_path, "sonar", out_master_name)

    if os.path.exists(out_master):
        print("master csv already exists")
    else:
        master_df.to_csv(out_master, index=False)

    # iterate through all scans in scans folder
    for scan in os.listdir(scans):
        # ignore previously created scans
        if scan in scannedSet:
            print("scan already added to master csv")
        else:
            # convert scan csv to data frame
            scan_path = os.path.join(scans, scan)
            df = pd.read_csv(scan_path, encoding = "utf-8", sep=',')

            # create new fields that contain the 2d cartesian coordinates of the sonar pings
            df["bearing_cartesian"] = np.radians(90 - df["bearing"])
            df["x"] = df["distance"] * np.cos(df["bearing_cartesian"])
            df["y"] = df["distance"] * np.sin(df["bearing_cartesian"])

            df['bin'] = None

            # put the intensity values into bins <4 and <=15
            df['bin'] = pd.cut(
                df['intensity'],
                bins=[-float('inf'), 3, 15],
                labels=[1, 2]
            ).astype('int')

            # create a numpy array with the x, y, and bin fields
            x_y_z = df[['x', 'y', 'bin']]
            X = x_y_z.to_numpy()

            # run a HDBSCAN cluster model with the numpy array
            dbscan_cluster_model = HDBSCAN(min_samples=200).fit(X)

            # add a cluster field to the data frame
            df['cluster'] = dbscan_cluster_model.labels_

            # keep only records that have a bin value of 2
            bin2_rows = df[df['bin'] == 2]

            # Get unique cluster labels associated with bin == 2 that are not -1 (outliers)
            clusters_with_bin2 = [c for c in bin2_rows['cluster'].unique() if c != -1]

            # Filter rows where cluster is one of those and bin == 2
            filtered = df[(df['cluster'].isin(clusters_with_bin2)) & (df['bin'] == 2)]

            # Extract the first six columns (by position or label)
            subset = filtered.iloc[:, :6]

            # Append to master DataFrame
            subset.to_csv(out_master, mode='a', index=False, header=False)

            print(f'{scan} merged with master csv')

    print('finished')

def find_oculus(path):
    # Iterate over all files in the specified folder
    for file_name in os.listdir(path):
        # Check if the file has the specified extension
        if file_name.endswith(".oculus"):
            return file_name

def header(data):
    data_length = 48
    data_list = [data[0:data_length]]
    for x in data_list:
        data_format = "<B3xI6s10x2h2d4x"
        data_payload = list(struct.unpack(data_format, x))
        
    # variables
    data_payload[0]                                      # fileHeader
    data_payload[1]                                      # sizeHeader
    data_payload[2]                                      # source
    data_payload[3]                                      # version
    data_payload[4]                                      # encryption
    data_payload[5]                                      # key
    data_payload[6]                                      # time

    hdrs = [
        "fileHeader",
        "sizeHeader",
        "source",
        "version",
        "encryption",
        "key",
        "time",
    ]

    df = pd.DataFrame(data=[data_payload], columns=hdrs)
    return df

def sonarLogHeader(data, start, logSize):
    data_list = [data[start:(start+logSize)]]
    for x in data_list:
        data_format = "<2I2h4xd2xh2I4x5HIH5B4dI8xI20xI4x8dBd2H16x3I"
        data_payload = list(struct.unpack(data_format, x))

    # variables
    data_payload[0]                                      # itemHeader
    data_payload[1]                                      # sizeHeader
    data_payload[2]                                      # messageType
    data_payload[3]                                      # version
    data_payload[4] = datetime.fromtimestamp(data_payload[4], tz=timezone.utc).strftime('%Y.%m.%d %H:%M:%S:%f')[:-3] # time   
    data_payload[5]                                      # compression
    data_payload[6]                                      # rawSize
    data_payload[7]                                      # payloadSize
    data_payload[8]                                      # 
    data_payload[9]                                      # 
    data_payload[10]                                     # 
    data_payload[11]                                     # 
    data_payload[12]                                     #    
    data_payload[13]                                     # 
    data_payload[14]                                     # 
    data_payload[15]                                     # 
    data_payload[16]                                     # 
    data_payload[17]                                     # 
    data_payload[18]                                     # 
    data_payload[19]                                     # 
    data_payload[20]                                     #    
    data_payload[21]                                     # 
    data_payload[22]                                     # 
    data_payload[23]                                     # 
    data_payload[24]                                     # 
    data_payload[25]                                     # 
    data_payload[26]                                     # 
    data_payload[27]                                     # 
    data_payload[28]                                     #    
    data_payload[29]                                     # 
    data_payload[30]                                     # 
    data_payload[31]                                     # 
    data_payload[32]                                     #    
    data_payload[33]                                     # 
    data_payload[34]                                     # 
    data_payload[35]                                     # 
    data_payload[36]                                     # rangeResolution
    data_payload[37]                                     # rangeCount
    data_payload[38]                                     # 
    data_payload[39]                                     # 
    data_payload[40]                                     #   
    data_payload[41]                                     # 


    hdrs = [
        "itemHeader",
        "sizeHeader",
        "messageType",
        "version",
        "time",
        "compression",
        "rawSize",
        "payloadSize1",
        "oculusID",
        "sourceID",
        "destinationID",
        "messageID",
        "version",
        "payloadSize2",
        "partNumber",
        "masterMode",
        "pingRate",
        "networkSpeed",
        "gamma",
        "flags",
        "range",
        "gain",
        "speedOfSound1",
        "salinity",
        "extFlags",
        "beaconLocatorFrequency",
        "pingID",
        "frequency",
        "temperature",
        "pressure",
        "heading",
        "pitch",
        "roll",
        "speedOfSound2",
        "pingStartTime",
        "dataSize",
        "rangeResolution",
        "rangeCount",
        "bearingCount",
        "imageOffset",
        "imageSize",
        "messageSize"

    ]

    df = pd.DataFrame(data=[data_payload], columns=hdrs)
    return df

def nibbleReader(binary):
    nibbles = [binary[i:i+4] for i in range(0, len(binary),4)]
    return nibbles

def binaryConverter(binary): 
    binary_map = {'0000': 0, '0001': 1, '0010': 2, '0011': 3, 
                  '0100': 4, '0101': 5, '0110': 6, '0111': 7, 
                  '1000': 8, '1001': 9, '1010': 10, '1011': 11, 
                  '1100': 12, '1101': 13, '1110': 14, '1111': 15} 

    return [binary_map[i] for i in nibbleReader(binary)]

def bearings(data, bearingStart, numBearings): 
    '''
    Make a list of sonar bearings
    '''
    n = 0 
    bearings = [] 
    for i in range(numBearings): 
        x = data[bearingStart + n:bearingStart + n + 2] 
        data_format = "<h" 
        bearing = struct.unpack(data_format, x)[0] / 100 
        bearings.append(bearing) 
        n += 2 
    
    filtered_bearings = bearings[48:208]

    return filtered_bearings 

def payload(data, rangeCount, rangeResolution, time, position, bearings): 
    payloadStart = position + 2088
    all_data = []
    upperRangeCutoff = rangeCount * 0.98
    lowerRangeCutoff = rangeCount * 0.02

    for i in range(rangeCount): 
        intensities = [] 
        for v in range(128): 
            x = data[payloadStart + i * 128 + v: payloadStart + i * 128 + v + 1] 
            try:
                sonar = struct.unpack("<B", x)[0] 
            except struct.error:
                pass
            b = format(sonar, '08b') 
            nibble = binaryConverter(str(b)) 
            intensities.extend(nibble) 
            
        all_data.append(intensities) 
    
    out_data = [] 

    all_data_np = np.array(all_data)

    # Slice columns 48 to 207 (Python excludes the last index)
    filtered_data = all_data_np[:, 48:208]  # Shape: (num_rows, 160)

    # Loop through bearings and grab column i efficiently
    for i, bearing in enumerate(bearings):
        pings = filtered_data[:, i]  # Just one slice, super fast
        for col_index, ping in enumerate(pings):
            # ping is the intensity value
            if ping > 0 and col_index < upperRangeCutoff and col_index > lowerRangeCutoff:
                new_row = [bearing, col_index, rangeResolution, ping, (col_index * rangeResolution), time]
                out_data.append(new_row)

    return out_data  

if __name__ == "__main__":
    main()

