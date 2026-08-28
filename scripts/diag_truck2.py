"""truck.hm 各元素段解码统计: 找出失败段."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes, _parse_a_type
from collections import Counter

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

segs = find_elem_segments(p)
ok = 0
fail = []
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got:
        ok += len(got)
    else:
        fail.append((sh, segid, cnt, Y))
print(f"decoded: {ok} / target {sum(s[3] for s in segs)}")
print(f"failed segs: {len(fail)}/{len(segs)}")
# 失败段按 Y 分类
print("fail Y dist:", Counter(f[3] for f in fail))
print("fail cnt dist:", Counter(f[2] for f in fail).most_common(10))
print("fail segid sample:", [f[1] for f in fail[:30]])
# 失败段总 cnt
print("fail total cnt:", sum(f[2] for f in fail))
# 部分失败段
part = []
for sh, segid, cfg71, cnt, X, Y in segs:
    got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    if got and len(got) < cnt:
        part.append((segid, cnt, len(got)))
print(f"partial segs: {len(part)}")
for x in part[:15]:
    print("  partial:", x)
