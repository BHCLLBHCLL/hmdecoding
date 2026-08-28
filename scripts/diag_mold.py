"""诊断 molding1.hm 元素段."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes, is_const
from collections import Counter

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm", "rb").read()
p = gzip.decompress(raw[12:])
print(f"payload {len(p)}")
ns = find_node_section(p)
print("node section:", ns)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1))

segs = find_elem_segments(p)
print(f"elem segs: {len(segs)}")
print("X dist:", Counter(s[4] for s in segs))
print("Y dist:", Counter(s[5] for s in segs).most_common(10))
print("cfg71 dist:", Counter(s[2] for s in segs).most_common(10))
print("cnt total:", sum(s[3] for s in segs))
# 大段列表
big = sorted(segs, key=lambda s: -s[3])[:8]
for s in big:
    print("  big seg:", s)
