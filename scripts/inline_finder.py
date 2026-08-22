import gzip, struct
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
# manual finder
cands = []
for i in range(0, len(p) - 28, 4):
    if u32(i + 8) == 1 and u32(i + 12) == 136:
        n = u32(i + 16)
        if 1 <= n <= 10_000_000:
            cands.append((i, n))
print("inline candidates:", [(hex(h), n) for h, n in cands[:5]])
print("u32@0x93108:", u32(0x93108), "u32@0x9310c:", u32(0x9310c), "u32@0x93110:", u32(0x93110))
