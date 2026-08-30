
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_a_geom, _parse_a_type

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\body_side_assembly.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
for i, (sh, segid, cfg71, cnt, X, Y) in enumerate(segs):
    nxt = segs[i+1][0] if i+1 < len(segs) else len(p)
    g = _parse_a_geom(p, sh, nxt, cnt, ns[1], rm, max_rec=None)
    a = _parse_a_type(p, sh, cnt, ns[1], rm, max_rec=None)
    print(f"seg{segid}: cnt={cnt} geom={len(g) if g else 0} atype={len(a) if a else 0}")
