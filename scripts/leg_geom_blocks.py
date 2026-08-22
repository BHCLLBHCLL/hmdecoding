import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 从 0x484 起 52 字节步进，检查各块
for base in range(0x484, 0x800, 52):
    vals = []
    for i in range(0, 52, 4):
        vals.append(u32(base + i))
    d = [d64(base + i) for i in range(0, 52, 8)]
    out.append(f"block @0x{base:x}: u32s={vals[:13]}")
    out.append(f"              d64s={[round(v, 3) for v in d]}")
open("output/ground_truth/leg_geom_blocks.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
