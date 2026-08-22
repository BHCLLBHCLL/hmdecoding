
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
t0 = time.time()
hits = []
start = 0
scan_lim = min(len(p), 8_000_000)
while True:
    i = p.find(b"\x88\x00\x00\x00", start, scan_lim)
    if i < 0: break
    n = u32(p, i + 4)
    if 1 <= n <= 10_000_000:
        hits.append((i, n))
    start = i + 1
print(f"[136] hits: {len(hits)} in {time.time()-t0:.1f}s")
t0 = time.time()
cands = []
pat = b"\x00\x00\x00\x00\x01\x00\x00\x00"
start = 0
limit = min(len(p), 2_000_000)
while True:
    i = p.find(pat, start, limit)
    if i < 0: break
    base = i - 4
    if base >= 0:
        nid = u32(p, base)
        if 1 <= nid <= 10_000_000:
            cands.append(base)
    start = i + 1
print(f"struct cands: {len(cands)} in {time.time()-t0:.1f}s")
