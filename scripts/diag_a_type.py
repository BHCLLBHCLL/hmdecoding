"""调试 _parse_a_type 对 shell_section seg@917."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, _parse_a_type

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\shell_section.hm", "rb").read()
p = gzip.decompress(raw[12:])

# 节点解析
ns = find_node_section(p)
print("node section:", ns)
import decoder
n1, b1 = decoder.parse_nodes(p, ns)
print(f"nodes: {len(n1)}")

# row_map
row_map = {}
row = 0
for k in range(ns[1]):
    rec = ns[2] + k * ns[3]
    nid = u32(p, rec + ns[4])
    row += 1
    row_map[row] = nid
print(f"row_map: {row} rows")

segs = find_elem_segments(p)
for sh, segid, cfg71, cnt, X, Y in segs:
    if X == 3:
        got = _parse_a_type(p, sh, cnt, len(n1), row_map)
        print(f"seg@{sh} cfg71={cfg71} cnt={cnt} X={X} Y={Y} -> {got}")
