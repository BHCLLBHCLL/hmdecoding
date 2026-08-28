"""truck Y=2 family-1 @+18 eid 覆盖 vs 缺失区间."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

# Y=2 段 family-1 @+18 eid 收集
f1_eids = []
f1_fail = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    if Y != 2:
        continue
    anchor = None
    for s in range(sh + 16, sh + 80):
        if is_const(u32(p, s)):
            anchor = s; break
    if anchor is None:
        continue
    rec = anchor
    for k in range(cnt):
        eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
        # family-1 检测条件
        ok = (u32(p, rec + 8) in (0x02BD0002, 0x02AE0002)
              and u16(p, rec + 12) == 2596
              and u32(p, rec + 4) >= 2_000_000
              and u32(p, rec + 4) != eid
              and 0 < eid < 10_000_000)
        if ok:
            f1_eids.append(eid)
        else:
            f1_fail += 1
        nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
        while nxt >= 0:
            if is_const(u32(p, nxt)): break
            nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
        if nxt < 0: break
        rec = nxt

print(f"Y=2 family-1 检测成功: {len(f1_eids)} 失败: {f1_fail}")
if f1_eids:
    print(f"f1 eid 范围: {min(f1_eids)}..{max(f1_eids)}")
    # 缺失区间内有多少 f1 eid
    miss = [e for e in f1_eids if 212715 <= e <= 228633]
    print(f"f1 eid 落在缺失区间 [212715,228633]: {len(miss)}")
# f1 eid 覆盖哪些 oracle 区间
s = set(f1_eids)
print(f"f1 eid 唯一数: {len(s)} 与 oracle 交集: {len(s & gt)}")
