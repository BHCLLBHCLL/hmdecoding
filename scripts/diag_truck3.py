"""对比 decode() vs 直接 _parse_a_type 在 truck 上的差异."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, d64, find_node_section, parse_nodes,
                     _parse_a_type, decode_elements, _collect_node_segments)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1), ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

# 路径 A: 直接 _parse_a_type (与 diag_truck2 相同)
segs = __import__('decoder', fromlist=['find_elem_segments']).find_elem_segments(p)
tot_a = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        tot_a += len(got)
print("path A (_parse_a_type per seg):", tot_a)

# 路径 B: decode_elements
elems = decode_elements(p, row_map, len(n1))
print("path B (decode_elements):", len(elems) if elems else 0)
