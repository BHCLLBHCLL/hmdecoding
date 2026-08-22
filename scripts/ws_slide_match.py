import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
TOL = 1e-3
# 1 字节滑动: 找 z 匹配的位置 → 检查 x/y
z_set = sorted(set(z for _, _, z in pts.values()))
by_z = {}
for pid, (x, y, z) in pts.items():
    by_z.setdefault(z, []).append((pid, x, y))
matched = {}
import time
t0 = time.time()
for i in range(len(p) - 24):
    zv = d64(i + 16)
    for z in z_set:
        if abs(zv - z) < TOL:
            for pid, x, y in by_z[z]:
                if pid in matched:
                    continue
                if abs(d64(i) - x) < TOL and abs(d64(i + 8) - y) < TOL:
                    matched[pid] = i
    if i % 500000 == 0:
        print(f"  progress {i} matched={len(matched)}", flush=True)
print(f"matched: {len(matched)}/{len(pts)} time={time.time()-t0:.0f}s", flush=True)
un = [pid for pid in pts if pid not in matched]
print(f"unmatched: {un[:15]} ({len(un)})", flush=True)
import json
json.dump({str(k): v for k, v in matched.items()}, open("output/ground_truth/ws_pt_positions.json", "w"))
print("saved", flush=True)
