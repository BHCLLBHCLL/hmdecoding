import gzip, struct
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
print("raw size:", len(raw), "head:", raw[:12].hex())
p = gzip.decompress(raw[12:])
print("payload:", len(p))
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
for off in range(0x930f0, 0x93160, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"0x{off:04x}  {hexs}  {ascii_}")
print("u32@0x93108:", u32(0x93108), "u32@0x9310c:", u32(0x9310c), "u32@0x93110:", u32(0x93110))
print("d64@0x93100:", d64(0x93100))
