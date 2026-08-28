"""frame_assembly_1 family-1 命中 + 首记录."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, find_elem_segments, is_const

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\frame_assembly_1.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)
hits = 0
for sh, segid, cfg71, cnt, X, Y in segs:
    j = sh + 24
    while True:
        c = p.find(b"\xf5\x1f\x24\x70", j, sh + cnt * 300)
        if c < 0:
            break
        if u32(p, c + 8) in (0x02BD0002, 0x02AE0002) and u16(p, c + 12) == 2596:
            hits += 1
        j = c + 1
print("family-1 mark hits:", hits)
sh, segid, cfg71, cnt, X, Y = segs[0]
print(f"seg {segid} @{sh} cnt={cnt} Y={Y}")
for off in range(0, 80, 4):
    q = sh + off
    v = u32(p, q)
    mark = " <CONST>" if is_const(v) else ""
    print(f"  +{off:2d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)}){mark}")
