import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
marks = [i for i in range(len(p) - 8) if u32(i) == 0x40008126]
all_points = {}
for m in marks:
    off = u32(m + 4)
    best = None
    for start in range(off, off + 0x40):
        # 验证 52 步进记录流
        pts = []
        ok = True
        base = start
        for k in range(10):
            rec = base + k * 52
            if rec + 52 > len(p):
                ok = False; break
            x, y, z = d64(rec), d64(rec + 8), d64(rec + 16)
            rid = u32(rec + 40)
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                ok = False; break
            pts.append((rid, x, y, z))
        if ok and pts:
            score = sum(1 for (rid, x, y, z) in pts if 0 < rid < 1e6 and (abs(x) > 1e-9 or abs(y) > 1e-9 or abs(z) > 1e-9))
            if best is None or score > best[0]:
                best = (score, start, pts)
    if best:
        out.append(f"mark@0x{m:x} off=0x{off:x}: 流起点 0x{best[1]:x} (score={best[0]})")
        # 完整解码
        base = best[1]
        k = 0
        while base + 52 <= len(p) and k < 5000:
            rec = base + k * 52
            x, y, z = d64(rec), d64(rec + 8), d64(rec + 16)
            rid = u32(rec + 40)
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                break
            if 0 < rid < 1e6:
                all_points[rid] = (round(x, 4), round(y, 4), round(z, 4))
            k += 1
        out.append(f"  该区 {k} 条记录")
out.append(f"总显示点数: {len(all_points)}")
ids = sorted(all_points)
if ids:
    out.append(f"id 范围: {ids[0]}..{ids[-1]}")
    out.append(f"示例: {[(i, all_points[i]) for i in ids[:8]]}")
    out.append(f"示例尾: {[(i, all_points[i]) for i in ids[-5:]]}")
open("output/ground_truth/display_points2.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
