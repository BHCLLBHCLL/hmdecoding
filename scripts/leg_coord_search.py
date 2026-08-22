import gzip, struct, re
raw = open("C:/Program Files/Altair/2019/tutorials/hm/interfaces/madymo/leg_geom.hm", "rb").read()
p = gzip.decompress(raw[12:])
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 搜索各坐标值的 d64 出现
for v in (-0.3, -0.85, -1.03, -1.0, 0.16, 0.42, 0.0):
    pat = struct.pack("<d", v)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    out.append(f"d64 {v}: {[hex(h) for h in hits[:10]]}")
# 线 id 1,2,4 在 0x400+ 区域
for v in (1, 2, 4):
    pat = struct.pack("<I", v)
    hits = [m.start() for m in re.finditer(re.escape(pat), p) if m.start() >= 0x400]
    out.append(f"u32 {v} @>=0x400: {[hex(h) for h in hits[:12]]}")
open("output/ground_truth/leg_coord_search.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
