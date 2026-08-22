
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
for fname in ["bottle.hm", "housing.hm", "fe_only.hm", "quality_index.hm", "yoke.hm", "propeller.hm", "dummy.hm", "molding1.hm", "truck.hm", "car_section.hm", "cover.hm", "SEAT_MODEL.hm"]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    info = gt.get(fname)
    print(f"== {fname} len={len(p)} node_hdr={ns[0][0] if ns else None} node_count={ns[0][1] if ns else None}")
    if not ns or not info: continue
    hdr, ncount, shift, idoff, coordoff = ns[0]
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    id2row = {nid: k + 1 for k, nid in enumerate(ids)}
    print(f"   node ids: first5={ids[:5]} last3={ids[-3:]} max={max(ids) if ids else 0}")
    for eid, d in list(info["elems"].items())[:2]:
        nds = [x for x in d["nodes"] if x]
        rows = [id2row.get(n) for n in nds]
        print(f"   E{eid} nds={nds} rows={rows}")
        for label, seq in (("ids", nds), ("rows", rows)):
            if any(x is None for x in seq): continue
            hits = []
            for i in range(0, len(p) - 4 * len(seq)):
                if all(u32(p, i + j * 4) == seq[j] for j in range(len(seq))):
                    hits.append(i)
            if hits:
                print(f"      {label}: hits={hits[:4]}")
