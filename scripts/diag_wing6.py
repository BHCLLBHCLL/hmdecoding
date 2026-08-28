"""直接调用 _parse_a_geom 测试 wing_section 两段."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes, _parse_a_geom

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

for sh, segid, cfg71, cnt, X, Y in find_elem_segments(p):
    if X != 3:
        continue
    got = _parse_a_geom(p, sh, cnt, len(n1), row_map)
    print(f"seg@{sh} cnt={cnt} -> {len(got)} elems")
    if got:
        items = list(got.items())
        print("  first:", items[0], "last:", items[-1])
