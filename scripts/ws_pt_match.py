import sys, gzip, struct, re
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def d64(o): return struct.unpack_from("<d", p, o)[0]
out = []
# 解析 oracle 点
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
out.append(f"oracle 点: {len(pts)}")
# 对每个点: 找 x 的 d64 位置 → 检查 y/z 容差
TOL = 2e-4
matched = {}
for pid, (x, y, z) in pts.items():
    pat = struct.pack("<d", x)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    best = None
    for h in hits:
        if h + 24 > len(p):
            continue
        y2, z2 = d64(h + 8), d64(h + 16)
        if abs(y2 - y) < TOL and abs(z2 - z) < TOL:
            best = h
            break
    if best is not None:
        matched[pid] = best
out.append(f"匹配到三元组: {len(matched)}/{len(pts)}")
# 未匹配的
unmatched = [pid for pid in pts if pid not in matched]
out.append(f"未匹配: {unmatched[:10]} (共{len(unmatched)})")
# 匹配示例
for pid in list(matched)[:5]:
    h = matched[pid]
    out.append(f"  点{pid}: @0x{h:x} 存储=({round(d64(h),6)},{round(d64(h+8),6)},{round(d64(h+16),6)}) oracle={pts[pid]}")
open("output/ground_truth/ws_pt_match.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
