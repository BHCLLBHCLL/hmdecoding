
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, find_node_section, parse_nodes, find_elem_segments

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\wing_section_complete.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
segs = find_elem_segments(p)
sh = segs[0][0]; nxt = segs[1][0]
# dump records at j = sh+24 + k*74 for k near 395..410 + also find eid at each
MARK = b"\xe4\x0b\x04\x1a"
hits = []
j = sh + 24
while j < nxt:
    j = p.find(MARK, j, nxt)
    if j < 0: break
    hits.append(j)
    j += 1
print("mark hits:", len(hits))
for k in range(393, min(405, len(hits))):
    h = hits[k]
    eid = u32(p, h + 36)
    rows = [u32(p, h + 48 + 4*i) >> 16 for i in range(4)]
    print(f"k={k} @{h}: eid={eid} spacing={h-hits[k-1] if k>0 else '?'} rows={rows}")
