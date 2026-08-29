
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_ansys2d_elems

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
print("segs:", [(s[1], s[3], s[4], s[5]) for s in segs])
tot = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_ansys2d_elems(p, sh, cnt, ns[1], rm, max_rec=None)
    n = len(got) if got else 0
    tot += n
    print(f"seg{segid}: cnt={cnt} got={n}")
print("total:", tot)
