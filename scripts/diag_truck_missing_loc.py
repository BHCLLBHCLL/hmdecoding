"""truck 剩余 15911 缺失定位: 哪个段 (Y值/segid) 包含 eid 212715+."""
import sys
from collections import Counter, defaultdict
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     find_elem_segments, is_const, decode)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

m = decode(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
dec = set(m.elements.keys())
missing = sorted(gt - dec)
miss_set = set(missing)
print("missing:", len(missing))

# 逐段统计: 该段记录 (用 family-1 的 @+18 或标准 @+8hi 提取 eid) 命中缺失集的数量
# 对每个段, 尝试两种 eid 提取: f1(@+18) 和 std(@+8hi)
print("\n=== 段级命中缺失集 ===")
hits_by_seg = []
for sh, segid, cfg71, cnt, X, Y in segs:
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s; break
    if anchor is None:
        continue
    rec = anchor
    f1_hit = 0
    std_hit = 0
    v8_marker = Counter()
    for k in range(cnt):
        v8 = u32(p, rec + 8)
        v8_marker[v8 >> 16] += 1
        f1_eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        std_eid = v8 >> 16
        if f1_eid in miss_set:
            f1_hit += 1
        if std_eid in miss_set:
            std_hit += 1
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)): break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0: break
        rec = nxt
    if f1_hit or std_hit:
        hits_by_seg.append((f1_hit, std_hit, Y, segid, cnt))
        if f1_hit or std_hit:
            top = v8_marker.most_common(3)
            print(f"seg {segid} Y={Y} cnt={cnt} f1_hit={f1_hit} std_hit={std_hit} v8hi_top={top}")

print(f"\n共 {len(hits_by_seg)} 个段命中缺失集")
print("按 Y 汇总命中:", Counter(s[2] for s in hits_by_seg))
print("f1 总命中:", sum(s[0] for s in hits_by_seg), "std 总命中:", sum(s[1] for s in hits_by_seg))
