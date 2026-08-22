import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
for region in (0x390, 0x6e0):
    out.append(f"=== 0x{region:x} ===")
    for off in range(region, region + 0x100, 4):
        v = u32(off); dv = d64(off)
        tag = ""
        if abs(dv) < 20 and dv != 0:
            tag = f" d={dv:.2f}"
        if 1 <= v <= 50:
            tag += " <id?>"
        out.append(f"0x{off:04x}  u32={v:>9}{tag}")
open("output/ground_truth/1d_line_regions.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
