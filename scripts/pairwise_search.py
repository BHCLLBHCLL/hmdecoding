import gzip, struct, re

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]

# GT pairs from elem 1-5
GT = {1: (146,151,133,134), 2: (151,108,109,133), 3: (147,150,151,146), 4: (150,107,108,151), 5: (148,152,150,147)}
# for each GT quad, find where its 4 values appear with ANY spacing within 32 bytes
for eid, quad in GT.items():
    locs = {}
    for v in quad:
        offs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
        locs[v] = offs
    print(f"elem {eid} {quad}:")
    for v, offs in locs.items():
        print(f"   node {v}: {[hex(o) for o in offs[:8]]}")
# dump a candidate window: elem2 nodes 151,108,109,133 — look near 0x7084 (u32 151)
for o in [0x7084]:
    print(f"context @0x{o:x}:")
    for off in range(o - 32, o + 64, 4):
        print(f"   0x{off:04x}: {u32(off)}")
