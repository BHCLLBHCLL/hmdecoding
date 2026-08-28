"""检查 SEAT_MODEL / molding1 / chapter2_2 的 @+4 vs @+8hi."""
import sys, gzip
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

def check(path, gt_file, name):
    p = load_payload(path)
    ns = find_node_section(p)
    n1, _ = parse_nodes(p, ns)
    segs = find_elem_segments(p)
    lines = open(gt_file).read().splitlines()
    gt = set(int(l) for l in lines if l.strip().isdigit())
    store, hi = [], []
    for sh, segid, cfg71, cnt, X, Y in segs:
        if X != 3:
            continue
        anchor = None
        for s in range(sh + 16, sh + 80):
            if is_const(u32(p, s)):
                anchor = s; break
        if anchor is None:
            continue
        rec = anchor
        for k in range(cnt):
            store.append(u32(p, rec + 4))
            hi.append(u32(p, rec + 8) >> 16)
            nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while nxt >= 0:
                if is_const(u32(p, nxt)): break
                nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
            if nxt < 0: break
            rec = nxt
    print(f"\n=== {name} ===  nodes={len(n1)} segs={len(segs)} oracle={len(gt)} walked={len(store)}")
    print(f"  store==gt: {sorted(store)==sorted(gt)}  store∩gt={len(set(store)&gt)}/{len(set(store))}")
    print(f"  hi==gt:    {sorted(hi)==sorted(gt)}  hi∩gt={len(set(hi)&gt)}/{len(set(hi))}")
    # 每个记录 store 与 hi 是否相等
    same = sum(1 for a,b in zip(store,hi) if a==b)
    print(f"  store==hi 记录数: {same}/{len(store)}")
    if store:
        print(f"  store范围 {min(store)}..{max(store)}  hi范围 {min(hi)}..{max(hi)}")

check(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm",
      "output/ground_truth/seatmodel_elemids.txt", "SEAT_MODEL")
check(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm",
      "output/ground_truth/fa3_elemids.txt", "frame_assembly_3")
check(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly_1.hm",
      "output/ground_truth/fa1_elemids.txt", "frame_assembly_1")
