
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, find_node_section, parse_nodes
p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
ns = find_node_section(p)
rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
from decoder import _parse_b_slots
for sh, segid, cfg71, cnt, X, Y in segs:
    g = _parse_b_slots(p, sh, cnt, len(rm), rm, Y)
    print(f"seg{segid} cnt={cnt} slots={len(g) if g else 0}")
