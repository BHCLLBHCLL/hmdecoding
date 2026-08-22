
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes

CONST = 0x70241FF5

def find_elem_segments(p):
    segs = []
    i = 0
    while i < len(p) - 24:
        if u32(p, i) == 997:
            segid = u32(p, i + 4); cfg71 = u32(p, i + 8); cnt = u32(p, i + 12)
            X = u32(p, i + 16); Y = u32(p, i + 20)
            if X in (2, 3) and 100 <= cfg71 <= 500 and 1 <= cnt <= 10_000_000 and Y < 10_000_000 and segid < 1_000_000:
                segs.append((i, segid, cfg71, cnt, X, Y))
        i += 1
    return segs

def parse_a_type(p, s, cnt, row_count, row_map, config, maxprobe=200):
    stride = None
    for j in range(s + 24, min(s + 24 + maxprobe, len(p) - 4)):
        if u32(p, j) == CONST:
            stride = j - s
            break
    if stride is None or stride % 4:
        return None
    target = (config + 256) << 16
    fp = None
    for off in range(12, stride - 12, 4):
        if u32(p, s + off) == target:
            fp = off
            break
    if fp is None:
        return None
    nodes_off = fp + 4
    if (stride - nodes_off - 8) % 4 or stride - nodes_off < 12:
        return None
    n = (stride - nodes_off - 8) // 4
    if not (1 <= n <= 12):
        return None
    elems = {}
    for k in range(min(cnt, 10)):
        rec = s + k * stride
        if u32(p, rec) != CONST or u32(p, rec + fp) != target:
            return None
        eid = u32(p, rec + 4)
        if not (0 < eid < 10_000_000):
            return None
        nds = [u32(p, rec + nodes_off + j * 4) for j in range(n)]
        if not all(1 <= r <= row_count for r in nds):
            return None
        elems[eid] = (config, [row_map.get(r, r) for r in nds])
    return elems

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\clip_refine.hm")
ns = find_node_section(p)
hdr, ncount, shift, idoff, coordoff = ns[0]
nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
row_map = {k + 1: nid for k, nid in enumerate(ids)}
segs = find_elem_segments(p)
print("segs:", segs)
sh, segid, cfg71, cnt, X, Y = segs[0]
got = parse_a_type(p, sh + 24, cnt, ncount, row_map, cfg71 - 71)
print("type:", type(got))
if got:
    print("keys:", sorted(got.keys())[:12])
    print("E1:", got.get(1))
    gt = json.load(open("output/ground_truth/multi_elem_gt.json"))["clip_refine.hm"]
    print("GT E1:", gt["elems"]["1"])
