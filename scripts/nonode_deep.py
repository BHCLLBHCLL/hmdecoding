
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

# molding1 node section at 126
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
print("== molding1 node hdr@126:", [u32(p, 126+j*4) for j in range(6)])
for k in range(0, 64, 4):
    off = 126 + 24 + k
    print(f"  +{24+k:3d}: {p[off:off+4].hex()} u32={u32(p,off):>8d} d64={d64(p,off):.4g}")

# truck: scan first element seg region for node candidates
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
print("\n== truck: scan for node-section candidates [1][136] variants / 997")
cands = []
for i in range(0, 11084188, 2):
    v = u32(p2, i)
    if v == 997 and u32(p2, i + 4) == 0:
        cands.append(("997-0", i, [u32(p2, i + 4*j) for j in range(8)]))
    elif u32(p2, i + 4) == 1 and u32(p2, i + 8) == 136 and u32(p2, i + 12) == 1:
        cands.append(("x-1-136-1", i, [u32(p2, i + 4*j) for j in range(8)]))
    if len(cands) > 10:
        break
for c in cands:
    print(" ", c)
