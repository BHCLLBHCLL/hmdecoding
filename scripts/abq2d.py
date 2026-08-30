
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import (_parse_a_type, _parse_y2_c60, _parse_ansys2d_elems)
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\abaqus_contactManager_2D_tutorial.hm")
ns = find_node_section(p)
rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
for i, (sh, segid, cfg71, cnt, X, Y) in enumerate(segs):
    nxt = segs[i+1][0] if i+1 < len(segs) else len(p)
    g = _parse_ansys2d_elems(p, sh, cnt, len(rm), rm)
    n = 0
    if g:
        v = next(iter(g.values())); n = sum(len(x) for x in g.values()) if isinstance(v, list) else len(g)
    print(f"seg{segid}: cnt={cnt} got={n} Y={Y}")
