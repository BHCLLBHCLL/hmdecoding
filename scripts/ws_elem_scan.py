import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
nodes, base = D.parse_nodes(p, hdr, count, shift, idoff, coordoff)
row_order = [D.u32(p, base + k * 52 + idoff) for k in range(count)]
def u16(o): return struct.unpack_from("<H", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]

# scan for record signature: [u32 eid][u32 0][u32 0][u16 359][u16 r1][u16 0][u16 r2][u16 0][u16 r3][u16 0][u16 r4]
recs = {}
for i in range(0, len(p) - 30):
    if u32(i + 4) == 0 and u32(i + 8) == 0 and u16(i + 12) == 0x0167:
        eid = u32(i)
        if eid < 100000:
            continue
        refs = [u16(i + 14), u16(i + 18), u16(i + 22), u16(i + 26)]
        if all(r == 0 or (1 <= r <= count) for r in refs):
            recs[eid] = (i, refs)
print("records found:", len(recs))
# eid range
eids = sorted(recs)
print("eid min/max:", eids[0], eids[-1])
# count by node ref validity: check a sample
import random
ok = 0
for eid, (pos, refs) in list(recs.items())[:20]:
    ids = [row_order[r-1] if 1 <= r <= count else 0 for r in refs]
    print(f"  elem {eid} @0x{pos:x}: refs={refs} ids={ids[:3]}")
