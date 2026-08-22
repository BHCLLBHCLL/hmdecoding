import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
def u16(o): return struct.unpack_from("<H", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]

# loose scan: [eid u32][0 u32][0 u32][u16 flag][r1 u16][0 u16][r2 u16][0 u16][r3 u16][0 u16][r4 u16]
hits = []
for i in range(0, len(p) - 30):
    if u32(i + 4) == 0 and u32(i + 8) == 0:
        eid = u32(i)
        if eid < 100000 or eid > 400000:
            continue
        r1, r2, r3, r4 = u16(i + 14), u16(i + 18), u16(i + 22), u16(i + 26)
        if all(r <= count for r in (r1, r2, r3, r4)) and any(r > 0 for r in (r1, r2, r3, r4)):
            hits.append((i, eid, u16(i + 12), (r1, r2, r3, r4)))
print("loose hits:", len(hits))
from collections import Counter
flags = Counter(h[2] for h in hits)
print("flags:", flags.most_common(10))
eids = [h[1] for h in hits]
print("eid range:", min(eids), max(eids))
# region distribution
regs = Counter(hex(h[0] >> 16) for h in hits)
print("regions:", regs.most_common(12))
