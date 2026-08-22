import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
for v in (18, 19, 20, 21, 36, 37, 38, 39):
    hits = []
    for off in range(0, len(p) - 4, 4):
        if u32(off) == v:
            hits.append(off)
    out.append(f"u32 {v} (4对齐): {[hex(h) for h in hits]}")
# 对齐 u32 18 的上下文
for h in [o for o in range(0, len(p)-4, 4) if u32(o) == 18]:
    ctx = [u32(o) for o in range(h - 16, h + 32, 4)]
    out.append(f"u32 18 @0x{h:x}: ctx={ctx}")
open("output/ground_truth/line18_aligned.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
