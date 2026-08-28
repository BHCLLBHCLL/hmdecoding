"""dump SEAT_MODEL family-1 误命中记录 vs truck 真记录."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, d64, find_node_section, parse_nodes, find_elem_segments

p = load_payload(r"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/SEAT_MODEL.hm")
ns = find_node_section(p)
n1, _ = parse_nodes(p, ns)
segs = find_elem_segments(p)

# 第一条命中
for sh, segid, cfg71, cnt, X, Y in segs[:3]:
    j = sh + 24
    c = p.find(b"\xf5\x1f\x24\x70", j, sh + 300)
    while c >= 0:
        if u32(p, c + 8) in (0x02BD0002, 0x02AE0002) and u16(p, c + 12) == 2596:
            print(f"\n== seg {segid} @{sh} Y={Y} hit @{c} ==")
            for off in range(0, 56, 4):
                q = c + off
                v = u32(p, q)
                print(f"  +{off:2d}: {p[q:q+4].hex(' ')} u32={v:<10d} u16=({u16(p,q)},{u16(p,q+2)})")
            break
        j = c + 1
        c = p.find(b"\xf5\x1f\x24\x70", j, sh + 300)
