import gzip, struct
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def f32(o): return struct.unpack_from("<f", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 0x400-0x4a0: 4 字节对齐的 f32 流
out.append("=== f32 @0x400-0x4a0 (4对齐) ===")
for off in range(0x400, 0x4a0, 4):
    v = f32(off)
    if abs(v) < 100 and v != 0:
        out.append(f"0x{off:04x}  f32={v:.5f}")
# 0x430-0x480 按 1 字节滑动找合理 f32 流
out.append("=== f32 滑动扫描 0x430-0x480 (|v|<20) ===")
for off in range(0x430, 0x480):
    v = f32(off)
    if abs(v) < 20 and abs(v) > 1e-4:
        out.append(f"0x{off:04x}  f32={v:.5f}")
open("output/ground_truth/geom_f32.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
