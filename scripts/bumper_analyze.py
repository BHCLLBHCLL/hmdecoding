import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/bumper.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
print("payload:", len(p))
# [1][136] variants: try different offsets relative to a double
for i in range(0, len(p) - 24, 4):
    if u32(i) == 1 and u32(i+4) == 136:
        print(f"[1][136] @0x{i:x} next={u32(i+8)} next2={u32(i+12)}")
# scan for any [136] preceded by 1 within 16 bytes
n = 0
for i in range(0, len(p) - 16, 4):
    if u32(i) == 136:
        for j in range(1, 5):
            if u32(i - j*4) == 1:
                n += 1
print("1..136 pairs:", n)
# 6408-style count? bumper has 473 nodes: search u32 473
hits = [i for i in range(0, len(p)-4, 4) if u32(i) == 473]
print("u32 473:", [hex(h) for h in hits[:10]])
# look at head structure of bumper vs 1d_elements
print("head u32s:", [hex(u32(i)) for i in range(0, 0x60, 4)])
