import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]

for off in range(0x2d0, 0x3d0, 4):
    v = u32(off)
    dv = d(off)
    print(f"0x{off:04x}  u32={v:>12}  d={dv:.6g}")
