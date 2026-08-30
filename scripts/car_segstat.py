
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import (_parse_a_type, _parse_y2_c60, _parse_y6_c3, _parse_y7_elems, _parse_y4_elems,
                     _parse_y0_elems, _parse_a_geom, _parse_v13_elems, _parse_ansys2d_elems,
                     _parse_b_type, _parse_b_slots, _parse_b_u16rows)

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\car_section.hm")
ns = find_node_section(p)
import struct
rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
rowc = len(rm)
segs = find_elem_segments(p)
print("segs:", len(segs), "cnt sum:", sum(s[3] for s in segs))
total = 0
short = []
for i, (sh, segid, cfg71, cnt, X, Y) in enumerate(segs):
    got = None
    if X == 3:
        if Y == 0: got = _parse_y0_elems(p, sh, cnt, rowc, rm)
        elif Y == 2: got = _parse_y2_c60(p, sh, cnt, rowc, rm)
        elif Y == 6: got = _parse_y6_c3(p, sh, cnt, rowc, rm)
        elif Y == 7: got = _parse_y7_elems(p, sh, cnt, rowc, rm)
        elif Y == 4: got = _parse_y4_elems(p, sh, cnt, rowc, rm)
        else: got = _parse_a_type(p, sh, cnt, rowc, rm)
        if got is None and Y == 3:
            nxt = segs[i+1][0] if i+1 < len(segs) else len(p)
            got = _parse_a_geom(p, sh, nxt, cnt, rowc, rm)
    else:
        got = _parse_b_type(p, sh, cnt, rowc, rm, Y)
    # unique eid count from got dict-of-list
    n = 0
    if got:
        from collections import Counter
        if got and isinstance(next(iter(got.values())), list):
            n = sum(len(v) for v in got.values())
        else:
            n = len(got)
    total += n
    if n < cnt:
        short.append((segid, cnt, n, Y))
print("total records:", total)
print("short segs (segid, cnt, got, Y):")
for s in sorted(short, key=lambda t: -(t[1]-t[2]))[:20]:
    print("  ", s)
