import sys, gzip, struct, json
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
pos = json.load(open("output/ground_truth/ws_pt_positions.json"))
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
# 验证每个位置
bad = []
for pid_str, off in pos.items():
    pid = int(pid_str)
    x, y, z = pts[pid]
    xs, ys, zs = d64(off), d64(off + 8), d64(off + 16)
    err = max(abs(xs - x), abs(ys - y), abs(zs - z))
    if err > 1e-3:
        bad.append((pid, hex(off), (x, y, z), (round(xs,4), round(ys,4), round(zs,4)), err))
out.append(f"位置验证: {len(pos) - len(bad)}/{len(pos)} 误差<1e-3, {len(bad)} 个坏位置")
for b in bad[:10]:
    out.append(f"  bad: {b}")
# 11529 检查
out.append(f"11529 @0x{pos['11529']:x}: stored=({d64(pos['11529']):.6f},{d64(pos['11529']+8):.6f},{d64(pos['11529']+16):.6f})")
open("output/ground_truth/ws_pos_verify.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
