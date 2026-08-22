import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
for off in range(0x480, 0x760, 4):
    v = u32(off)
    dv = d64(off)
    tag = ""
    if 1 <= v <= 20:
        tag = " <== id?"
    elif abs(dv) < 10 and dv != 0:
        tag = f" <== d={dv:.4f}"
    out.append(f"0x{off:04x}  u32={v:>9}  d={dv:>10.4f}{tag}")
open("output/ground_truth/leg_geom_480.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
