
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_ansys2d_elems

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_wizard_2-d_tutorial.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
sh = segs[1][0]
got = _parse_ansys2d_elems(p, sh, 162, ns[1], rm, max_rec=None)
print("58 in got:", 58 in got)
print("got keys sample:", sorted(got.keys())[:5], "...", sorted(got.keys())[-5:])
print("num keys:", len(got))
print("gap in 41..202:", sorted(set(range(41,203)) - set(got.keys())))
# 58 record position relative to seg2 start
print("seg2 sh:", sh)
# what's got for 57 and 59?
print("57:", got.get(57), "59:", got.get(59), "58:", got.get(58))
