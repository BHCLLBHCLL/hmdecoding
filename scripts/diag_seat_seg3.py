"""SEAT_MODEL: 检查 seg 3 (segid 4) 首记录与产出."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const, _parse_a_type, _parse_y2_c60

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {k + 1: k + 1 for k in range(ns[1])}
rc = len(row_map)

segs = find_elem_segments(p)
sh, segid, cfg71, cnt, X, Y = segs[3]
print(f"seg 3: sh={sh} segid={segid} cnt={cnt} X={X} Y={Y}")
rec = sh + 24
print("u16(rec+30):", u16(p, rec + 30), "is_const:", is_const(u32(p, rec)))
r = _parse_a_type(p, sh, cnt, rc, row_map)
# 只显示前 5 个
items = list(r.items())[:5] if r else []
print("_parse_a_type first 5:", items)
print("has 5545:", 5545 in (r or {}))
# dump 前 40 字节
for off in range(0, 44, 2):
    q = sh + off
    print(f"  +{off:3d}: {p[q:q+2].hex(' ')} u16={u16(p,q)}")
