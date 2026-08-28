"""car_section: 找缺失 eid + 分段产出."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import decode, load_payload, u32, u16, find_node_section, parse_nodes, find_elem_segments, _parse_a_type
from collections import Counter

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
m = decode(r"C:/Program Files/Altair/2019/tutorials/hm/car_section.hm")
print("nodes:", len(m.nodes), "elems:", len(m.elements))
missing = [e for e in range(1, 28512) if e not in m.elements]
print("num missing:", len(missing))
print("missing (first 40):", missing[:40])
print("missing (last 20):", missing[-20:])
# 缺失 eid 的分布 (按段)
# config 分布
cfgs = Counter(c for c, _ in m.elements.values())
print("decoded config hist:", dict(cfgs))

# 检查缺失 eid 是否集中在某个范围
import collections
ranges = []
for e in missing:
    if not ranges or e != ranges[-1][-1] + 1:
        ranges.append([e])
    else:
        ranges[-1].append(e)
print("missing ranges (first 10):", [(r[0], r[-1], len(r)) for r in ranges[:10]])
print("num ranges:", len(ranges))
