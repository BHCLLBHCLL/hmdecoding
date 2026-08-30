
import sys
sys.path.insert(0, "hmdecoder")
from decoder import load_payload, u32, d64, find_node_section, parse_nodes

p = load_payload(r"C:\Program Files\Altair\2019\tutorials\hm\interfaces\ansys\hm-ansys_contact_manager_2-d_tutorial.hm")
ns = find_node_section(p)
nodes, base = parse_nodes(p, ns)
m_end = ns[2] + len(nodes) * ns[3]
lo = max(0, m_end - 256)
hi = m_end + 512*1024
excl = [(ns[2], ns[2]+8)]
ZERO4 = b"\x00\x00\x00\x00"
starts = {56: [], 68: []}
j = lo
while True:
    j = p.find(ZERO4, j, hi)
    if j < 0: break
    b = j - 4
    if b < 0 or any(a <= b < c for a, c in excl):
        j += 1; continue
    nid = u32(p, b)
    k = u32(p, b + 8)
    if not (104 < nid <= 10_000_000 and k <= 16):
        j += 1; continue
    for stride in (56, 68):
        if b + stride > len(p): continue
        x, y, z = d64(p, b + 12), d64(p, b + 20), d64(p, b + 28)
        if abs(x) < 10000 and abs(y) < 10000 and abs(z) < 10000:
            starts[stride].append(b)
    j += 1
print("starts[56] first 8:", starts[56][:8])
print("starts[68] first 8:", starts[68][:8])
print("100361 in starts[56]:", 100361 in starts[56], " in 68:", 100361 in starts[68])
# what is at 100361+4 (0?): print
print("u32@100361:", u32(p,100361), "u32@100365:", u32(p,100365), "u32@100369:", u32(p,100369), "u32@100373:", u32(p,100373))
