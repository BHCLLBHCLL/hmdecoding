import sys, gzip, struct, re
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
# 按 z 分组 oracle 点
by_z = {}
for pid, (x, y, z) in pts.items():
    by_z.setdefault(z, []).append((pid, x, y))
out.append(f"唯一 z 值: {len(by_z)}")
TOL = 2e-4
matched = {}
# 对每个 z: 找 z 的 d64 位置（z 是精确值? 或量化?）— 用容差滑动找
# 高效: 扫描所有 8 对齐位置，检查 d64 是否 ≈ 某个 oracle 点的 z
z_vals = sorted(by_z)
pos_by_z = {z: [] for z in z_vals}
for i in range(0, len(p) - 24, 8):
    zv = d64(i + 16)
    for z in z_vals:
        if abs(zv - z) < TOL:
            pos_by_z[z].append(i)
out.append(f"z 位置数: {[(z, len(v)) for z, v in pos_by_z.items()]}")
# 对每个 z 位置检查 x/y
for z, positions in pos_by_z.items():
    for pid, x, y in by_z[z]:
        for i in positions:
            x2, y2 = d64(i), d64(i + 8)
            if abs(x2 - x) < TOL and abs(y2 - y) < TOL:
                matched[pid] = i
                break
out.append(f"最终匹配: {len(matched)}/{len(pts)}")
unmatched = [pid for pid in pts if pid not in matched]
out.append(f"未匹配: {unmatched[:10]} 共{len(unmatched)}")
open("output/ground_truth/ws_pt_final.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
