import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def f(off): return struct.unpack_from("<f", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]

for off in range(0x780, 0x920, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    u = u32(off)
    print(f"0x{off:04x}  {hexs}  u32={u} f={f(off):.4g}")
# also look around 0x6800-0x68d0 (before element section)
print()
for off in range(0x6800, 0x68d8, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    print(f"0x{off:04x}  {hexs}")
