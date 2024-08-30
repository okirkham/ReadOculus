import binascii
import struct
import pandas as pd
from datetime import datetime as dt

oculus = r"P:\ROV\DEEP_TREKKER_MISSION-PACKAGE_2023-07-18_17-32-14\sonar\Oculus_20230718_173214.oculus.old"

oculusBinary = open(oculus, mode='rb')

def test_function(sbd_hex):
    sbd_length = 44
    sbd_list = [sbd_hex[0:sbd_length]]
    for x in sbd_list:
        sbd_format = "=B3xI6s10x2h2d"
        sbd_payload = list(struct.unpack(sbd_format, x))
        
    # variables
    sbd_payload[0]                                      # fileHeader
    sbd_payload[1]                                      # sizeHeader
    sbd_payload[2]                                      # source
    sbd_payload[3]                                      # version
    sbd_payload[4]                                      # encryption
    sbd_payload[5]                                      # key
    sbd_payload[6]                                      # time

    hdrs = [
        "fileHeader",
        "sizeHeader",
        "source",
        "version",
        "encryption",
        "key",
        "time",
    ]

    df = pd.DataFrame(data=[sbd_payload], columns=hdrs)
    return df

# Test
data = oculusBinary.read(44)
print(data)
df = test_function(data)
print(df)
# ts = dt.now().strftime("%Y%m%d_%H%M%S")
# df.to_csv(f"{ts}_data.csv")

