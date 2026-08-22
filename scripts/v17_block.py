
import sys, time
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
base = 197811
# find where 68B stream breaks
t0 = time.time()
cnt = 0
while True:
    rec = base + cnt * 68
    nid = u32(p, rec)
    x = d64(p, rec + 12)
    if not (1 <= nid <= 10_000_000) or abs(x) > 1e9 or u32(p, rec+4) != 0 or u32(p, rec+8) != 1:
        break
    cnt += 1
print(f"continuous: {cnt} in {time.time()-t0:.1f}s")
rec = base + cnt * 68
print("break rec:", rec)
for off in range(-16, 96, 4):
    print(f"  {off:+4d}: {p[rec+off:rec+off+4].hex()} u32={u32(p,rec+off):>10d}")
# after break, scan for next 68B block start (id pattern)
nxt = None
for j in range(rec + 16, min(rec + 200000, len(p) - 8), 1):
    nid = u32(p, j)
    if 1 <= nid <= 10_000_000 and u32(p, j+4) == 0 and u32(p, j+8) == 1 and abs(d64(p, j+12)) < 1e9:
        # verify 3 more
        ok = 1
        for k in range(1, 4):
            n2 = u32(p, j + k*68)
            if not (1 <= n2 <= 10_000_000 and u32(p, j+k*68+4) == 0 and u32(p, j+k*68+8) == 1):
                ok = 0; break
        if ok:
            nxt = j
            break
print("next block at:", nxt, "delta:", (nxt - rec) if nxt else None)
