import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/arm2D.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
print("payload:", len(p))
# all [997][3] patterns
hits = []
for i in range(0, len(p) - 16, 4):
    if u32(i) == 997 and u32(i+4) == 3:
        hits.append((i, u32(i+8), u32(i+12)))
print("[997][3] hits:", [(hex(h[0]), h[1], h[2]) for h in hits[:10]])
# 0x70241FF5 count
c = 0
offs = []
for i in range(0, len(p) - 4, 4):
    if u32(i) == 0x70241FF5:
        c += 1
        offs.append(i)
print("0x70241FF5:", c, [hex(o) for o in offs[:10]])
# 0x01680000 count
c2 = 0
for i in range(0, len(p) - 4, 4):
    if u32(i) == 0x01680000:
        c2 += 1
print("0x01680000:", c2)
# node section found at? print section info
import sys
sys.path.insert(0, ".")
from hmdecoder import find_node_section
ns = find_node_section(p)
print("node section candidates:", [(hex(h), n) for h, n in ns[:5]])
