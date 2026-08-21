import gzip, struct

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

p = load("v1913_03_t1")
def u32(off): return struct.unpack_from("<I", p, off)[0]

# dump config table region 0x980..0xa40
print("=== config table region 0x980..0xa80 ===")
for off in range(0x980, 0xa80, 4):
    print(f"0x{off:04x}  u32={u32(off):>10}")
