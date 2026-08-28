"""car_section 段结构总览."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const
from collections import Counter

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1), "ns:", ns)
print("db:", __import__('struct').unpack_from('<d', p, 4)[0])

segs = find_elem_segments(p)
print("num segs:", len(segs))
print("X:", Counter(s[4] for s in segs), "Y:", Counter(s[5] for s in segs).most_common(10))
print("cfg71:", Counter(s[2] for s in segs).most_common(10))

# 打印所有段
total = 0
for i, s in enumerate(segs):
    sh, segid, cfg71, cnt, X, Y = s
    total += cnt
    print(f"  [{i}] sh={sh} segid={segid} cnt={cnt} X={X} Y={Y}")
print("total cnt:", total)
