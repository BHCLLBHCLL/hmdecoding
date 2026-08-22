
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, _parse_a_type, find_node_section, parse_nodes, row_map_from_nodes

for fname, sub in [("composites.hm", ""), ("joints.hm", "interfaces/lsdyna/")]:
    path = f"C:/Program Files/Altair/2019/tutorials/hm/{sub}{fname}"
    p = load_payload(path)
    ns = find_node_section(p)
    nodes, base = parse_nodes(p, ns)
    rm = row_map_from_nodes(p, ns, base)
    segs = find_elem_segments(p)
    print(f"== {fname} ns={ns} segs={[(s[1], s[3], s[4], s[5]) for s in segs[:8]]}")
    for sh, segid, cfg71, cnt, X, Y in segs[:3]:
        got = _parse_a_type(p, sh, cnt, ns[1], rm, max_rec=10) if X == 3 else None
        print(f"   seg{segid}: {'OK' if got else 'FAIL'}")
        if not got:
            # dump record start bytes
            s = sh + 24
            for k in range(0, 48, 4):
                print(f"     +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d}")
