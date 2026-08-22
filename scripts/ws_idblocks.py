import sys, gzip, struct, json
sys.path.insert(0, ".")
import hmdecoder.decoder as D
p = D.load_payload("WS_3.2_3d_tetra_finish.hm")
def u32(o): return struct.unpack_from("<I", p, o)[0]
out = []
# 已知点 id
pts = {}
for line in open("output/ground_truth/ws_allpoints.log", encoding="utf-8").read().splitlines():
    parts = line.split()
    if len(parts) == 5:
        pts[int(parts[1])] = (float(parts[2]), float(parts[3]), float(parts[4]))
# 宽松扫描: [id][1] 模式（id 在已知点集合）
found = {}
for i in range(0, len(p) - 8):
    v = u32(i)
    if v in pts and u32(i + 4) == 1:
        found.setdefault(v, []).append(i)
out.append(f"已知点 id 出现 [id][1] 模式: {len(found)}/{len(pts)}")
multi = {k: v for k, v in found.items() if len(v) > 1}
out.append(f"多位置: {len(multi)}")
for k, v in list(multi.items())[:5]:
    out.append(f"  id {k}: {[hex(x) for x in v[:4]]}")
# 单位置的分布
single = {k: v[0] for k, v in found.items() if len(v) == 1}
out.append(f"单位置: {len(single)}")
if single:
    import collections
    regs = collections.Counter(hex(o >> 12) for o in single.values())
    out.append(f"单位置区域(4K): {sorted(regs.items(), key=lambda x: -x[1])[:10]}")
open("output/ground_truth/ws_idblocks.txt", "w", encoding="utf-8").write("\n".join(out))
print("done")
