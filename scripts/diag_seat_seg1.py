"""SEAT_MODEL: seg 1 首尾记录 eid 及 5545 位置."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const, _parse_a_type

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {k + 1: k + 1 for k in range(ns[1])}
rc = len(row_map)

segs = find_elem_segments(p)
sh, segid, cfg71, cnt, X, Y = segs[1]
print(f"seg 1: sh={sh} segid={segid} cnt={cnt} X={X} Y={Y}")

r = _parse_a_type(p, sh, cnt, rc, row_map)
items = sorted(r.items())
print("num:", len(items))
print("first 3:", items[:3])
print("last 3:", items[-3:])
print("has 5545:", 5545 in r, "has 5548:", 5548 in r)
# 找 5545 在哪
for eid in (5544, 5545, 5548, 5549):
    print(f"  {eid} in seg1: {eid in r}")

# seg 2 的 5545 上下文
sh2 = segs[2][0]
print(f"\nseg 2 sh={sh2}, 5545 config104 在 2330015 是否属于 seg1 记录流:")
print("  2330015 - sh1 =", 2330015 - sh)
