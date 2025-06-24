import struct
import pandas as pd
from datetime import datetime, timezone
import os 

def main():
    # filter settings
    filter = False

    # input misson package path
    base_path = r"C:\Users\0w3nk\Documents\ROV\DEEP_TREKKER_MISSION-PACKAGE_2025-02-07_14-19-17"

    sonar = os.path.join(base_path, "sonar")

    binaryfile = find_oculus(sonar)

    oculus = os.path.join(base_path, "sonar", binaryfile)

    # create output csv path
    out_csv_name = binaryfile.replace("oculus", "csv")

    out_csv = os.path.join(base_path, "sonar", out_csv_name)

    oculusBinary = open(oculus, mode='rb')

    sonarData = oculusBinary.read()
    fileSize = len(sonarData)

    # define constant value sizes 
    position = 48
    logSize = 242
    bearingStart = position + logSize

    headerData = header(sonarData)

    dfSonarMeta = sonarLogHeader(sonarData, position, logSize)

    # find beam bearings
    numBearings = dfSonarMeta['bearingCount'].values[0]
    bearingList = bearings(sonarData, bearingStart, numBearings, filter)

    # calculate estimate message size
    size = dfSonarMeta['messageSize'].values[0]

    true_size = size + 40

    numItems = int((fileSize-48)/true_size)
    
    # create message size
    messageSize = 0

    # create final list
    final_list = []

    # create chunk processing threshold
    threshold = 10

    for item in range(0,numItems):
        if position + logSize > fileSize: 
            break

        sonarMeta = sonarLogHeader(sonarData, position, logSize)

        # extract key values
        rangeCount = sonarMeta['rangeCount'].values[0]
        rangeResolution = sonarMeta['rangeResolution'].values[0]
        time = sonarMeta['time'].values[0]
        messageSize = sonarMeta['messageSize'].values[0]

        # extract sonar data for item
        dataList = payload(sonarData, rangeCount, rangeResolution, time, position, bearingList, filter)

        position = position + messageSize + 40
        
        progress = (position/fileSize)*100

        final_list.append(dataList)

        if progress > threshold:
            print(f'{progress}% complete')
            flat_data = [item for sublist in final_list for item in sublist]
            final_df = pd.DataFrame(flat_data, columns=['bearing', 'rangeLine', 'rangeResolution', 'Intensity', 
                                    'distance', 'timestamp'])

            final_df = final_df.sort_values('timestamp') 

            # clearing memory
            final_list = []
            #del final_df 
            del flat_data
            #del metadf

            if threshold == 10:
                final_df.to_csv(out_csv, mode = 'a', index=False)
            else:
                final_df.to_csv(out_csv, mode = 'a', header=False, index=False)

            if threshold < 90:
                threshold += 10
            else:
                threshold += 1
            #del merged
            del final_df

    print('100% complete')
    oculusBinary.close()

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

def bearings(data, bearingStart, numBearings, filter): 
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

    if filter is True:
        return filtered_bearings 
    else:
        return bearings
    
def payload(data, rangeCount, rangeResolution, time, position, bearings, filter): 
    payloadStart = position + 2136 
    all_data = []

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
    
    if filter is True:
        filtered_data = [row[48:208] for row in all_data]

        # Calculate dynamic range indices
        first_third_end = rangeCount // 3  # End index of first 1/3
        last_third_start = 2 * (rangeCount // 3)  # Start index of last 1/3

        # Apply 0.5 weight to the first 1/3 of the data
        for i in range(first_third_end):  
            filtered_data[i] = [x * 0.5 for x in filtered_data[i]]

        # Apply 0.5 weight to the last 1/3 of the data
        for i in range(last_third_start, rangeCount):  
            filtered_data[i] = [x * 0.1 for x in filtered_data[i]]

        # Apply 0.1 weight to values > 4, 0.5 to all others in the middle 1/3 of the data
        for i in range(first_third_end, last_third_start):  # Middle range lines
            filtered_data[i] = [x * 0.1 if x > 4 else x * 2 for x in filtered_data[i]]  # Modify only values > 6

        for i, bearing in enumerate(bearings): 
            if i < len(filtered_data): 
                pings = [row[i] for row in filtered_data]
                if len(pings) > 2: 
                    max_value = max(pings) 
                    if max_value > 1: 
                        max_col_index = pings.index(max_value) 
                        new_row = [bearing, max_col_index, rangeResolution, max_value, (max_col_index * rangeResolution), time] 
                        out_data.append(new_row)
        return out_data
    else:
        for i, bearing in enumerate(bearings): 
            if i < len(all_data): 
                pings = [row[i] for row in all_data]
                if len(pings) > 2: 
                    max_value = max(pings) 
                    if max_value > 1: 
                        max_col_index = pings.index(max_value) 
                        new_row = [bearing, max_col_index, rangeResolution, max_value, (max_col_index * rangeResolution), time] 
                        out_data.append(new_row)

        return out_data     

if __name__ == "__main__":
    main()

