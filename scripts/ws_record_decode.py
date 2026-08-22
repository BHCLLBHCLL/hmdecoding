import gzip, struct
raw = open("WS_3.2_3d_tetra_finish.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d64(off): return struct.unpack_from("<d", p, off)[0]
def f32(off): return struct.unpack_from("<f", p, off)[0]

GT = {67604: (1843.9648684694, -228.95189910969, -916.0),
      68519: (1547.9624571325, -126.41658730473, -879.99997278378),
      70307: (1784.4999999293, 114.79718740675, -802.82643947833),
      70468: (1603.200754327, -209.1154221864, -916.0),
      70576: (1628.4970136607, -158.71059822793, -916.0)}
# ids found at: 68519@0x93119, 67604@0x93151, 70576@0x93185?, check by search
import re
pos = {}
for nid in GT:
    offs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", nid)), p)]
    pos[nid] = offs
print("id positions:", {k: [hex(o) for o in v[:2]] for k, v in pos.items()})
# decode records at stride 52 from the first id position minus 4
for nid in (68519, 67604):
    o = pos[nid][0]
    for start in (o - 4, o, o + 4):
        fields = []
        for i in range(0, 52, 4):
            fields.append(u32(start + i))
        coords = {}
        for off in (0x10, 0x14, 0x18, 0x1c, 0x20, 0x24, 0x28):
            if start + off + 8 <= len(p):
                coords[off] = d64(start + off)
        print(f"node {nid} start=0x{start:x}: id={fields[1] if fields else '?'} fields[:4]={fields[:4]}")
        print(f"   d64 offsets: { {hex(k): round(v, 3) for k, v in coords.items()} }")
