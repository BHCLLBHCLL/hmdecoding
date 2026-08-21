import gzip, struct, re

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

p = load("v1913_03_t1")
def u32(off): return struct.unpack_from("<I", p, off)[0]
# search for 0x70241FF5 constant
c = struct.pack("<I", 0x70241FF5)
offs = [m.start() for m in re.finditer(re.escape(c), p)]
print("0x70241FF5 hits:", [hex(o) for o in offs])
for o in offs[:6]:
    print(f"  @0x{o:x} pre={p[o-32:o].hex()}")
    print(f"          post={p[o+4:o+36].hex()}")
    # decode context
    base = o - 24
    vals = [u32(base + i*4) for i in range(14)]
    print(f"          u32s: {vals}")
