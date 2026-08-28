"""调试 standard_section.hm _parse_a_type 各段."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, _parse_a_type, parse_nodes, is_const

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\standard_section.hm", "rb").read()
p = gzip.decompress(raw[12:])
ns = find_node_section(p)
print("node section:", ns)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1))
row_map = {}
for k in range(ns[1]):
    rec = ns[2] + k * ns[3]
    row_map[k + 1] = u32(p, rec + ns[4])

segs = find_elem_segments(p)
print("elem segs:", segs)
for sh, segid, cfg71, cnt, X, Y in segs:
    if X == 3:
        got = _parse_a_type(p, sh, cnt, len(n1), row_map)
        print(f"seg@{sh} cfg71={cfg71} cnt={cnt} -> {len(got) if got else 0} elems")
        if got:
            print("   sample:", list(got.items())[:6])
        else:
            # dump 段头 + 首记录
            print("   dump:")
            for off in range(0, 64, 4):
                q = sh + off
                v = u32(p, q)
                mark = " <CONST>" if is_const(v) else ""
                print(f"    +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
