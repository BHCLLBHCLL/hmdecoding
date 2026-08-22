import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def f32(o): return struct.unpack_from("<f", p, o)[0]
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 在 0x1500-0x1B00 区统计 f32 坐标出现
region = p[0x1500:0x1B00]
vals = [5.0, -5.0, 0.0, -0.5, 2.5, 1.0, -1.0]
for v in vals:
    pat = struct.pack("<f", v)
    hits = [0x1500 + m.start() for m in re.finditer(re.escape(pat), region)]
    out.append(f"f32 {v}: {len(hits)} hits")
# 显示点记录模式: [u32 idx][坐标...] — dump 0x1520-0x1600 的 u32 索引位置
out.append("=== 0x1500-0x1700 中的小 u32 索引 ===")
for off in range(0x1500, 0x1700, 4):
    v = u32(off)
    if 1 <= v <= 70:
        out.append(f"0x{off:04x}: u32 {v}")
open("output/ground_truth/display_mesh.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
