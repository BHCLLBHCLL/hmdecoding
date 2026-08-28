"""测试新 _parse_a_geom 枚举式."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes, _parse_a_geom

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
rc = len(n1)
row_map = {}
for k in range(ns[1]):
    row_map[k + 1] = u32(p, ns[2] + k * ns[3] + ns[4])

segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if X != 3:
        continue
    nxt = next((s2[0] for s2 in segs if s2[0] > sh), len(p))
    got = _parse_a_geom(p, sh, nxt, cnt, rc, row_map)
    print(f"seg@{sh} cnt={cnt} -> {len(got)} elems")
