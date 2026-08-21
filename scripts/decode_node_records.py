import gzip, struct

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

p = load("v1913_04_t2")
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]

base = 0x504
for i in range(5):
    rec = base + i * 72
    print(f"node {i+1} @0x{rec:x}")
    # print every field: u32s and doubles
    for off in range(rec, rec + 72, 4):
        tag = "u32"
        print(f"  +{off-rec:02x}: {u32(off):>12}  d={d(off):.6g}" if off % 8 == 0 else f"  +{off-rec:02x}: {u32(off):>12}")
