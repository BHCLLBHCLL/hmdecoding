import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]

HDR = 0xE90
print("header:", [hex(u32(HDR + i)) for i in range(0, 20, 4)], "d64@0:", d(HDR))
BASE = HDR + 20   # 0xEA4
print("base:", hex(BASE))
# dump first 3 and last 3 records
for k in (0, 1, 2, 440, 441, 442):
    rec = BASE + k * 52
    fields = []
    for i in range(0, 52, 4):
        v = u32(rec + i)
        fields.append(v)
    coords = (d(rec), d(rec + 8), d(rec + 16)) if rec + 24 <= len(p) else None
    print(f"row {k+1} @0x{rec:x}: coords={coords} fields={fields}")
# verify against known nodes: find which rows hold our known coords
NODES = {}
for line in open("output/ground_truth/node_many.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 4:
        nid = int(parts[0])
        x, y, z = (float(parts[1]), float(parts[2]), float(parts[3]))
        if abs(x) < 1e-9: x = 0.0
        NODES[nid] = (x, y, z)
for nid, (x, y, z) in list(NODES.items())[:6]:
    found = []
    for k in range(443):
        rec = BASE + k * 52
        c = (d(rec), d(rec + 8), d(rec + 16))
        if abs(c[0]-x) < 1e-9 and abs(c[1]-y) < 1e-9 and abs(c[2]-z) < 1e-9:
            found.append(k + 1)
    print(f"node {nid} ({x},{y},{z}) in rows: {found[:6]}")
