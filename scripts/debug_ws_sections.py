import gzip, struct
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
print("payload:", len(p))
hits = []
for i in range(0, len(p) - 16, 4):
    if u32(i) == 1 and u32(i+4) == 136:
        hits.append((i, u32(i+8), u32(i+12)))
print("[1][136] hits:", [(hex(h[0]), h[1], h[2]) for h in hits[:12]])
hits2 = []
for i in range(0, len(p) - 16, 4):
    if u32(i) == 997 and u32(i+4) == 3:
        hits2.append((i, u32(i+8), u32(i+12)))
print("[997][3] hits:", [(hex(h[0]), h[1], h[2]) for h in hits2[:12]])
n = 0
for i in range(0, len(p) - 0x30, 4):
    if u32(i) == 0 and u32(i+4) == 0x01680000:
        n += 1
print("element record markers:", n)
c = 0
for i in range(0, len(p) - 4, 4):
    if u32(i) == 0x70241FF5:
        c += 1
print("0x70241FF5:", c)
for h in hits:
    if abs(h[1] - 6408) < 200:
        print("near-6408:", hex(h[0]), h)
