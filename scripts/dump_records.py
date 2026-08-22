
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
files = ["clip_refine.hm", "frame_assembly.hm", "head_2.hm", "s_bend_tube.hm", "bottle.hm",
         "housing.hm", "fe_only.hm", "quality_index.hm", "yoke.hm", "propeller.hm", "dummy.hm",
         "body_side.hm"]
for fname in files:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    if not os.path.exists(path):
        path = "WS_3.2_3d_tetra_finish.hm" if fname == "body_side.hm" else path
    p = load_payload(path)
    info = gt.get(fname)
    if not info: continue
    ns = find_node_section(p)
    hdr, ncount, shift, idoff, coordoff = ns[0]
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    id2row = {nid: k + 1 for k, nid in enumerate(ids)}
    eid0 = sorted(info["elems"])[0]
    d = info["elems"][eid0]
    nds = [x for x in d["nodes"] if x]
    rows = [id2row[n] for n in nds]
    # find first hit
    hit = None
    for i in range(0, len(p) - 4 * len(rows)):
        if all(u32(p, i + j * 4) == rows[j] for j in range(len(rows))):
            hit = i; break
    if hit is None:
        print(f"== {fname}: NO HIT (eid {eid0})"); continue
    # second element for stride
    eid1 = sorted(info["elems"])[1]
    d1 = info["elems"][eid1]
    nds1 = [x for x in d1["nodes"] if x]
    rows1 = [id2row[n] for n in nds1]
    hit2 = None
    for i in range(hit + 1, len(p) - 4 * len(rows1)):
        if all(u32(p, i + j * 4) == rows1[j] for j in range(len(rows1))):
            hit2 = i; break
    pre = []
    for j in range(10):
        pre.append(u32(p, hit - 4 * (10 - j)))
    post = [u32(p, hit + 4 * len(rows) + j) for j in range(6)]
    print(f"== {fname} cfg={d['cfg']} n={len(rows)} eid={eid0} hit={hit} hit2={hit2} stride={hit2-hit if hit2 else '?'}")
    print(f"   pre10 : {pre}")
    print(f"   nodes : {rows}")
    print(f"   post6 : {post}")
