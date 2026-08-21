import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
print("payload:", len(p))
NODES = {2: (0.0, 0.0, -0.3), 4: (0.0, 0.0, -0.85), 6: (0.16, 0.0, -1.03), 7: (0.42, 0.0, -1.0)}
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]
for nid, (x, y, z) in NODES.items():
    pat = struct.pack("<ddd", x, y, z)
    offs = [m.start() for m in re.finditer(re.escape(pat), p)]
    print(f"node {nid} ({x},{y},{z}): {[hex(o) for o in offs]}")
# check 72-byte stride hypothesis from the first found triple
pat1 = struct.pack("<ddd", 0.0, 0.0, -0.3)
base = [m.start() for m in re.finditer(re.escape(pat1), p)]
print("node2 candidates:", [hex(b) for b in base])
for b in base[:3]:
    print(f"  @0x{b:x}: +0x34={u32(b+0x34)} +0x38={u32(b+0x38)} +0x30={u32(b+0x30)} +0x28={u32(b+0x28)}")
    # check stride 72 for other nodes
    for nid, (x, y, z) in NODES.items():
        r2 = b + (nid - 2) * 72
        if r2 + 24 <= len(p):
            print(f"    +{(nid-2)*72}: ({d(r2):g},{d(r2+8):g},{d(r2+16):g}) +0x34={u32(r2+0x34)}")
    print()
