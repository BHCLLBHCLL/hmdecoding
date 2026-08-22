import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
nodes, base = D.parse_nodes(p, hdr, count, shift, idoff, coordoff)
row_order = [D.u32(p, base + k * 52 + idoff) for k in range(count)]
row_of = {nid: k + 1 for k, nid in enumerate(row_order)}
print("node section hdr=0x%x count=%d base=0x%x idoff=%d" % (hdr, count, base, idoff))
rows = [row_of.get(n) for n in (70098, 70393, 68911)]
print("rows of (70098,70393,68911):", rows)
def u32(o): return struct.unpack_from("<I", p, o)[0]
def u16(o): return struct.unpack_from("<H", p, o)[0]
for off in range(0xe46c8, 0xe4730, 2):
    v2 = u16(off); v4 = u32(off)
    ann = ""
    if v2 in rows or v4 in rows:
        ann = "  <-- ROW!"
    if v4 in (302871, 302870):
        ann = "  <== EID"
    print(f"0x{off:05x}  u16={v2:>6}  u32={v4:>9}{ann}")
