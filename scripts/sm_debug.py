
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm")
hits = []
start = 0
while True:
    i = p.find(b"\x88\x00\x00\x00", start)
    if i < 0: break
    n = u32(p, i + 4)
    if 1 <= n <= 10_000_000:
        hits.append((i, n))
    start = i + 1
print("plausible 136 hits:", len(hits))
print("sorted top10:", sorted(hits, key=lambda h: -h[1])[:10])
hi, count = 110269, 34296
print("is (110269, 34296) in hits:", (110269, 34296) in hits)
base = 110293
for k in range(10):
    rec = base + k * 56
    x = d64(p, rec + 4)
    nid = u32(p, rec + 44) - 1
    tail = u32(p, rec + 48) == 0 and u32(p, rec + 52) == 0
    print(f"  k={k}: nid={nid} x={x:.3f} tail={tail}")
