import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
for mark in (0x40008125, 0x40008126, 0x40008127, 0x40008152, 0x4000812A):
    hits = []
    for i in range(len(p) - 8):
        if u32(i) == mark:
            hits.append(i)
    out.append(f"0x{mark:08x}: {[hex(h) for h in hits]}")
    for h in hits[:3]:
        ctx = [u32(h + j) for j in range(-12, 24, 4)]
        out.append(f"  @0x{h:x}: ctx={ctx}")
open("output/ground_truth/marks_meta.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
