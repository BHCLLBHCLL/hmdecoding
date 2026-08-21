import gzip, struct, re
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
print("payload:", len(p))
for v in (6408, 31843, 126, 157, 354, 93):
    pat = struct.pack("<I", v)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"u32 {v}: {len(offs)} hits {[hex(o) for o in offs[:10]]}")
# dump around 0x8a84 (the spurious [1][136])
print()
for off in range(0x8a60, 0x8ad0, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"0x{off:04x}  {hexs}  {ascii_}")
# head fields of WS vs 1d_elements
for name, path in (("WS", "WS_3.2_3d_tetra_finish.hm"), ("1d", "C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")):
    raw2 = open(path, "rb").read()
    p2 = gzip.decompress(raw2[12:])
    print(name, "head:", [hex(u32(p2, i)) for i in range(0, 0x40, 4)])
