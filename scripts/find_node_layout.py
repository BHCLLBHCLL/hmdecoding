import gzip, struct, re

def load(name):
    raw = open(f"corpus/synthetic/{name}.hm", "rb").read()
    return gzip.decompress(raw[12:])

p = load("v1913_04_t2")
NODES = {1: (1.0, 2.0, 3.0), 2: (10.0, 0.0, 0.0), 3: (0.0, 10.0, 0.0), 4: (0.0, 0.0, 10.0), 5: (5.0, 5.0, 5.0)}

for nid, (x, y, z) in NODES.items():
    pat = struct.pack("<ddd", x, y, z)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"node {nid} triple({x},{y},{z}): {[hex(o) for o in offs]}")
    for o in offs[:3]:
        print(f"   ctx @0x{o:x}: pre={p[o-16:o].hex()}  post={p[o+24:o+64].hex()}")
