import struct, gzip
raw = open("WS_3.2_3d_tetra_finish.hm","rb").read()
print("prefix double (bytes 4-11):", struct.unpack("<d", raw[4:12])[0])
payload = gzip.decompress(raw[12:])
print("payload head doubles/u32s:")
for off in (0,4,8,12):
    print(f"  d@0x{off:02x} = {struct.unpack('<d', payload[off:off+8])[0]}")
for off in range(0,64,4):
    v = struct.unpack("<I", payload[off:off+4])[0]
    print(f"  u32@0x{off:02x} = {v} (0x{v:08x})")
print("payload size:", len(payload), "= 0x%x" % len(payload))
