"""诊断 wing_section_complete.hm 元素段."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
print(f"payload {len(p)}")
ns = find_node_section(p)
print("node section:", ns)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1))

segs = find_elem_segments(p)
print("elem segs:", segs)
from collections import Counter
print("X dist:", Counter(s[4] for s in segs), "Y dist:", Counter(s[5] for s in segs), "cfg71 dist:", Counter(s[2] for s in segs).most_common(10))
