import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
def f32(off): return struct.unpack_from("<f", p, off)[0]
for nid in (67604, 68519, 70307, 70468, 70576):
    offs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", nid)), p)]
    print(f"u32 {nid}: {len(offs)} hits {[hex(o) for o in offs[:8]]}")
    for o in offs[:2]:
        print(f"   @0x{o:x}: ctx={p[o-16:o+48].hex()}")
