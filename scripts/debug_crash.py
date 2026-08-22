
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, _parse_b_type, find_node_section, parse_nodes, row_map_from_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
print("ns:", ns, "segs:", [(s[1], s[3], s[4], s[5]) for s in segs])
for sh, segid, cfg71, cnt, X, Y in segs[:4]:
    got = _parse_b_type(p, sh, cnt, ns[1], rm, Y, max_rec=5)
    print(f"  seg{segid}: {'OK' if got else 'FAIL'} {len(got) if got else 0}")
    if not got:
        s = sh + 24
        for k in range(0, 44, 4):
            print(f"     +{k:3d}: {p[s+k:s+k+4].hex()} u32={u32(p,s+k):>9d} u16=({u16(p,s+k):>5d},{u16(p,s+k+2):>5d})")
