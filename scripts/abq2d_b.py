
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_b_type, _parse_b_slots, _parse_b_u16rows

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\abaqus_contactManager_2D_tutorial.hm")
ns = find_node_section(p)
rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    bt = _parse_b_type(p, sh, cnt, len(rm), rm, Y)
    bs = _parse_b_slots(p, sh, cnt, len(rm), rm, Y)
    bu = _parse_b_u16rows(p, sh, cnt, len(rm), rm, Y)
    def ln(g):
        if not g: return 0
        v = next(iter(g.values())); return sum(len(x) for x in g.values()) if isinstance(v, list) else len(g)
    print(f"seg{segid}: cnt={cnt} btype={ln(bt)} slots={ln(bs)} u16rows={ln(bu)}")
