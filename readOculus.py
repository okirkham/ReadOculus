import struct
import pandas as pd
from datetime import datetime as dt 

oculus = r"C:\Users\0w3nk\Documents\Masters\ROV\Oculus_20240823_211229.oculus.old"

oculusBinary = open(oculus, mode='rb')

def main():
    sonarData = oculusBinary.read()
    
    # define constant value sizes
    start = 48
    logSize = 242
    bearingStart = start + logSize

    headerData = header(sonarData)

    dfSonarMeta = sonarLogHeader(sonarData, start, logSize)

    numBearings = dfSonarMeta['bearingCount'].values[0]
    messageSize = dfSonarMeta['messageSize'].values[0]
    rangeCount = dfSonarMeta['rangeCount'].values[0]
    fileSize = len(sonarData)

    df = payload(sonarData, bearingStart, numBearings, rangeCount)

    df.to_csv(r"C:\Users\0w3nk\Documents\Masters\ROV\Oculus_20240823_211229.csv", index=False)  

    numItems = int((fileSize-48)/(messageSize+40))

    print(numItems)

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
    data_payload[4]                                      # time   
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
    data_payload[36]                                     # 
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
    out4bit = [] 
    for i in nibbleReader(binary):
        if i == '0000': 
            out4bit.append(0) 
        elif i == '0001': 
            out4bit.append(1) 
        elif i == '0010': 
            out4bit.append(2) 
        elif i == '0011': 
            out4bit.append(3) 
        elif i == '0100': 
            out4bit.append(4) 
        elif i == '0101': 
            out4bit.append(5) 
        elif i == '0110': 
            out4bit.append(6) 
        elif i == '0111': 
            out4bit.append(7) 
        elif i == '1000': 
            out4bit.append(8) 
        elif i == '1001': 
            out4bit.append(9) 
        elif i == '1010': 
            out4bit.append(10) 
        elif i == '1011': 
            out4bit.append(11) 
        elif i == '1100': 
            out4bit.append(12) 
        elif i == '1101': 
            out4bit.append(13) 
        elif i == '1110': 
            out4bit.append(14) 
        elif i == '1111': 
            out4bit.append(15) 
    return out4bit

def payload(data, bearingStart, numBearings, rangeCount):
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

    payloadStart = bearingStart + n + 1334 
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
        df = pd.DataFrame(intensities, columns=[f'{i}']) 
        dfList.append(df) 

    dfc = pd.concat(dfList, axis=1)
    
    return dfc

if __name__ == "__main__":
    main()

