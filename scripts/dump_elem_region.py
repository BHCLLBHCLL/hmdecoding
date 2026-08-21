import gzip, struct

raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(off): return struct.unpack_from("<I", p, off)[0]
def d(off): return struct.unpack_from("<d", p, off)[0]

# dump the element region 0x7400..0x7700 decoded
for off in range(0x7400, 0x7700, 4):
    print(f"0x{off:04x}  u32={u32(off):>10}  d={d(off):.6g}")
