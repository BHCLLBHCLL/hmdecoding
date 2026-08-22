import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
nodes, base = D.parse_nodes(p, hdr, count, shift, idoff, coordoff)
row_order = [D.u32(p, base + k * 52 + idoff) for k in range(count)]
row_of = {nid: k + 1 for k, nid in enumerate(row_order)}
def u16(o): return struct.unpack_from("<H", p, o)[0]
GT = {302871: (70098, 70393, 68911, 0), 302870: (70393, 70098, 70097, 0),
      302869: (70393, 70395, 68912, 0), 302868: (70394, 70097, 70096, 0),
      302867: (70395, 70393, 70394, 0)}
# find record positions: eid countdown at ~0x30 spacing? find eid 302871 first
import re
o = [m.start() for m in re.finditer(re.escape(struct.pack("<I", 302871)), p)]
print("eid 302871 at:", [hex(x) for x in o[:4]])
for eid, quad in GT.items():
    # find eid position
    pos = [m.start() for m in re.finditer(re.escape(struct.pack("<I", eid)), p)]
    if not pos:
        print(f"elem {eid}: eid not found"); continue
    r = pos[0]
    refs = [u16(r + 0x0e), u16(r + 0x12), u16(r + 0x16), u16(r + 0x1a)]
    ids = [row_order[x - 1] if 1 <= x <= len(row_order) else 0 for x in refs]
    print(f"elem {eid} @0x{r:x}: rows={refs} -> ids={ids} GT={quad} {'MATCH' if tuple(ids) == quad else 'MISMATCH'}")
