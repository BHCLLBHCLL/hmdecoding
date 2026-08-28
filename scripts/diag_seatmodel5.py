"""SEAT_MODEL 段级合并模拟, 找重复 eid."""
import sys
from collections import defaultdict
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)

eid_segs = defaultdict(list)
sum_n = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        sum_n += len(got)
        for eid in got:
            eid_segs[eid].append(segid)
dups = {e: s for e, s in eid_segs.items() if len(s) > 1}
print(f"sum={sum_n} unique={len(eid_segs)} dups={len(dups)} extra={sum(len(s)-1 for s in dups.values())}")
for e, s in sorted(dups.items())[:15]:
    print(f"  eid {e}: segs {s}")
