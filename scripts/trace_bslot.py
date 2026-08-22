
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, _parse_b_slots, find_node_section, parse_nodes, row_map_from_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\abaqus\crash_tubes.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
rm = row_map_from_nodes(p, ns, base)
segs = find_elem_segments(p)
print("ns:", ns)
print("segs:", [(s[0], s[1], s[3], s[4], s[5]) for s in segs])
sh, segid, cfg71, cnt, X, Y = segs[0]
print("seg1 sh:", sh, "count:", cnt, "Y:", Y)
s = sh + 24
print("s bytes:", [u32(p, s+j*4) for j in range(4)])
print("E1 slot at 260240, s =", s, "delta:", 260240 - s)
got = _parse_b_slots(p, sh, cnt, ns[1], rm, Y, max_rec=5)
print("b_slots:", "OK" if got else "FAIL", len(got) if got else 0)
# manual trace
rec = s + 8
print("rec:", rec, "delta to E1 slot:", 260240 - rec)
slots = 0
while slots < 12 and u16(p, rec + 4*slots) != 0 and u16(p, rec + 4*slots + 2) == 0:
    slots += 1
print("slots:", slots, "first:", [u16(p, rec+4*j) for j in range(min(slots, 6))])
