import gzip, struct
def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])
p2 = load("v1913_geom02_p2")
def d64(o): return struct.unpack_from("<d", p2, o)[0]
out = []
for off in range(0x580, 0x5d0, 1):
    dv = d64(off)
    if abs(dv) < 1000 and dv != 0:
        out.append(f"d64@{hex(off)} = {dv:.6f}")
open("output/ground_truth/p2_d64s.txt", "w", encoding="utf-8").write("\n".join(out))
# 原始字节 0x580-0x5d0
out2 = []
for off in range(0x580, 0x5d0, 16):
    chunk = p2[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    out2.append(f"0x{off:04x}  {hexs}")
open("output/ground_truth/p2_bytes.txt", "w", encoding="utf-8").write("\n".join(out2))
print("done")
