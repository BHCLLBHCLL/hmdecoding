
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments
from decoder import _parse_a_geom

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = {k+1: u32(p, base + k*ns[3] + ns[4]) for k in range(ns[1])}
segs = find_elem_segments(p)
print("segs:", [(s[0], s[1], s[3], s[4], s[5]) for s in segs])
sh, segid, cfg71, cnt, X, Y = segs[0]
print("seg8 sh:", sh, "cnt:", cnt, "Y:", Y)
# next seg
nxt_sh = segs[1][0] if len(segs) > 1 else len(p)
print("next seg:", nxt_sh, "hi range:", nxt_sh - sh)
got = _parse_a_geom(p, sh, nxt_sh, cnt, ns[1], rm, max_rec=20)
print("parse_a_geom seg8:", len(got) if got else 0)
# count MARK hits in seg8 range
MARK = b"\xe4\x0b\x04\x1a"
hits = []
j = sh + 24
while j < nxt_sh:
    j = p.find(MARK, j, nxt_sh)
    if j < 0: break
    hits.append(j)
    j += 1
print("MARK hits in seg8:", len(hits), "spacing:", [hits[i+1]-hits[i] for i in range(min(10, len(hits)-1))] if len(hits) > 1 else None)
