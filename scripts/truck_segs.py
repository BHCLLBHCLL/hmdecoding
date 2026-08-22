
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, row_map_from_nodes, find_elem_segments
from decoder import _parse_a_type, _parse_b_type, _parse_b_slots

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
print("ns:", ns, "segs:", len(segs))
total = 0
fails = []
for sh, segid, cfg71, cnt, X, Y in segs:
    if X == 3:
        got = _parse_a_type(p, sh, cnt, ns[1], rm)
    else:
        got = _parse_b_type(p, sh, cnt, ns[1], rm, Y)
        g2 = _parse_b_slots(p, sh, cnt, ns[1], rm, Y)
        if g2 and (got is None or len(g2) > len(got)):
            got = g2
    n = len(got) if got else 0
    total += n
    if n < cnt:
        fails.append((segid, cnt, n))
print("decoded:", total, "of", sum(s[3] for s in segs))
print("fails (segid, cnt, got):", fails[:30])
