
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_elem_segments, find_node_section, _parse_b_slots

for fname, sub in [("crash_tubes.hm", "interfaces/abaqus/"), ("abaqus3_0tutorial.hm", "interfaces/abaqus/")]:
    p = load_payload(rf"C:\Program Files\Altair\2019\tutorials\hm\{sub}{fname}")
    ns = find_node_section(p)
    rm = {k+1: u32(p, ns[2] + k*ns[3] + ns[4]) for k in range(ns[1])}
    segs = find_elem_segments(p)
    for sh, segid, cfg71, cnt, X, Y in segs:
        g = _parse_b_slots(p, sh, cnt, len(rm), rm, Y)
        if not g:
            continue
        eids = sorted(g.keys()) if not isinstance(next(iter(g.values())), list) else sorted(k for k, v in g.items())
        n = sum(len(v) for v in g.values()) if isinstance(next(iter(g.values())), list) else len(g)
        print(f"{fname} seg{segid}: cnt={cnt} got={n} eids[{len(eids)}]={eids[:2]}..{eids[-2:]}")
        # find gap
        all_e = set(range(Y, Y + cnt))
        missing = sorted(all_e - set(eids))
        if missing:
            print(f"   missing eids: {missing[:10]}")
