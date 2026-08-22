import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
for v in (70393, 70098, 68911, 302867, 302871, 103):
    offs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
    print(f"u32 {v}: {len(offs)} hits {[hex(o) for o in offs[:8]]}")
