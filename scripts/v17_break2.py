
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\dummy_positioner.hm")
base = 197811
rec = base + 116734 * 68
print("break rec:", rec)
for off in range(-8, 88, 4):
    print(f"  {off:+4d}: {p[rec+off:rec+off+4].hex()} u32={u32(p,rec+off):>10d}")
# next block after break
nxt = None
for j in range(rec + 16, min(rec + 400000, len(p) - 8)):
    nid = u32(p, j)
    if 1 <= nid <= 10_000_000 and u32(p, j+4) == 0 and 1 <= u32(p, j+8) <= 16 and abs(d64(p, j+12)) < 1e9:
        ok = 1
        for k in range(1, 4):
            n2 = u32(p, j + k*68)
            if not (1 <= n2 <= 10_000_000 and u32(p, j+k*68+4) == 0 and 1 <= u32(p, j+k*68+8) <= 16):
                ok = 0; break
        if ok:
            nxt = j
            break
print("next block:", nxt, "delta:", (nxt - rec) if nxt else None)
if nxt:
    for k in range(3):
        r2 = nxt + k*68
        print(f"  block2 rec{k}: id={u32(p, r2)} mark={u32(p, r2+8)} x={d64(p, r2+12):.4g}")
