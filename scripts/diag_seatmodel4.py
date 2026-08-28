"""SEAT_MODEL 逐段 _parse_a_type 结果."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
segs = find_elem_segments(p)
tot = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    n = len(got) if got else 0
    tot += n
    if got is None or n < cnt:
        print(f"seg {segid} Y={Y} cnt={cnt} -> {n}")
print(f"total: {tot}")
