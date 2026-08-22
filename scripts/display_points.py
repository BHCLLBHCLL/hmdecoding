import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
marks = [i for i in range(len(p) - 8) if u32(i) == 0x40008126]
points = {}
for m in marks:
    off = u32(m + 4)
    base = off
    k = 0
    while base + 52 <= len(p) and k < 5000:
        rec = base + k * 52
        x, y, z = d64(rec), d64(rec + 8), d64(rec + 16)
        rid = u32(rec + 40)
        if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
            break
        if rid == 0 and x == 0 and y == 0 and z == 0 and k > 0:
            break
        if rid != 0:
            points[rid] = (round(x, 4), round(y, 4), round(z, 4))
        k += 1
    out.append(f"mark@0x{m:x} off=0x{off:x}: {k} 条候选")
out.append(f"总显示点数: {len(points)}")
ids = sorted(points)
out.append(f"id 范围: {ids[0]}..{ids[-1]}")
out.append(f"示例: {[(i, points[i]) for i in ids[:5]]}")
out.append(f"示例尾: {[(i, points[i]) for i in ids[-5:]]}")
open("output/ground_truth/display_points.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
