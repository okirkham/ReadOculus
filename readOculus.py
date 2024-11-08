import struct
import pandas as pd
from datetime import datetime, timezone
import numpy as np

oculus = r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2023-07-17_18-12-24\sonar\Oculus_20230717_181225.oculus.old"

def main():
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
    Bdf = bearings(sonarData, bearingStart, numBearings)

    # calculate estimate message size
    size = dfSonarMeta['messageSize'].values[0]

    true_size = size + 40

    numItems = int((fileSize-48)/true_size)
    
    # create message size
    messageSize = 0

    
    final_df = pd.DataFrame(columns=[['bearing', 'rangeLine', 'Intensity', 
                                    'distance (m)', 'time', 'heading', 
                                    'pitch', 'roll']])

    for item in range(0,numItems):
        sonarMeta = sonarLogHeader(sonarData, position, logSize)

        # extract key values
        rangeCount = sonarMeta['rangeCount'].values[0]
        rangeResolution = sonarMeta['rangeResolution'].values[0]
        time = sonarMeta['time'].values[0]
        heading = sonarMeta['heading'].values[0]
        pitch = sonarMeta['pitch'].values[0]
        roll = sonarMeta['roll'].values[0]
        messageSize = sonarMeta['messageSize'].values[0]

        # extract sonar data for item
        df = payload(sonarData, rangeCount, rangeResolution, time, position, heading, pitch, roll, Bdf)

        position = position + messageSize + 40
        
        print(f'{(position/fileSize)*100}% complete')

        final_df = pd.concat([final_df, df])

    final_df.to_csv(r"C:\Users\0w3nk\Documents\Masters\ROV\DEEP_TREKKER_MISSION-PACKAGE_2023-07-17_18-12-24\Oculus_20230717_181225.csv", index=False) 

    oculusBinary.close()


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
    data_payload[37]                                     # 
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
    dfb = pd.DataFrame([0],  columns =  ["bearings"]) # 0 is a placeholder value that gets overwritten by the first bearing
    n = 0
    bearings = []

    for i in range(numBearings):
        x = data[bearingStart+n:bearingStart+n+2]
        data_format = "<h"
        bearing = struct.unpack(data_format, x)[0]/100
        bearings.append(bearing)
        n += 2

    dfb = pd.DataFrame(bearings, columns=["bearings"])

    return dfb

def payload(data, rangeCount, rangeResolution, time, position, heading, pitch, roll, dfb):

    payloadStart = position + 2136
    dfList = [dfb] 
    for i in range(rangeCount): 
        intensities = [] 

        for v in range(128): 
            x = data[payloadStart + i*128 + v: payloadStart + i*128 + v + 1] 
            sonar = struct.unpack("<B", x)[0]
            b = format(sonar, '08b')
            nibble = binaryConverter(str(b))
            for f in nibble:
                intensities.append(f) 
        df = pd.DataFrame(intensities, columns=[f'{i+1}']) 
        dfList.append(df) 

    dfc = pd.concat(dfList, axis=1)

    new_data = [] 
    for index, row in dfc.iloc[1:].iterrows():  
        max_value = row.iloc[2:].max()
        if max_value > 14:
            max_col_header = row.iloc[1:].idxmax()
            new_row = [row.iloc[0], max_col_header, max_value, (int(max_col_header)*rangeResolution), time, heading, pitch, roll] 
            new_data.append(new_row)
        else:
            pass
    
    new_columns = ['bearing', 'rangeLine', 'Intensity', 'distance (m)', 'time', 'heading', 'pitch', 'roll'] 

    out_df = pd.DataFrame(new_data, columns=new_columns)
    
    return out_df

if __name__ == "__main__":
    main()

