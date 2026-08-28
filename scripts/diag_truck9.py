"""truck 重复 eid 来源分析."""
import sys
from collections import defaultdict
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

segs = find_elem_segments(p)
seg_eids = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        seg_eids[segid] = got

# eid -> 段列表
eid_segs = defaultdict(list)
for segid, elems in seg_eids.items():
    for eid in elems:
        eid_segs[eid].append(segid)
dups = {e: s for e, s in eid_segs.items() if len(s) > 1}
print(f"dup eids: {len(dups)}")
for e, segs in sorted(dups.items())[:12]:
    print(f"  eid {e}: segs {segs}")
