import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 搜索 z=0 的 52B 显示记录（几何层 z=0 平面）
geom_disp = []
i = 0
while i < len(p) - 52:
    x, y, z = d64(i), d64(i + 8), d64(i + 16)
    rid = u32(i + 40)
    if abs(x) < 100 and abs(y) < 100 and z == 0.0 and 0 < rid < 2000 and (abs(x) > 0.01 or abs(y) > 0.01):
        geom_disp.append((i, rid, round(x, 2), round(y, 2)))
        i += 52
    else:
        i += 4
out.append(f"z=0 显示记录: {len(geom_disp)}")
# 找矩形角点 (5,-5,0),(5,5,0),(-5,5,0),(-5,-5,0) 附近的记录
for target in ((5.0, -5.0), (5.0, 5.0), (-5.0, 5.0), (-5.0, -5.0)):
    hits = [(o, r, x, y) for (o, r, x, y) in geom_disp if abs(x - target[0]) < 0.01 and abs(y - target[1]) < 0.01]
    out.append(f"角点 {target}: {hits[:4]}")
open("output/ground_truth/geom_display.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
