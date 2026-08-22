import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
marks = [i for i in range(len(p) - 8) if u32(i) == 0x40008126]
out.append(f"WS MARK_GEOM 数量: {len(marks)}")
# 前 6 个 mark 的偏移与候选
for m in marks[:6]:
    off = u32(m + 4)
    # 检查 off 处及滑动起点的记录验证
    best = None
    for start in range(off, min(off + 0x40, len(p) - 52)):
        ok = True
        for k in range(10):
            rec = start + k * 52
            if rec + 52 > len(p):
                ok = False; break
            x, y, z = d64(rec), d64(rec + 8), d64(rec + 16)
            if not (abs(x) < 1e6 and abs(y) < 1e6 and abs(z) < 1e6):
                ok = False; break
        if ok:
            score = sum(1 for k in range(10) if 0 < u32(start + k * 52 + 40) < 1e6)
            if best is None or score > best[0]:
                best = (score, start)
    out.append(f"  mark@0x{m:x} off=0x{off:x} best={best}")
open("output/ground_truth/ws_display_dbg.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
