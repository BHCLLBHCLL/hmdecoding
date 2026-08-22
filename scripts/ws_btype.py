
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments
from decoder import _parse_b_type

p = load_payload("WS_3.2_3d_tetra_finish.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
print("WS ns:", ns, "segs:", segs)
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_b_type(p, sh, cnt, ns[1], rm, Y, max_rec=5)
    print(f"  seg{segid}: {'OK' if got else 'FAIL'}")
    if got:
        print("    sample:", {k: v for k, v in list(got.items())[:3]})
