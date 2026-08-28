"""SEAT_MODEL 段结构总览 + 缺失 eid 定位."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const
from collections import Counter

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_count = len(n1)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])
print("nodes:", row_count, "ns:", ns)

segs = find_elem_segments(p)
print("num segs:", len(segs))
print("X:", Counter(s[4] for s in segs), "Y:", Counter(s[5] for s in segs).most_common(10))

# 打印所有段 (segid, cnt, X, Y, sh)
for i, s in enumerate(segs):
    sh, segid, cfg71, cnt, X, Y = s
    if cnt > 20 or i < 60:
        print(f"  [{i}] sh={sh} segid={segid} cnt={cnt} X={X} Y={Y}")

# 重点: 最后几个段 (seg 29/30 附近)
print("\n== 最后 6 个段 ==")
for i, s in enumerate(segs[-6:]):
    sh, segid, cfg71, cnt, X, Y = s
    print(f"  [{len(segs)-6+i}] sh={sh} segid={segid} cnt={cnt} X={X} Y={Y}")
    # dump 前 60 字节 u16
    for off in range(0, 60, 2):
        q = sh + off
        print(f"      +{off:3d}: {p[q:q+2].hex(' ')} u16={u16(p,q)}")
