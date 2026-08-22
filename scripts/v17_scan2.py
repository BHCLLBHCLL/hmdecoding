
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
t0 = time.time()
pat = b"\x00\x00\x00\x00\x01\x00\x00\x00"
cands = []
start = 8_200_000
while True:
    i = p.find(pat, start)
    if i < 0: break
    base = i - 4
    if base >= 0:
        nid = u32(p, base)
        if 1 <= nid <= 10_000_000:
            cands.append(base)
    start = i + 1
print(f"cands after 8.2MB: {len(cands)} in {time.time()-t0:.1f}s")
print("first 10:", cands[:10])
# verify first few as 68B streams
for cb in cands[:6]:
    ok = 0
    for k in range(10):
        rec = cb + k*68
        if 1 <= u32(p, rec) <= 10_000_000 and u32(p, rec+4) == 0 and 1 <= u32(p, rec+8) <= 16 and abs(d64(p, rec+12)) < 1e9:
            ok += 1
        else:
            break
    print(f"  cand@{cb}: ok10={ok}")
