import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
for v in (7, 6):
    offs = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p)]
    print(f"u32 {v}: {[hex(o) for o in offs[:10]]}")
# 线记录假设: [id u32][...][n1][n2]? 搜索 1,2,4 附近的 u32 对
# 在 0x480..0x750 区域内找 (u32 线id) 模式
for off in range(0x480, 0x760, 4):
    v = u32(off)
    if v in (1, 2, 4) and 0 < v <= 4:
        ctx = [u32(off + i) for i in range(0, 48, 4)]
        print(f"@0x{off:x} v={v}: {ctx}")
