"""car_section: dump segid 175 首记录."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if segid == 175:
        print(f"segid 175 sh={sh} cnt={cnt} X={X} Y={Y}")
        for off in range(0, 120, 2):
            q = sh + off
            v = u16(p, q)
            mark = " <CONST>" if is_const(u32(p, q)) else ""
            print(f"  +{off:3d}: {p[q:q+2].hex(' ')} u16={v}{mark}")
        break
