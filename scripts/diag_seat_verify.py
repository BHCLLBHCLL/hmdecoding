"""SEAT_MODEL: 检查最终解码结果 vs oracle 缺失 eid."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_elem_segments, _parse_y2_c60, _parse_y4_elems

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_count = len(ns)  # placeholder
row_map = {k + 1: k + 1 for k in range(ns[1])}
rc = len(row_map)

segs = find_elem_segments(p)
for idx in (9, 10):
    sh, segid, cfg71, cnt, X, Y = segs[idx]
    print(f"seg {idx} segid={segid} cnt={cnt} X={X} Y={Y}")
    if Y == 2:
        r = _parse_y2_c60(p, sh, cnt, rc, row_map)
        print("  _parse_y2_c60 ->", r)
    if Y == 4:
        r = _parse_y4_elems(p, sh, cnt, rc, row_map)
        print("  _parse_y4_elems ->", r)
