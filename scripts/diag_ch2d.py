"""chapter2_2 节点记录标记 0x10200bc7 间距分析."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\chapter2_2.hm")
MARK = (0x10200bc7).to_bytes(4, "little")
hits = []
j = 0
while True:
    j = p.find(MARK, j)
    if j < 0:
        break
    hits.append(j); j += 1
print(f"mark hits: {len(hits)}")
if len(hits) > 2:
    diffs = [b - a for a, b in zip(hits, hits[1:])]
    from collections import Counter
    print("spacing:", Counter(diffs).most_common(6))
# 前几条记录
for h in hits[:4]:
    print(f"\n@{h}: nid={u32(p,h+12)} z4={u32(p,h+4)} z8={u32(p,h+8)}")
    for off in (0, 4, 8, 12, 16, 20, 24, 28, 36, 44, 52, 60, 68, 76):
        q = h + off
        print(f"  +{off:2d}: {p[q:q+4].hex(' ')} u32={u32(p,q):<10d} d={d64(p,q):.5g}")
