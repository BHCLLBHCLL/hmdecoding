import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
def f32v(v): return struct.unpack("<f", struct.pack("<f", v))[0]
out = []
# 存储值 @0xfdf（点11573 候选）
for h in (0xfdf, 0x4c93, 0x1b3):
    x, y, z = d64(h), d64(h + 8), d64(h + 16)
    out.append(f"存储@0x{h:x}: ({x:.14f}, {y:.14f}, {z:.14f})")
# f32 化比较
vals = [(-76.413612365723, "oracle11573-y"), (-78.439056396484, "oracle12726-y"), (-835.0, "z-835"), (-900.0, "z-900")]
for v, label in vals:
    out.append(f"{label}: oracle={v:.14f} f32={f32v(v):.14f} diff={abs(v-f32v(v)):.2e}")
# 存储 y 值集合（从匹配的 51 个点位置）
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
out.append("--- 51 个匹配点: oracle y vs 存储 y ---")
TOL = 2e-4
z_vals = sorted(set(z for _, _, z in pts.values()))
pos_by_z = {z: [] for z in z_vals}
for i in range(0, len(p) - 24, 8):
    zv = d64(i + 16)
    for z in z_vals:
        if abs(zv - z) < TOL:
            pos_by_z[z].append(i)
matched = {}
for z, positions in pos_by_z.items():
    for pid, x, y in [(pid, x, y) for pid, (x, y, zz) in pts.items() if zz == z]:
        for i in positions:
            x2, y2 = d64(i), d64(i + 8)
            if abs(x2 - x) < TOL and abs(y2 - y) < TOL:
                matched[pid] = i
                break
cnt = 0
for pid, i in matched.items():
    x, y, z = pts[pid]
    ys = d64(i + 8)
    out.append(f"  点{pid}: oracle_y={y:.10f} 存储_y={ys:.10f} diff={abs(y-ys):.2e} f32diff={abs(f32v(y)-ys):.2e}")
    cnt += 1
    if cnt > 8:
        break
open("output/ground_truth/ws_f32_compare.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
