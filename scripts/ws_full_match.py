import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
# 全扫描: 8 对齐 + 4 对齐 + 未对齐(1字节滑动) 的 d64 三元组容差匹配
matched = {}
for tol in (2e-4, 5e-4, 2e-3):
    m = {}
    for i in range(0, len(p) - 24, 4):  # 4 字节步进(含8对齐)
        x2, y2, z2 = d64(i), d64(i + 8), d64(i + 16)
        for pid, (x, y, z) in pts.items():
            if pid in m:
                continue
            if abs(x2 - x) < tol and abs(y2 - y) < tol and abs(z2 - z) < tol:
                m[pid] = i
                break
    out.append(f"tol={tol}: {len(m)}/{len(pts)}")
    if tol == 5e-4:
        matched = m
# 未匹配分析
un = [pid for pid in pts if pid not in matched]
out.append(f"tol=5e-4 未匹配: {un[:15]} 共{len(un)}")
open("output/ground_truth/ws_full_match.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
