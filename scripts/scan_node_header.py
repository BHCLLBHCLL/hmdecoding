import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]
def f(off): return struct.unpack_from("<f", p, off)[0]

# find region where node section might start: scan for a header with 442 nearby
for off in range(0, 0x8000, 4):
    v = u32(off)
    if v in (442, 443, 444):
        print(f"u32 {v} at 0x{off:x}: pre={p[off-16:off].hex()}")
# dump 0x0e00..0x0f00
print()
for off in range(0x0e00, 0x0f00, 16):
    chunk = p[off:off+16]
    hexs = " ".join(f"{b:02x}" for b in chunk)
    ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"0x{off:04x}  {hexs}  {ascii_}")
