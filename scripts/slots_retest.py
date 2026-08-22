
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments
from decoder import _parse_b_slots

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    s2 = _parse_b_slots(p, sh, cnt, ns[1], rm, Y)
    print(f"seg{segid}: cnt={cnt} slots={len(s2) if s2 else 0}")
