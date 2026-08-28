"""SEAT_MODEL: dump seg 29 与 seg 30 完整内容."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_count = len(n1)
segs = find_elem_segments(p)

# seg 29: index 9 (sh=3395021), seg 30: index 10 (sh=3395449)
for idx in (9, 10):
    sh, segid, cfg71, cnt, X, Y = segs[idx]
    print(f"\n===== seg index {idx} sh={sh} segid={segid} cnt={cnt} X={X} Y={Y} =====")
    # dump 400 bytes
    for off in range(0, 400, 2):
        q = sh + off
        v = u16(p, q)
        mark = " <CONST>" if is_const(u32(p, q)) else ""
        print(f"  +{off:4d} (abs {q}): {p[q:q+2].hex(' ')} u16={v}{mark}")
