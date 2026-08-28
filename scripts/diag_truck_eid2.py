"""truck 深挖: 各 Y 段 @+4/@+8hi 范围 + 当前 decode 缺失 eid 定位."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, is_const, decode)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

# 各 Y 段 @+4 / @+8hi 范围
print("=== 各 Y 段 @+4/@+8hi 范围 ===")
for Y in (1, 2, 4, 7):
    stores = []
    his = []
    for sh, segid, cfg71, cnt, X, yy in segs:
        if yy != Y:
            continue
        anchor = None
        for s in range(sh + 16, sh + 80):
            if is_const(u32(p, s)):
                anchor = s; break
        if anchor is None:
            continue
        rec = anchor
        for k in range(cnt):
            stores.append(u32(p, rec + 4))
            his.append(u32(p, rec + 8) >> 16)
            nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while nxt >= 0:
                if is_const(u32(p, nxt)): break
                nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
            if nxt < 0: break
            rec = nxt
    if stores:
        print(f"Y={Y}: store [{min(stores)}..{max(stores)}] hi [{min(his)}..{max(his)}] "
              f"hi∩gt={len(set(his)&gt)}/{len(set(his))} store∩gt={len(set(stores)&gt)}/{len(set(stores))}")

# 当前 decode 结果
m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
dec = set(m.elements.keys())
missing = sorted(gt - dec)
extra = sorted(dec - gt)
print(f"\n当前 decode: {len(dec)} oracle {len(gt)}")
print(f"missing {len(missing)}: 首20 {missing[:20]} 尾10 {missing[-10:]}")
print(f"extra {len(extra)}: 首20 {extra[:20]}")

# 缺失 eid 区间分布
ranges = []
for v in missing:
    if ranges and v == ranges[-1][1] + 1:
        ranges[-1][1] = v
    else:
        ranges.append([v, v])
print(f"缺失区间数 {len(ranges)}: {ranges[:20]}")
