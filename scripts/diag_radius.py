"""诊断 radius-tcl.hm 元素段."""
import sys, gzip
sys.path.insert(0, "hmdecoder")
from decoder import u32, u16, d64, find_node_section, find_elem_segments, parse_nodes, is_const

raw = open(r"C:\Program Files\Altair\2019\tutorials\hm\radius-tcl.hm", "rb").read()
p = gzip.decompress(raw[12:])
print(f"payload {len(p)}")
ns = find_node_section(p)
print("node section:", ns)
n1, _ = parse_nodes(p, ns)
print("nodes:", len(n1))

segs = find_elem_segments(p)
print("elem segs:", segs)
for sh, segid, cfg71, cnt, X, Y in segs:
    print(f"\n== seg @{sh} segid={segid} cfg71={cfg71} cnt={cnt} X={X} Y={Y}")
    for off in range(0, 120, 4):
        q = sh + off
        if q + 4 > len(p):
            break
        v = u32(p, q)
        mark = " <CONST>" if is_const(v) else ""
        print(f"  +{off:3d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
