import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
for mark in (0x4000812A, 0x40008125, 0x40008126):
    hits = []
    for off in range(0, len(p) - 4, 4):
        if u32(off) == mark:
            hits.append(off)
    out.append(f"0x{mark:08x}: {[hex(h) for h in hits]}")
    for h in hits[:4]:
        ctx = [u32(o) for o in range(h - 8, h + 40, 4)]
        out.append(f"  @0x{h:x} ctx={ctx}")
open("output/ground_truth/marker_positions.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
