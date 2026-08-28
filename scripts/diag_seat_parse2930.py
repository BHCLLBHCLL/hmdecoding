"""SEAT_MODEL: 检查 seg 29/30 在 _parse_a_type / _parse_y4_elems 下的输出."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, _parse_a_type, _parse_y4_elems)

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_count = len(n1)
row_map = {k + 1: k + 1 for k in range(ns[1])}  # chain=True identity

segs = find_elem_segments(p)
for idx in (9, 10):
    sh, segid, cfg71, cnt, X, Y = segs[idx]
    print(f"\n=== seg idx {idx} segid={segid} cnt={cnt} X={X} Y={Y} ===")
    a = _parse_a_type(p, sh, cnt, row_count, row_map)
    print("  _parse_a_type ->", a)
    if Y == 4:
        y4 = _parse_y4_elems(p, sh, cnt, row_count, row_map)
        print("  _parse_y4_elems ->", y4)
