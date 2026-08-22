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
# 量化到 6 位小数后精确搜索
def q6(v): return round(v, 6)
matched = {}
for pid, (x, y, z) in pts.items():
    xq, yq, zq = q6(x), q6(y), q6(z)
    pat = struct.pack("<ddd", xq, yq, zq)
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    if hits:
        matched[pid] = hits[0]
out.append(f"量化(6位)精确匹配: {len(matched)}/{len(pts)}")
# 5 位小数
matched5 = {}
for pid, (x, y, z) in pts.items():
    pat = struct.pack("<ddd", round(x, 5), round(y, 5), round(z, 5))
    hits = [m.start() for m in re.finditer(re.escape(pat), p)]
    if hits:
        matched5[pid] = hits[0]
out.append(f"量化(5位)精确匹配: {len(matched5)}/{len(pts)}")
# 示例
for pid in list(matched)[:3]:
    h = matched[pid]
    out.append(f"  点{pid} @0x{h:x}: 存储=({d64(h):.8f},{d64(h+8):.8f},{d64(h+16):.8f}) oracle={pts[pid]}")
unmatched = [pid for pid in pts if pid not in matched]
out.append(f"未匹配(6位): {unmatched[:8]} 共{len(unmatched)}")
open("output/ground_truth/ws_quant_match.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
