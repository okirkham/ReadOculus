import binascii
import struct
import pandas as pd
from datetime import datetime as dt

oculus = r"P:\ROV\DEEP_TREKKER_MISSION-PACKAGE_2023-07-18_17-32-14\sonar\Oculus_20230718_173214.oculus.old"

oculusBinary = open(oculus, mode='rb')

def main():
    headerData = oculusBinary.read(44)
    
    df = header(headerData)
    print(df)

def header(data):
    data_length = 44
    data_list = [data[0:data_length]]
    for x in data_list:
        data_format = "=B3xI6s10x2h2d"
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

def sonarData(data):
    data_length = len(data)
    data_list = [data[0:data_length]]
    for x in data_list:
        data_format = "=B3xI6s10x2h2d"
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

if __name__ == "__main__":
    main()

