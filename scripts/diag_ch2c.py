"""字节搜索 chapter2_2 节点坐标定位记录."""
import sys, struct
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\chapter2_2.hm")

targets = [(1, 55.68956, 80.41011, 0.0), (5, 100.0, 72.0, 0.0)]
for nid, tx, ty, tz in targets:
    pat = struct.pack("<d", tx)
    hits = []
    j = 0
    while True:
        j = p.find(pat, j)
        if j < 0:
            break
        hits.append(j); j += 1
    print(f"nid {nid} x={tx}: {len(hits)} hits @ {hits[:8]}")
    for h in hits[:3]:
        lo = max(0, h - 24)
        print(f"  @{h}: ctx=[{p[lo:h+40].hex(' ')}]")
        # 尝试各布局
        for base in range(max(0, h - 24), h + 1, 4):
            x = d64(p, base) if base + 8 <= len(p) else 0
            if abs(x - tx) < 1e-4:
                n = u32(p, base - 12) if base >= 12 else 0
                z4 = u32(p, base - 8) if base >= 8 else -1
                z4b = u32(p, base - 4) if base >= 4 else -1
                print(f"    cand base={base} nid@-12={n} z4@-8={z4} z4@-4={z4b}")
