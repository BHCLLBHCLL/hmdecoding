
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, find_node_section, parse_nodes, decode_elements, row_map_from_nodes

# WS fake segments
p = load_payload("WS_3.2_3d_tetra_finish.hm")
segs = find_elem_segments(p)
print("WS elem segs:", segs[:8], "total:", len(segs))

# molding1 hits
p2 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\molding1.hm")
hits = []
start = 0
while True:
    i = p2.find(b"\x88\x00\x00\x00", start)
    if i < 0: break
    n = u32(p2, i + 4)
    if 1 <= n <= 10_000_000:
        hits.append((i, n))
    start = i + 1
print("\nmolding1 136 hits:", sorted(hits, key=lambda h: -h[1])[:8])
ns = find_node_section(p2)
print("molding1 ns:", ns)

# body_side debug
p3 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\body_side.hm")
ns3 = find_node_section(p3)
nodes3, base3 = parse_nodes(p3, ns3)
rm3 = row_map_from_nodes(p3, ns3, base3)
segs3 = find_elem_segments(p3)
print("\nbody_side ns:", ns3, "segs:", segs3[:4])
from hmdecoder.decoder import _parse_a_type
got = _parse_a_type(p3, segs3[0][0], segs3[0][3], ns3[1], rm3, max_rec=50)
print("body_side parse:", "OK" if got else "FAIL", len(got) if got else "")

# truck first seg
p4 = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\truck.hm")
ns4 = find_node_section(p4)
nodes4, base4 = parse_nodes(p4, ns4)
rm4 = row_map_from_nodes(p4, ns4, base4)
segs4 = find_elem_segments(p4)
print("\ntruck ns:", ns4, "segs:", len(segs4), "first:", segs4[:3])
got4 = _parse_a_type(p4, segs4[0][0], segs4[0][3], ns4[1], rm4, max_rec=30)
print("truck seg1 parse:", "OK" if got4 else "FAIL", len(got4) if got4 else "")
