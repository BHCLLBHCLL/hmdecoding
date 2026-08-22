import gzip, struct
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
for off in range(0xe4600, 0xe4900, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    u = [u32(off + i) for i in range(0, 16, 4)]
    print(f"0x{off:05x}  {hexs}  {ascii_}  u32={u}")
