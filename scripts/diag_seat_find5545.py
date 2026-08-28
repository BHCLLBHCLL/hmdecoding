"""SEAT_MODEL: 搜索 eid 5545 的所有出现位置及上下文."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
# 5545 = 0x15A9, bytes "a9 15"
pat = b"\xa9\x15"
hits = []
j = 0
while True:
    j = p.find(pat, j)
    if j < 0:
        break
    hits.append(j)
    j += 1
print("eid 5545 (a9 15) hits:", len(hits))
for h in hits:
    print(f"  @ {h}: ctx u16[0..8] = {[u16(p, h+2*i) for i in range(9)]}")

# 也搜索 config 104 元素 5545 的节点 [7256, 9972, 9973, 8416] 的第一个节点 7256=0x1C58
pat2 = b"\x58\x1c"
hits2 = []
j = 0
while True:
    j = p.find(pat2, j)
    if j < 0:
        break
    hits2.append(j)
    j += 1
print("node 7256 (58 1c) hits:", len(hits2), hits2[:20])
