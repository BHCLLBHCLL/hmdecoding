
import sys, os
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import (_parse_a_type, _parse_y2_c60, _parse_y6_c3, _parse_y7_elems, _parse_y4_elems,
                     _parse_y0_elems, _parse_a_geom, _parse_v13_elems, _parse_ansys2d_elems,
                     _parse_b_type, _parse_b_slots, _parse_b_u16rows)

def ln(g):
    if not g: return 0
    v = next(iter(g.values()))
    return sum(len(x) for x in g.values()) if isinstance(v, list) else len(g)

def segstat(fname, subs):
    path = None
    for sub in subs:
        c = f"C:/Program Files/Altair/2019/tutorials/hm/{sub}{fname}"
        if os.path.exists(c): path = c; break
    if not path:
        path = f"C:/Program Files/Altair/2019/tutorials/hm/{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    if not ns:
        print(f"{fname}: NO-NODE"); return
    rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
    rowc = len(rm)
    segs = find_elem_segments(p)
    total = 0; short = []
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
            g2 = _parse_b_slots(p, sh, cnt, rowc, rm, Y)
            g3 = _parse_b_u16rows(p, sh, cnt, rowc, rm, Y)
            for g in (g2, g3):
                if g and (got is None or ln(g) > ln(got)): got = g
        n = ln(got)
        total += n
        if n < cnt:
            short.append((segid, cnt, n, X, Y))
    print(f"{fname}: cnt_sum={sum(s[3] for s in segs)} total={total}")
    for s in sorted(short, key=lambda t: -(t[1]-t[2]))[:10]:
        print("  ", s)

for f, subs in [("hook.hm", ["interfaces/samcef/", ""]),
                ("crash_tubes.hm", ["interfaces/abaqus/", ""]),
                ("channel.hm", [""]),
                ("keyhole.hm", [""]),
                ("abaqus3_0tutorial.hm", ["interfaces/abaqus/", ""])]:
    segstat(f, subs)
