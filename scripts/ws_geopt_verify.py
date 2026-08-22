import sys, gzip, struct
sys.path.insert(0, ".")
import hmdecoder.decoder as D
m = D.decode("WS_3.2_3d_tetra_finish.hm")
out = []
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
ok = 0
false = []
for pid, gp in m.geo_points.items():
    if pid in pts:
        x, y, z = pts[pid]
        if max(abs(gp.x - x), abs(gp.y - y), abs(gp.z - z)) < 2e-3:
            ok += 1
        else:
            false.append(pid)
    else:
        false.append(pid)
out.append(f"真点正确: {ok}/157")
out.append(f"误报/错: {len(false)}")
out.append(f"误报示例: {false[:10]}")
open("output/ground_truth/ws_geopt_verify.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
