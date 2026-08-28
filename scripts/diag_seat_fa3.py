"""SEAT_MODEL vs fa3 记录结构对照: @+4/@+8/@+18 字段."""
import sys
sys.path.insert(0, "hmdecoder")
from decoder import (load_payload, u32, u16, find_node_section, parse_nodes,
                     find_elem_segments, is_const)

def dump(path, name, n=3):
    p = load_payload(path)
    ns = find_node_section(p)
    n1, _ = parse_nodes(p, ns)
    segs = find_elem_segments(p)
    print(f"\n===== {name} ===== nodes={len(n1)} segs={len(segs)}")
    shown = 0
    for sh, segid, cfg71, cnt, X, Y in segs:
        if X != 3 or shown >= n:
            continue
        anchor = None
        for s in range(sh + 16, sh + 80):
            if is_const(u32(p, s)):
                anchor = s; break
        if anchor is None:
            continue
        rec = anchor
        for k in range(min(cnt, 2)):
            w = [u32(p, rec + 4*i) for i in range(12)]
            f1_eid = u16(p, rec + 18) | (u16(p, rec + 20) << 16)
            print(f"  seg{segid} Y={Y} rec{k}: @+4={u32(p,rec+4)} @+8={u32(p,rec+8)} "
                  f"@+8hi={u32(p,rec+8)>>16} @+12={u32(p,rec+12)} @+16={u32(p,rec+16)} "
                  f"@+18={f1_eid} @+20={u32(p,rec+20)} flag@+24={u32(p,rec+24)}")
            print(f"       u32: {w}")
            nxt = p.find(b"\xf5\x1f", rec + 24, min(rec + 200, len(p) - 2))
            while nxt >= 0:
                if is_const(u32(p, nxt)): break
                nxt = p.find(b"\xf5\x1f", nxt + 1, min(rec + 200, len(p) - 2))
            if nxt < 0: break
            rec = nxt
        shown += 1

dump(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\SEAT_MODEL.hm", "SEAT_MODEL")
dump(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\lsdyna\frame_assembly_3.hm", "frame_assembly_3")
