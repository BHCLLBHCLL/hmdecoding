"""验证: truck Y=1 真实 eid = u32(rec+10) (跨 @+8hi 与 @+12 低16位的 misaligned u32)."""
import sys
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
segs = find_elem_segments(p)
lines = open("output/ground_truth/truck_elemids.txt").read().splitlines()
gt = set(int(l) for l in lines if l.strip().isdigit())

# 对 Y=1 段, 提取多种候选 eid
for Y in (1,):
    eid10 = []   # u32(rec+10)
    eid4 = []    # u32(rec+4)
    eid8hi = []  # @+8>>16
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
            eid10.append(u32(p, rec + 10))
            eid4.append(u32(p, rec + 4))
            eid8hi.append(u32(p, rec + 8) >> 16)
            nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while nxt >= 0:
                if is_const(u32(p, nxt)): break
                nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
            if nxt < 0: break
            rec = nxt
    print(f"Y={Y}: walked={len(eid10)}")
    print(f"  u32(rec+10) ∩ gt: {len(set(eid10)&gt)}/{len(set(eid10))}  相等={sorted(eid10)==sorted(gt)}")
    print(f"  u32(rec+4)  ∩ gt: {len(set(eid4)&gt)}/{len(set(eid4))}")
    print(f"  @+8hi       ∩ gt: {len(set(eid8hi)&gt)}/{len(set(eid8hi))}")
    if eid10:
        print(f"  u32(rec+10) 范围: {min(eid10)}..{max(eid10)}")
