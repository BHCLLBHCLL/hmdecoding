import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("C:/Program Files/Altair/2019/tutorials/hm/1d_elements.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
marks = [(i, u32(i + 4)) for i in range(len(p) - 8) if u32(i) == 0x40008126]
for m, off in marks:
    # 滑动找流起点
    best = None
    for start in range(off, min(off + 0x40, len(p) - 52)):
        ok = True
        for k in range(8):
            rec = start + k * 52
            if rec + 52 > len(p):
                ok = False; break
            x, y, z = d64(rec), d64(rec + 8), d64(rec + 16)
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                ok = False; break
        if ok:
            score = sum(1 for k in range(8) if 0 < u32(start + k * 52 + 40) < 1e6)
            if best is None or score > best[0]:
                best = (score, start)
    if not best:
        continue
    base = best[1]
    pts = []
    k = 0
    while base + 52 <= len(p) and k < 300:
        rec = base + k * 52
        x, y, z = d64(rec), d64(rec + 8), d64(rec + 16)
        rid = u32(rec + 40)
        if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
            break
        if 0 < rid < 1e6:
            pts.append((rid, round(x, 2), round(y, 2), round(z, 2)))
        k += 1
    # 打印轨迹（压缩: 只显示坐标变化点）
    out.append(f"块 mark@0x{m:x} 偏移0x{off:x} -> 流@0x{base:x}: {len(pts)} 点")
    prev = None
    for pt in pts:
        if prev is None or pt[1:] != prev[1:]:
            out.append(f"    id={pt[0]}: ({pt[1]}, {pt[2]}, {pt[3]})")
            prev = pt
open("output/ground_truth/line_trajectories.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
