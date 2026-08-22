
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
print("dummy_positioner db:", d64(p, 4), "len:", len(p))
print("head:", [u32(p, j*4) for j in range(16)])
# v14+ header: strings table? look for 997 segments
segs = []
i = 0
while i < len(p) - 24 and len(segs) < 8:
    if u32(p, i) == 997:
        segs.append((i, u32(p, i+4), u32(p, i+8), u32(p, i+12), u32(p, i+16), u32(p, i+20)))
    i += 1
print("first 997s:", segs)
