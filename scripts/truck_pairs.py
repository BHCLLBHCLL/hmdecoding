
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments
from decoder import _parse_a_type

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if segid in (2000280, 2000310, 2000001):
        got = _parse_a_type(p, sh, cnt, ns[1], rm, max_rec=2000) if X == 3 else None
        if got:
            ks = sorted(got.keys())
            print(f"seg{segid}: cnt={cnt} Y={Y} eids={ks[:3]}..{ks[-3:] if len(ks) > 2 else ''} n={len(ks)}")
        else:
            print(f"seg{segid}: FAIL Y={Y}")
