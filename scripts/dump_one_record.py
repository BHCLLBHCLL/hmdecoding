
import sys, json, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes

gt = json.load(open("output/ground_truth/multi_elem_gt.json"))
# per file: segment header offset (from earlier scans), anchor eid with smallest id
SEGS = {
  "clip_refine.hm": 972751, "frame_assembly.hm": 1949029, "head_2.hm": 56946,
  "s_bend_tube.hm": 136775, "bottle.hm": 45421, "housing.hm": 1039309,
  "fe_only.hm": 4748145, "quality_index.hm": 262089, "yoke.hm": 1811343,
  "propeller.hm": 480895, "dummy.hm": 228589, "body_side.hm": 390741,
}
for fname, seg_hdr in SEGS.items():
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    if not os.path.exists(path):
        path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    info = gt.get(fname)
    if not info: continue
    ns = find_node_section(p)
    hdr, ncount, shift, idoff, coordoff = ns[0]
    nodes, base = parse_nodes(p, hdr, ncount, shift, idoff, coordoff)
    ids = [u32(p, base + k * 52 + idoff) for k in range(ncount)]
    id2row = {nid: k + 1 for k, nid in enumerate(ids)}
    eid0 = min(info["elems"])
    d = info["elems"][eid0]
    nds = [x for x in d["nodes"] if x]
    rows = [id2row[n] for n in nds]
    hit = None
    for i in range(0, len(p) - 4 * len(rows)):
        if all(u32(p, i + j * 4) == rows[j] for j in range(len(rows))):
            hit = i; break
    print(f"== {fname} cfg={d['cfg']} n={len(rows)} eid={eid0} seg={seg_hdr} hit={hit} rel2seg={hit-seg_hdr}")
    # dump 64B before hit and 48B after
    s = hit - 64
    for off in range(s, hit + 48, 16):
        ws = [u32(p, off + j) for j in range(0, 16, 4)]
        print(f"   {off - seg_hdr:5d}: {ws}")
