
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_a_geom, _parse_b_type, _parse_a_type

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
for i, (sh, segid, cfg71, cnt, X, Y) in enumerate(segs):
    nxt = segs[i+1][0] if i+1 < len(segs) else len(p)
    if X == 3 and Y == 3:
        got = _parse_a_geom(p, sh, nxt, cnt, ns[1], rm, max_rec=None)
        print(f"seg{segid} (Y=3): cnt={cnt} geom={len(got) if got else 0}")
    elif X == 2:
        got = _parse_b_type(p, sh, cnt, ns[1], rm, Y, max_rec=None)
        print(f"seg{segid} (X=2,Y={Y}): cnt={cnt} btype={len(got) if got else 0}")
    else:
        got = _parse_a_type(p, sh, cnt, ns[1], rm, max_rec=None)
        print(f"seg{segid} (Y={Y}): cnt={cnt} atype={len(got) if got else 0}")
