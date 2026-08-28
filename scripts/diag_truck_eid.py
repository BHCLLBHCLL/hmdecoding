"""truck 段结构深挖: 段类型分布 + 各类型 @+4/@+8hi 与 oracle 关系."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

print("nodes:", len(n1), "segs:", len(segs), "oracle:", len(gt))
print("X dist:", Counter(s[4] for s in segs))
print("Y dist:", Counter(s[5] for s in segs).most_common(15))
print("cfg71 dist:", Counter(s[2] for s in segs).most_common(15))
print("cnt sum:", sum(s[3] for s in segs))

# 按 X/Y 分组看 eid 覆盖
from collections import defaultdict
group = defaultdict(lambda: {"store": set(), "hi": set(), "cnt": 0})
for sh, segid, cfg71, cnt, X, Y in segs:
    g = group[(X, Y)]
    g["cnt"] += cnt
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s; break
    if anchor is None:
        continue
    rec = anchor
    for k in range(cnt):
        g["store"].add(u32(p, rec + 4))
        g["hi"].add(u32(p, rec + 8) >> 16)
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)): break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0: break
        rec = nxt

print("\n=== 按 (X,Y) 分组 ===")
for (X, Y), g in sorted(group.items()):
    store_ok = len(g["store"] & gt)
    hi_ok = len(g["hi"] & gt)
    print(f"(X={X},Y={Y}) cnt={g['cnt']} store∩gt={store_ok}/{len(g['store'])} hi∩gt={hi_ok}/{len(g['hi'])}")
