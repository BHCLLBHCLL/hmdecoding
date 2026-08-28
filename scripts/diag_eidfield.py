"""多文件 @+4 vs @+8hi vs oracle 对照, 判断真实 eid 字段位置."""
import sys, gzip
from collections import Counter
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

def check(path, gt_file):
    p = load_payload(path)
    ns = find_node_section(p)
    n1, _ = parse_nodes(p, ns)
    segs = find_elem_segments(p)
    lines = open(gt_file).read().splitlines()
    gt = set(int(l) for l in lines if l.strip().isdigit())
    store, hi = [], []
    for sh, segid, cfg71, cnt, X, Y in segs:
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
    print(f"\n=== {path.split('/')[-1]} ===  nodes={len(n1)} segs={len(segs)}")
    print(f"  oracle={len(gt)}  walked={len(store)}")
    print(f"  store==gt: {sorted(store)==sorted(gt)}  store∩gt={len(set(store)&gt)}/{len(set(store))}")
    print(f"  hi==gt:    {sorted(hi)==sorted(gt)}  hi∩gt={len(set(hi)&gt)}/{len(set(hi))}")
    # hi 值范围
    if hi:
        print(f"  store范围 {min(store)}..{max(store)}  hi范围 {min(hi)}..{max(hi)}")

check(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm",
      "output/ground_truth/fa3_elemids.txt")
check(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm",
      "output/ground_truth/truck_elemids.txt")
check(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly_1.hm",
      "output/ground_truth/fa1_elemids.txt")
