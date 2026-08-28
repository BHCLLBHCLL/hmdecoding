"""SEAT_MODEL 各段 @+8/@+12 结构分布."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
print("segs:", len(segs))

# 每段 @+8hi 和 u16(rec+12) 分布
for sh, segid, cfg71, cnt, X, Y in segs:
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s; break
    if anchor is None:
        print(f"seg {segid} Y={Y} cnt={cnt}: NO ANCHOR")
        continue
    rec = anchor
    v8hi = Counter()
    v12 = Counter()
    v4 = []
    for k in range(min(cnt, 5)):
        v8hi[u32(p, rec + 8) >> 16] += 1
        v12[u16(p, rec + 12)] += 1
        v4.append(u32(p, rec + 4))
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)): break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0: break
        rec = nxt
    print(f"seg {segid} Y={Y} cnt={cnt} @+8hi={dict(v8hi)} u16(+12)={dict(v12)} @+4首={v4[:3]}")
