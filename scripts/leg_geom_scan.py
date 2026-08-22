import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
print("payload:", len(p))
# find u32 1, 2, 4 occurrences (line ids) and node ids 2,4,6,7
for v in (1, 2, 4):
    offs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
    print(f"u32 {v}: {len(offs)} hits {[hex(o) for o in offs[:12]]}")
# dump after node section (node7 rec ends ~0x3c4) to 0x700
for off in range(0x3c4, 0x700, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"0x{off:04x}  {hexs}  {ascii_}")
