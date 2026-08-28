"""诊断 truck.hm 元素段: 找 2000001+ face 段特征."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes
from collections import Counter

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm", "rb").read()
p = gzip.decompress(raw[12:])
print(f"payload {len(p)}")
ns = find_node_section(p)
print("node section:", ns)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1))

segs = find_elem_segments(p)
print(f"elem segs: {len(segs)}")
print("X dist:", Counter(s[4] for s in segs))
print("Y dist:", Counter(s[5] for s in segs).most_common(12))
print("cfg71 dist:", Counter(s[2] for s in segs).most_common(12))
print("cnt total:", sum(s[3] for s in segs))
# 段分布: 按 segid 排序看 eid 范围
segs_sorted = sorted(segs, key=lambda s: s[0])
print("\nsegments (first 30 by offset):")
for s in segs_sorted[:30]:
    print("  ", s)
print("\nsegments with cnt > 1000:")
for s in sorted(segs, key=lambda s: -s[3])[:15]:
    print("  ", s)
