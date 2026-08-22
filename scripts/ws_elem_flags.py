import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
ns = D.find_node_section(p)
hdr, count, shift, idoff, coordoff = ns[0]
def u16(o): return struct.unpack_from("<H", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]

recs = {}
for i in range(0, len(p) - 30):
    if u32(i + 4) == 0 and u32(i + 8) == 0:
        eid = u32(i)
        if eid < 100000 or eid > 400000:
            continue
        flag = u16(i + 12)
        if flag not in (359, 460):
            continue
        refs = [u16(i + 14), u16(i + 18), u16(i + 22), u16(i + 26)]
        if all(r <= count for r in refs):
            recs[eid] = (i, flag, refs)
print("records:", len(recs), "eid range:", min(recs), "-", max(recs))
from collections import Counter
fc = Counter(f for _, f, _ in recs.values())
print("flag counts:", fc)
r4nz = sum(1 for _, f, r in recs.values() if r[3] != 0)
print("records with r4 != 0:", r4nz)
r3nz = sum(1 for _, f, r in recs.values() if r[3] == 0 and r[2] != 0)
print("records with r4==0 and r3!=0:", r3nz)
# check r4 nonzero by flag
f359 = [r for _, f, r in recs.values() if f == 359]
f460 = [r for _, f, r in recs.values() if f == 460]
print("flag359 r4 nonzero:", sum(1 for r in f359 if r[3] != 0), "/", len(f359))
print("flag460 r4 nonzero:", sum(1 for r in f460 if r[3] != 0), "/", len(f460))
