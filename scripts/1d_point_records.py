import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 点 2@0x248 点 3@0x36d 点 4@0x492 — dump 各记录前 64 字节
for base in (0x248, 0x36d, 0x492):
    out.append(f"=== around 0x{base:x} (点坐标 (5,5,0)/(-5,5,0)/(-5,-5,0)) ===")
    for off in range(base - 0x30, base + 0x28, 4):
        v = u32(off); dv = d64(off)
        tag = ""
        if abs(dv) < 20 and dv != 0:
            tag = f" d={dv:.3f}"
        if 1 <= v <= 50:
            tag += " <id?>"
        out.append(f"0x{off:04x}  u32={v:>9}{tag}")
open("output/ground_truth/1d_point_records.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
