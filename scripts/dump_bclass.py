
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
SEGS = {"bottle.hm": 45421, "housing.hm": 1039309, "propeller.hm": 480895, "fe_only.hm": 4748145}
for fname, seg_hdr in SEGS.items():
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    p = load_payload(path)
    info = gt[fname]
    ns = find_node_section(p)
    hdr, ncount, shift, idoff, coordoff = ns[0]
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    id2row = {nid: k + 1 for k, nid in enumerate(ids)}
    print(f"== {fname} seg={seg_hdr}")
    # anchor hit positions for all oracle elems
    hits = {}
    for eid, d in info["elems"].items():
        nds = [x for x in d["nodes"] if x]
        rows = [id2row[n] for n in nds]
        for i in range(0, len(p) - 4 * len(rows)):
            if all(u32(p, i + j * 4) == rows[j] for j in range(len(rows))):
                hits[eid] = i
                break
    print(f"   hits: {hits}")
    # dump 48 u32 from seg+16
    s = seg_hdr + 16
    for k in range(0, 48, 4):
        ws = [u32(p, s + k * 4 + j) for j in range(4)]
        print(f"   +{16 + k*4:4d}: {ws}")
