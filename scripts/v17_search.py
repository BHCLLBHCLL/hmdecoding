
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
x, y, z = -2071.821533, 597.444336, 333.329773
# search d64 bytes with tolerance: try exact and f32-quantized
import itertools
best = None
for sx in (x, round(x, 4), round(x, 5)):
    bx = struct.pack("<d", sx)
    i = p.find(bx)
    if i >= 0:
        print("x hit at", i, "sx=", sx)
        best = i
        break
if best is None:
    print("no exact x hit; scanning coords")
    # scan for d64 x near value
    cnt = 0
    for i in range(0, len(p) - 24, 4):
        v = d64(p, i)
        if abs(v - x) < 1e-3:
            cnt += 1
            if cnt <= 3:
                print("  cand:", i, d64(p, i), d64(p, i+8), d64(p, i+16))
    print("cands:", cnt)
