import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm", "rb").read()
p = gzip.decompress(raw[12:])
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
pts = {1: (5.0, -5.0, 0.0), 2: (5.0, 5.0, 0.0), 3: (-5.0, 5.0, 0.0), 4: (-5.0, -5.0, 0.0)}
for pid, (x, y, z) in pts.items():
    pat = struct.pack("<ddd", x, y, z)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"point {pid} ({x},{y},{z}): {[hex(h) for h in hits[:8]]}")
# 线 id 18-21 与点 id 1-4 附近: 搜 u32 序列 [18][1][2] 或 [1][2] 等
for seq in ([18, 1, 2], [19, 2, 3], [20, 3, 4], [21, 4, 1], [36, 1, 2]):
    pat = b"".join(struct.pack("<I", v) for v in seq)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"u32 {seq}: {[hex(h) for h in hits[:5]]}")
# 点 id 与线 id 在几何区(0x100-0xE90)的 u32 出现
for v in (18, 36):
    hits = [m.start() for m in re.finditer(re.escape(struct.pack("<I", v)), p) if 0x100 <= m.start() < 0xE90]
    out.append(f"u32 {v} 几何区: {[hex(h) for h in hits[:10]]}")
open("output/ground_truth/1d_point_locs.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
