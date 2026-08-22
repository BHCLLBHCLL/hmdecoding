import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
print("node candidates:", [(hex(h), n) for h, n in ns[:8]])
for h, n in ns[:3]:
    nodes, base = D.parse_nodes(p, h, n)
    print(f"  hdr=0x{h:x} count={n} -> {len(nodes)} nodes, base=0x{base:x}")
