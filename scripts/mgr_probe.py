
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, u16, find_elem_segments, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
print("db:", __import__('struct').unpack_from('<d', p, 4)[0])
ns = find_node_section(p)
print("node section:", ns)
segs = find_elem_segments(p)
print("segs:", [(s[1], s[3], s[4], s[5]) for s in segs])
pat = b"\x1f\x0b\x20\x30"
hits = []
start = 0
while True:
    i = p.find(pat, start)
    if i < 0: break
    hits.append(i)
    start = i + 1
print("0x30200B1F hits:", len(hits), "first:", hits[:5])
if hits:
    h = hits[0]
    for k in range(0, 48, 4):
        print(f"  +{k:3d}: {p[h+k:h+k+4].hex()} u32={u32(p,h+k):>10d}")
