
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, find_elem_segments
from decoder import _parse_a_type, _parse_y2_c60, _parse_ansys2d_elems

def ln(g):
    if not g: return 0
    v = next(iter(g.values()))
    return sum(len(x) for x in g.values()) if isinstance(v, list) else len(g)

def segstat(fname):
    path = f"C:/Program Files/Altair/2019/tutorials/hm/interfaces/lsdyna/{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
    segs = find_elem_segments(p)
    total = 0; short = []
    for sh, segid, cfg71, cnt, X, Y in segs:
        got = None
        for fn in (lambda: _parse_y2_c60(p, sh, cnt, len(rm), rm),
                   lambda: _parse_a_type(p, sh, cnt, len(rm), rm),
                   lambda: _parse_ansys2d_elems(p, sh, cnt, len(rm), rm)):
            g = fn()
            if g and (got is None or ln(g) > ln(got)): got = g
        n = ln(got)
        total += n
        if n < cnt:
            short.append((segid, cnt, n))
    print(f"{fname}: cnt_sum={sum(s[3] for s in segs)} total={total}")
    for s in sorted(short, key=lambda t: -(t[1]-t[2]))[:8]:
        print("  ", s)

segstat("seat_2.hm")
segstat("seat_start.hm")
