"""诊断 standard_section_complete.hm 缺失元素."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, _parse_a_type, _parse_b_type, _parse_b_slots, parse_nodes

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\standard_section_complete.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1), ns)
row_map = {}
for k in range(ns[1]):
    rec = ns[2] + k * ns[3]
    row_map[k + 1] = u32(p, rec + ns[4])

segs = find_elem_segments(p)
print("elem segs:", segs)
tot = {}
for sh, segid, cfg71, cnt, X, Y in segs:
    got = None
    if X == 3:
        got = _parse_a_type(p, sh, cnt, len(n1), row_map)
    else:
        got = _parse_b_type(p, sh, cnt, len(n1), row_map, Y)
        got2 = _parse_b_slots(p, sh, cnt, len(n1), row_map, Y)
        if got2 and (got is None or len(got2) > len(got)):
            got = got2
    print(f"seg@{sh} segid={segid} cfg71={cfg71} cnt={cnt} X={X} Y={Y} -> {len(got) if got else 0} elems")
    if got:
        tot.update(got)
print("total:", len(tot))
print("sample:", list(tot.items())[:8])
