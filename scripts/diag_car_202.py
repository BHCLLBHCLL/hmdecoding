"""car_section: dump segid 202 (Y=6, cnt=136) - 可能是 config 3."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, is_const, _parse_a_type, find_node_section, parse_nodes

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
rc = len(row_map)

segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if segid == 202:
        print(f"segid 202 sh={sh} cnt={cnt} X={X} Y={Y}")
        for off in range(0, 120, 2):
            q = sh + off
            v = u16(p, q)
            mark = " <CONST>" if is_const(u32(p, q)) else ""
            print(f"  +{off:3d}: {p[q:q+2].hex(' ')} u16={v}{mark}")
        r = _parse_a_type(p, sh, cnt, rc, row_map)
        print("  _parse_a_type:", list(r.items())[:5] if r else None)
        break
