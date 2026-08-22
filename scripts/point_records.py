import gzip, struct
def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])
p1 = load("v1913_geom01_p1")
p2 = load("v1913_geom02_p2")
def u32(o): return struct.unpack_from("<I", p2, o)[0]
def d64(o): return struct.unpack_from("<d", p2, o)[0]
out = []
out.append("=== p2 (两个点) 0x540..0x650 ===")
for off in range(0x540, 0x650, 4):
    v = u32(off); dv = d64(off)
    tag = ""
    if abs(dv) < 100 and dv != 0:
        tag = f" d={dv:.3f}"
    if 1 <= v <= 3:
        tag += " <id?>"
    out.append(f"0x{off:04x}  u32={v:>9}{tag}")
open("output/ground_truth/point_records.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
