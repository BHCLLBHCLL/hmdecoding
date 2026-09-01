
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, find_elem_segments
from decoder import _parse_a_type, _parse_y2_c60, _parse_ansys2d_elems, _parse_a_geom, _parse_b_type, _parse_b_slots, _parse_b_u16rows

def ln(g):
    if not g: return 0
    v = next(iter(g.values()))
    return sum(len(x) for x in g.values()) if isinstance(v, list) else len(g)

def segstat(fname, subs):
    path = None
    for sub in subs:
        c = f"C:/Program Files/Altair/2019/tutorials/hm/{sub}{fname}"
        if os.path.exists(c): path = c; break
    if not path: path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
    segs = find_elem_segments(p)
    total = 0; short = []
    for i, (sh, segid, cfg71, cnt, X, Y) in enumerate(segs):
        got = None
        if X == 3:
            if Y == 2:
                got = _parse_ansys2d_elems(p, sh, cnt, len(rm), rm)
                if got is None: got = _parse_a_type(p, sh, cnt, len(rm), rm)
            else:
                got = _parse_a_type(p, sh, cnt, len(rm), rm)
        else:
            got = _parse_b_type(p, sh, cnt, len(rm), rm, Y)
            for g in (_parse_b_slots(p, sh, cnt, len(rm), rm, Y), _parse_b_u16rows(p, sh, cnt, len(rm), rm, Y)):
                if g and (got is None or ln(g) > ln(got)): got = g
        n = ln(got)
        total += n
        if n < cnt:
            short.append((segid, cnt, n, X, Y))
    print(f"{fname}: cnt_sum={sum(s[3] for s in segs)} total={total}")
    for s in sorted(short, key=lambda t: -(t[1]-t[2]))[:8]:
        print("  ", s)

segstat("seat_2.hm", ["interfaces/lsdyna/", ""])
segstat("seat_start.hm", ["interfaces/lsdyna/", ""])
