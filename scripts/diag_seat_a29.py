"""SEAT_MODEL: seg 29 _parse_a_type 在 row_count=34296 下的输出."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, find_node_section, parse_nodes, find_elem_segments, _parse_a_type

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {k + 1: k + 1 for k in range(ns[1])}
rc = len(row_map)
print("rc:", rc)

segs = find_elem_segments(p)
sh, segid, cfg71, cnt, X, Y = segs[9]
r = _parse_a_type(p, sh, cnt, rc, row_map)
print("seg 29 _parse_a_type ->", r)
