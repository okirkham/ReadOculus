import struct

#print(struct.calcsize("2I2h4xd2xh2I4x5HIH5B4dI8xI20xI4x8dBd2H16x3I"))

# Given binary hex code
#binary_data = bytes.fromhex(hex_data)

# Define the struct format
struct_format = "<I4x5HIH5B"

# Unpack the binary data
#unpacked_data = struct.unpack(struct_format, binary_data)

# Print the unpacked data
#print(unpacked_data)

print(struct.calcsize(struct_format))