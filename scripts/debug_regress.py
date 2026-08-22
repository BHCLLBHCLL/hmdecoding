
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

# WS node section: find true [136]
p = load_payload("WS_3.2_3d_tetra_finish.hm")
hits = []
start = 0
while True:
    i = p.find(b"\x88\x00\x00\x00", start)
    if i < 0: break
    n = u32(p, i + 4)
    hits.append((i, n))
    start = i + 1
print("WS [136] hits:", [(i, n) for i, n in hits if 1 <= n <= 10_000_000][:10])
# old find_node_section v1 result
import importlib, hmdecoder.decoder as dec
print("old-style check: scan [1][136] adjacent")
for i in range(0, len(p) - 40):
    if u32(p, i + 8) == 1 and u32(p, i + 12) == 136:
        print("  [1][136]@", i, "count:", u32(p, i + 16))
        break
# body_side elem segment: check where CONST chain breaks
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
sh = 390741
s = sh + 28
print("\nbody_side: check CONST chain from", s)
breaks = []
rec = s
for k in range(120):
    if u32(p2, rec) != 0x70241FF5:
        breaks.append((k, rec))
        break
    rec += 76
print("  first break at k=", breaks if breaks else "none in 120")
# dump around break
if breaks:
    b = breaks[0][1]
    for off in range(-16, 64, 4):
        print(f"  {off:+4d}: {p2[b+off:b+off+4].hex()} u32={u32(p2, b+off)}")
