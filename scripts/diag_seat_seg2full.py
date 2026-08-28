"""SEAT_MODEL: dump seg 2 完整记录 (前 3 条)."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
segs = find_elem_segments(p)
sh, segid, cfg71, cnt, X, Y = segs[2]
print(f"seg 2: sh={sh} segid={segid} cnt={cnt} X={X} Y={Y}")

# 找 CONST 锚点
anchors = []
for s in range(sh + 16, sh + 80):
    if is_const(u32(p, s)):
        anchors.append(s)
print("anchors:", anchors)

# dump 第一条记录完整 (200 字节)
if anchors:
    rec = anchors[0]
    for off in range(0, 200, 2):
        q = rec + off
        v = u16(p, q)
        mark = " <CONST>" if is_const(u32(p, q)) else ""
        print(f"  +{off:4d}: {p[q:q+2].hex(' ')} u16={v}{mark}")
